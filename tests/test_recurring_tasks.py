"""Verify recurring task dates, ownership, completion, and planning."""

from datetime import date, datetime, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def setup_task(frequency="daily", due_date=date(2026, 1, 31)):
    owner = Owner("Khoa", 40)
    dog, cat = Pet("Niki", 12), Pet("Skibidi", 6)
    owner.add_pet(dog)
    owner.add_pet(cat)
    task = Task("Feeding", 10, frequency, "high", time="08:00", due_date=due_date)
    cat.add_task(task)
    return Scheduler(owner), dog, cat, task


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7), (" Weekly ", 7)])
def test_recurring_completion_creates_independent_task_for_same_pet(frequency, days):
    scheduler, dog, cat, task = setup_task(frequency)
    next_task = scheduler.mark_task_complete(task.task_id, completed_on=task.due_date)
    assert task.completed is True
    assert next_task is not task
    assert next_task.task_id != task.task_id
    assert next_task.completed is False
    assert next_task.due_date == task.due_date + timedelta(days=days)
    assert (next_task.description, next_task.duration_minutes, next_task.priority,
            next_task.time, next_task.frequency) == (
        task.description, 10, "high", "08:00", frequency.strip().casefold()
    )
    assert cat.tasks == [task, next_task]
    assert dog.tasks == []


def test_completing_an_already_completed_task_does_not_create_another_task():
    scheduler, _, cat, task = setup_task()
    next_task = scheduler.mark_task_complete(task.task_id, task.due_date)
    assert scheduler.mark_task_complete(task.task_id, task.due_date) is None
    assert scheduler.mark_task_complete(task.task_id, task.due_date) is None
    assert cat.tasks == [task, next_task]


def test_task_mark_complete_only_changes_status():
    scheduler, _, cat, task = setup_task()
    assert task.mark_complete() is None
    assert task.completed is True
    assert not hasattr(task, "next_occurrence")
    assert scheduler.mark_task_complete(task.task_id, task.due_date) is None
    assert cat.tasks == [task]


@pytest.mark.parametrize("frequency", ["once", "monthly", "twice daily"])
def test_other_frequencies_complete_without_followup(frequency):
    scheduler, _, cat, task = setup_task(frequency)
    assert scheduler.mark_task_complete(task.task_id, task.due_date) is None
    assert task.completed is True
    assert cat.tasks == [task]


@pytest.mark.parametrize("completion_day,expected", [
    (date(2026, 1, 30), date(2026, 1, 31)),
    (date(2026, 2, 4), date(2026, 2, 5)),
])
def test_early_and_late_completion_use_completion_date(completion_day, expected):
    scheduler, _, _, task = setup_task()
    assert scheduler.mark_task_complete(task.task_id, completion_day).due_date == expected


def test_future_occurrence_waits_until_due_and_overdue_tasks_are_included():
    scheduler, _, _, task = setup_task()
    original_day = task.due_date
    next_task = scheduler.mark_task_complete(task.task_id, original_day)
    today_plan = scheduler.generate_plan(original_day)
    assert today_plan["scheduled_tasks"] == []
    assert today_plan["unscheduled_tasks"] == []
    assert scheduler.get_pending_tasks(original_day) == []
    for day in (next_task.due_date, next_task.due_date + timedelta(days=3)):
        assert scheduler.generate_plan(day)["scheduled_tasks"][0]["task"] is next_task


def test_followup_can_repeat_again_across_year_boundary():
    scheduler, _, cat, task = setup_task("weekly", date(2026, 12, 31))
    second = scheduler.mark_task_complete(task.task_id, task.due_date)
    third = scheduler.mark_task_complete(second.task_id, second.due_date)
    assert third.due_date == date(2027, 1, 14)
    assert cat.tasks == [task, second, third]


@pytest.mark.parametrize("invalid_date", ["2026-01-31", datetime(2026, 1, 31), 123])
def test_invalid_dates_do_not_complete_or_mutate_tasks(invalid_date):
    with pytest.raises(ValueError):
        Task("Feeding", 10, due_date=invalid_date)
    scheduler, _, cat, task = setup_task()
    with pytest.raises(ValueError):
        scheduler.mark_task_complete(task.task_id, invalid_date)
    assert task.completed is False
    assert cat.tasks == [task]
    with pytest.raises(ValueError):
        scheduler.filter_tasks(due_on=invalid_date)


def test_edit_preserves_due_date_and_can_change_it():
    _, _, cat, task = setup_task()
    cat.edit_task(task.task_id, description="Morning feeding")
    assert task.due_date == date(2026, 1, 31)
    cat.edit_task(task.task_id, due_date=date(2026, 2, 1))
    assert task.due_date == date(2026, 2, 1)
