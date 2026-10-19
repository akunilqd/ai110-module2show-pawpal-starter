"""Simple tests for task completion and adding tasks to a pet."""

from pawpal_system import Pet, Task


def test_task_completion():
    task = Task("Feeding", duration_minutes=10)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    pet = Pet("Mochi", age_months=12, species="cat")
    task = Task("Brushing", duration_minutes=15)
    initial_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
    assert task in pet.tasks
