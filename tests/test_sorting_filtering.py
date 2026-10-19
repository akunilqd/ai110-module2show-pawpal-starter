"""Verify chronological ordering and filters across multiple pets."""

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def scheduler():
    owner = Owner("Khoa", 60)
    dog = Pet("Niki", 2, "dog")
    cat = Pet("Skibidi", 4, "cat")
    dog.add_task(Task("Evening walk", 10, time="18:30"))
    dog.add_task(Task("Breakfast", 20, time="08:00", completed=True))
    cat.add_task(Task("Brushing", 5))
    cat.add_task(Task("Feeding", 10, time="07:30"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    return Scheduler(owner)


def test_sort_by_time_preserves_pet_links_and_original_order(scheduler):
    original = scheduler.owner.get_all_tasks()
    result = scheduler.sort_by_time()
    assert [(pet.name, task.time) for pet, task in result] == [
        ("Skibidi", "07:30"), ("Niki", "08:00"),
        ("Niki", "18:30"), ("Skibidi", None),
    ]
    assert scheduler.owner.get_all_tasks() == original
    assert scheduler.sort_by_time([]) == []


def test_equal_times_are_stable_and_day_boundaries_sort_correctly():
    owner = Owner("Khoa", 60)
    pet = Pet("Niki", 2)
    for description, time in (
        ("Last", "23:59"), ("First", "00:00"),
        ("Tie A", "12:00"), ("Tie B", "12:00"),
    ):
        pet.add_task(Task(description, 5, time=time))
    owner.add_pet(pet)
    assert [task.description for _, task in Scheduler(owner).sort_by_time()] == [
        "First", "Tie A", "Tie B", "Last",
    ]


def test_filters_work_separately_and_together(scheduler):
    assert len(scheduler.filter_tasks()) == 4
    assert len(scheduler.filter_tasks(completed=False)) == 3
    assert len(scheduler.filter_tasks(completed=True)) == 1
    assert len(scheduler.filter_tasks(pet_name="  NIKI  ")) == 2
    assert [task.description for _, task in scheduler.filter_tasks(
        completed=False, pet_name="niki"
    )] == ["Evening walk"]
    assert scheduler.filter_tasks(pet_name="Unknown") == []
    assert scheduler.filter_tasks(completed=True, pet_name="Skibidi") == []


def test_sort_filtered_tasks(scheduler):
    entries = scheduler.filter_tasks(completed=False)
    assert [task.time for _, task in scheduler.sort_by_time(entries)] == [
        "07:30", "18:30", None,
    ]


@pytest.mark.parametrize("time", ["8:00", "24:00", "12:60", "08:00 AM", "", 800])
def test_invalid_times_are_rejected(time):
    with pytest.raises(ValueError, match="HH:MM"):
        Task("Feeding", 10, time=time)


def test_time_edit_is_validated_without_resetting_status(scheduler):
    dog = scheduler.owner.pets[0]
    task = dog.tasks[1]
    dog.edit_task(task.task_id, time="09:30")
    assert task.time == "09:30"
    assert task.completed is True
    dog.edit_task(task.task_id, description="Later breakfast")
    assert task.time == "09:30"
    with pytest.raises(ValueError):
        dog.edit_task(task.task_id, description="Invalid edit", time="25:00")
    assert task.description == "Later breakfast"
    assert task.time == "09:30"


def test_empty_owner_has_no_matching_tasks():
    scheduler = Scheduler(Owner("Khoa", 0))
    assert scheduler.filter_tasks(completed=False) == []
    assert scheduler.sort_by_time() == []
