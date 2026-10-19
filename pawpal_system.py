"""PawPal+ backend with dated recurring tasks and daily time-budget planning."""

from __future__ import annotations

from datetime import date as Date, timedelta
import re
from uuid import uuid4


def _validate_minutes(value: int, minimum: int = 0) -> None:
    """Reject noninteger minute values or values below the minimum."""
    if type(value) is not int or value < minimum:
        raise ValueError(f"Minutes must be an integer of at least {minimum}.")


class Task:
    """A care activity with a duration, frequency, priority, and completion status."""

    PRIORITIES = {"high": 0, "medium": 1, "low": 2}

    def __init__(
        self,
        description: str,
        duration_minutes: int,
        frequency: str = "daily",
        priority: str = "medium",
        completed: bool = False,
        time: str | None = None,
        due_date: Date | None = None,
    ) -> None:
        """Initialize a validated care task with a unique ID."""
        if not description.strip():
            raise ValueError("Task description cannot be empty.")
        _validate_minutes(duration_minutes, minimum=1)
        if not frequency.strip():
            raise ValueError("Task frequency cannot be empty.")
        if priority not in self.PRIORITIES:
            raise ValueError("Priority must be high, medium, or low.")
        if type(completed) is not bool:
            raise ValueError("Completion status must be a boolean.")
        if time is not None and (
            not isinstance(time, str)
            or re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", time) is None
        ):
            raise ValueError("Time must use 24-hour HH:MM format, such as 08:30.")
        if due_date is not None and type(due_date) is not Date:
            raise ValueError("Due date must be a datetime.date object.")
        self.task_id = uuid4().hex
        self.description = description.strip()
        self.duration_minutes = duration_minutes
        self.frequency = frequency.strip().casefold()
        self.priority = priority
        self.completed = completed
        self.time = time
        self.due_date = due_date if due_date is not None else Date.today()

    def mark_complete(self) -> None:
        """Mark this task as completed; Scheduler handles recurring tasks."""
        self.completed = True

    def reset_completion(self) -> None:
        """Reset this task's status to unfinished."""
        self.completed = False


class Pet:
    """Pet details and the activities needed to care for this pet."""

    def __init__(self, name: str, age_months: int, species: str = "other") -> None:
        """Initialize pet details with empty care needs and task lists."""
        if not name.strip() or not species.strip():
            raise ValueError("Pet name and species cannot be empty.")
        if type(age_months) is not int or age_months < 0:
            raise ValueError("Age must be a nonnegative number of months.")
        self.name = name.strip()
        self.age_months = age_months
        self.species = species.strip()
        self.care_needs: list[str] = []
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task unless the same object is already assigned to this pet."""
        if not isinstance(task, Task):
            raise TypeError("Expected a Task object.")
        if task in self.tasks:
            raise ValueError("This task is already assigned to this pet.")
        self.tasks.append(task)

    def _find_task(self, task_id: str) -> Task:
        """Find a task by ID or raise ValueError if it does not belong to this pet."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        raise ValueError(f"Task {task_id!r} was not found for {self.name}.")

    def edit_task(
        self,
        task_id: str,
        *,
        description: str | None = None,
        duration_minutes: int | None = None,
        frequency: str | None = None,
        priority: str | None = None,
        time: str | None = None,
        due_date: Date | None = None,
    ) -> None:
        """Validate and update task details while preserving its ID and status."""
        task = self._find_task(task_id)
        # Validate all changes before modifying the existing task.
        updated = Task(
            task.description if description is None else description,
            task.duration_minutes if duration_minutes is None else duration_minutes,
            task.frequency if frequency is None else frequency,
            task.priority if priority is None else priority,
            task.completed,
            task.time if time is None else time,
            task.due_date if due_date is None else due_date,
        )
        task.description = updated.description
        task.duration_minutes = updated.duration_minutes
        task.frequency = updated.frequency
        task.priority = updated.priority
        task.time = updated.time
        task.due_date = updated.due_date

    def remove_task(self, task_id: str) -> None:
        """Remove this pet's task with the given ID."""
        self.tasks.remove(self._find_task(task_id))

    def update_care_needs(self, needs: list[str]) -> None:
        """Replace care needs with a copy of the supplied list."""
        self.care_needs = list(needs)


class Owner:
    """Manages multiple pets and exposes their tasks to the scheduler."""

    def __init__(self, name: str, available_minutes: int) -> None:
        """Initialize an owner with a daily time budget and no registered pets."""
        if not name.strip():
            raise ValueError("Owner name cannot be empty.")
        _validate_minutes(available_minutes)
        self.name = name.strip()
        self.available_minutes = available_minutes
        self.preferences: dict[str, bool] = {"prefer_short_tasks": False}
        self.pets: list[Pet] = []

    def update_available_time(self, minutes: int) -> None:
        """Set the owner's nonnegative daily time budget in minutes."""
        _validate_minutes(minutes)
        self.available_minutes = minutes

    def add_pet(self, pet: Pet) -> None:
        """Register a pet unless the same object is already registered."""
        if not isinstance(pet, Pet):
            raise TypeError("Expected a Pet object.")
        if pet in self.pets:
            raise ValueError("This pet is already registered.")
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a registered pet from this owner's list."""
        self.pets.remove(pet)

    def update_preference(self, key: str, value: bool) -> None:
        """Optionally prefer shorter tasks when priorities are equal."""
        if key != "prefer_short_tasks":
            raise ValueError("Supported preference: prefer_short_tasks.")
        if type(value) is not bool:
            raise ValueError("Preference value must be a boolean.")
        self.preferences[key] = value

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all tasks, including completed ones, paired with their pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieves all tasks through Owner and schedules unfinished activities."""

    def __init__(self, owner: Owner) -> None:
        """Connect the scheduler to the owner whose pets need care."""
        self.owner = owner

    def get_pending_tasks(self, date: Date | None = None) -> list[tuple[Pet, Task]]:
        """Retrieve unfinished tasks due on or before the given day, defaulting to today."""
        day = date if date is not None else Date.today()
        return self.filter_tasks(completed=False, due_on=day)

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None,
        due_on: Date | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Filter tasks by status, exact pet name, and optional latest due date."""
        if completed is not None and type(completed) is not bool:
            raise ValueError("Completion filter must be True, False, or None.")
        if due_on is not None and type(due_on) is not Date:
            raise ValueError("Due-date filter must be a datetime.date object.")
        name = pet_name.strip().casefold() if pet_name is not None else None
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if (completed is None or task.completed == completed)
            and (name is None or pet.name.casefold() == name)
            and (due_on is None or task.due_date <= due_on)
        ]

    def sort_by_time(
        self, tasks: list[tuple[Pet, Task]] | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return tasks ordered by HH:MM time, placing tasks without a time last."""
        entries = self.owner.get_all_tasks() if tasks is None else tasks
        # Zero-padded HH:MM strings sort in chronological order.
        return sorted(
            entries, key=lambda entry: (entry[1].time is None, entry[1].time or "")
        )

    def sort_tasks(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Sort by priority, preserving input order unless shorter is preferred."""
        prefer_short = self.owner.preferences["prefer_short_tasks"]
        return sorted(
            tasks,
            key=lambda entry: (
                Task.PRIORITIES[entry[1].priority],
                entry[1].duration_minutes if prefer_short else 0,
            ),
        )

    def detect_conflicts(
        self, tasks: list[tuple[Pet, Task]] | None = None
    ) -> list[str]:
        """Group unfinished tasks by due date and start time and return conflict warnings."""
        entries = self.owner.get_all_tasks() if tasks is None else tasks
        slots: dict[tuple[Date, str], list[str]] = {}
        for pet, task in entries:
            if task.completed or task.time is None:
                continue
            slot = (task.due_date, task.time)
            slots.setdefault(slot, []).append(f"{pet.name}: {task.description}")

        warnings = []
        for (day, time), activities in sorted(slots.items()):
            if len(activities) > 1:
                warnings.append(
                    f"Time conflict on {day} at {time}: {'; '.join(activities)}."
                )
        return warnings

    def generate_plan(self, date: Date | None = None) -> dict:
        """Select due tasks within the time budget and report conflicts without moving tasks."""
        day = date if date is not None else Date.today()
        remaining = self.owner.available_minutes
        scheduled = []
        unscheduled = []
        for pet, task in self.sort_tasks(self.get_pending_tasks(day)):
            entry = {"pet": pet, "task": task}
            if task.duration_minutes <= remaining:
                scheduled.append(entry)
                remaining -= task.duration_minutes
            else:
                unscheduled.append(entry)

        total = self.owner.available_minutes - remaining
        return {
            "date": day,
            "scheduled_tasks": scheduled,
            "unscheduled_tasks": unscheduled,
            "total_duration": total,
            "remaining_minutes": remaining,
            "warnings": self.detect_conflicts([
                (entry["pet"], entry["task"]) for entry in scheduled
            ]),
            "explanation": (
                f"Scheduled {len(scheduled)} unfinished tasks due by {day} by priority using "
                f"{total} of {self.owner.available_minutes} available minutes. "
                f"Shorter tasks break priority ties: "
                f"{self.owner.preferences['prefer_short_tasks']}. "
                f"{len(unscheduled)} tasks did not fit the remaining time."
            ),
        }

    def mark_task_complete(
        self, task_id: str, completed_on: Date | None = None
    ) -> Task | None:
        """Complete an unfinished task and add its daily or weekly repeat to the pet."""
        if completed_on is not None and type(completed_on) is not Date:
            raise ValueError("Completion date must be a datetime.date object.")
        for pet, task in self.owner.get_all_tasks():
            if task.task_id == task_id:
                if task.completed:
                    return None

                next_task = None
                interval = {"daily": 1, "weekly": 7}.get(task.frequency)
                if interval is not None:
                    today = completed_on if completed_on is not None else Date.today()
                    next_task = Task(
                        task.description, task.duration_minutes,
                        frequency=task.frequency, priority=task.priority,
                        time=task.time, due_date=today + timedelta(days=interval),
                    )

                task.mark_complete()
                if next_task is not None:
                    pet.add_task(next_task)
                return next_task
        raise ValueError(f"Task {task_id!r} was not found for this owner.")
