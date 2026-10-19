"""Check lightweight warnings for tasks sharing a date and start time."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.mark.parametrize("same_pet", [True, False])
def test_conflict_for_same_or_different_pets(same_pet):
    owner = Owner("Khoa", 40)
    dog, cat = Pet("Niki", 2), Pet("Skibidi", 4)
    owner.add_pet(dog)
    owner.add_pet(cat)
    day = date(2026, 10, 19)
    dog.add_task(Task("Walk", 20, time="17:30", due_date=day))
    other_pet = dog if same_pet else cat
    other_pet.add_task(Task("Feeding", 10, time="17:30", due_date=day))
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "2026-10-19 at 17:30" in warnings[0]
    assert "Niki: Walk" in warnings[0]
    assert f"{other_pet.name}: Feeding" in warnings[0]

    plan = scheduler.generate_plan(day)
    assert plan["warnings"] == warnings
    assert len(plan["scheduled_tasks"]) == 2
    assert plan["total_duration"] == 30
    assert all(not task.completed for _, task in owner.get_all_tasks())


def test_completed_untimed_and_different_dates_or_times_do_not_conflict():
    owner = Owner("Khoa", 60)
    pet = Pet("Niki", 2)
    owner.add_pet(pet)
    today = date.today()
    pet.add_task(Task("Walk", 10, time="08:00", due_date=today))
    pet.add_task(Task("Completed", 10, time="08:00", completed=True, due_date=today))
    pet.add_task(Task("Tomorrow", 10, time="08:00", due_date=today + timedelta(days=1)))
    pet.add_task(Task("Later", 10, time="08:15", due_date=today))
    pet.add_task(Task("Untimed A", 10))
    pet.add_task(Task("Untimed B", 10))
    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []
    assert scheduler.detect_conflicts([]) == []


def test_three_tasks_in_a_slot_produce_one_warning():
    owner = Owner("Khoa", 60)
    pet = Pet("Niki", 2)
    owner.add_pet(pet)
    for name in ("Walk", "Feeding", "Brushing"):
        pet.add_task(Task(name, 10, time="08:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert all(name in warnings[0] for name in ("Walk", "Feeding", "Brushing"))


def test_tasks_that_do_not_fit_are_not_plan_conflicts():
    owner = Owner("Khoa", 10)
    pet = Pet("Niki", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Feeding", 10, time="08:00", priority="high"))
    pet.add_task(Task("Walk", 20, time="08:00"))
    scheduler = Scheduler(owner)
    assert len(scheduler.detect_conflicts()) == 1
    plan = scheduler.generate_plan()
    assert plan["warnings"] == []
    assert len(plan["unscheduled_tasks"]) == 1


def test_empty_owner_has_no_conflicts():
    assert Scheduler(Owner("Khoa", 0)).detect_conflicts() == []
