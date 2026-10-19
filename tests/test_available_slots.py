"""Verify the advanced interval-search algorithm across pets."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_search_merges_overlapping_intervals_across_pets():
    owner = Owner("Khoa", 60)
    for name, time, duration in (
        ("Niki", "08:00", 30), ("Skibidi", "08:15", 45), ("Mochi", "09:00", 15)
    ):
        pet = Pet(name, 12)
        pet.add_task(Task("Care", duration, time=time))
        owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.find_next_available_slot(20) == "09:15"
    assert [task.time for _, task in owner.get_all_tasks()] == ["08:00", "08:15", "09:00"]


def test_gap_exact_fit_and_window_boundaries():
    owner = Owner("Khoa", 60)
    pet = Pet("Niki", 12)
    pet.add_task(Task("Care", 30, time="08:30"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.find_next_available_slot(30, latest="09:00") == "08:00"
    assert scheduler.find_next_available_slot(31, latest="09:00") is None
    assert scheduler.find_next_available_slot(10, earliest="08:45", latest="09:15") == "09:00"


def test_completed_untimed_other_dates_and_excluded_task_do_not_reserve_slots():
    owner = Owner("Khoa", 60)
    pet = Pet("Niki", 12)
    task = Task("Move me", 30, time="08:00")
    pet.add_task(task)
    pet.add_task(Task("Done", 60, time="08:00", completed=True))
    pet.add_task(Task("Untimed", 60))
    pet.add_task(Task("Tomorrow", 60, time="08:00", due_date=date.today() + timedelta(days=1)))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.find_next_available_slot(10) == "08:30"
    assert scheduler.find_next_available_slot(10, exclude_task_id=task.task_id) == "08:00"


@pytest.mark.parametrize("kwargs", [
    {"duration_minutes": 0}, {"duration_minutes": -1},
    {"duration_minutes": 10, "earliest": "8:00"},
    {"duration_minutes": 10, "latest": "24:00"},
    {"duration_minutes": 10, "earliest": "20:00", "latest": "08:00"},
    {"duration_minutes": 10, "date": "2026-10-19"},
])
def test_invalid_search_inputs_are_rejected(kwargs):
    with pytest.raises(ValueError):
        Scheduler(Owner("Khoa", 60)).find_next_available_slot(**kwargs)


def test_empty_calendar_and_end_of_day():
    scheduler = Scheduler(Owner("Khoa", 60))
    assert scheduler.find_next_available_slot(10) == "08:00"
    assert scheduler.find_next_available_slot(9, earliest="23:50", latest="23:59") == "23:50"
    assert scheduler.find_next_available_slot(10, earliest="23:50", latest="23:59") is None
