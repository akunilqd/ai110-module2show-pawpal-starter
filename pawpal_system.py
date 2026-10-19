"""PawPal+ backend skeleton based on diagrams/uml_draft.mmd.

Care tasks are dictionaries containing id, name, duration_minutes, and priority.
Scheduled entries reference a pet and its task. Constructors initialize state;
all other methods are empty stubs for the next implementation phase.
"""

from __future__ import annotations

from datetime import date as Date
from typing import Any


class Owner:
    """An owner with a daily time budget, preferences, and pets."""

    def __init__(self, name: str, available_minutes: int) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: dict[str, Any] = {}
        self.pets: list[Pet] = []

    def update_available_time(self, minutes: int) -> None:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def update_preference(self, key: str, value: Any) -> None:
        pass


class Pet:
    """A pet and the care needs and tasks associated with it."""

    def __init__(self, name: str, age_months: int) -> None:
        self.name = name
        self.age_months = age_months
        self.care_needs: list[str] = []
        self.care_tasks: list[dict[str, Any]] = []

    def add_task(self, task: dict[str, Any]) -> None:
        pass

    def edit_task(self, task_id: str, updates: dict[str, Any]) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def update_care_needs(self, needs: list[str]) -> None:
        pass


class DailyPlan:
    """A dated plan of care tasks that fit within a daily time budget."""

    def __init__(self, date: Date, available_minutes: int) -> None:
        self.date = date
        self.available_minutes = available_minutes
        self.scheduled_tasks: list[dict[str, Any]] = []
        self.unscheduled_tasks: list[dict[str, Any]] = []
        self.explanation: str = ""

    def add_task(self, pet: Pet, task: dict[str, Any]) -> None:
        pass

    def get_total_duration(self) -> int:
        pass

    def get_remaining_minutes(self) -> int:
        pass

    def explain_plan(self) -> str:
        pass


class Scheduler:
    """Uses owner preferences and pet tasks to generate a daily plan."""

    def sort_tasks(
        self, tasks: list[dict[str, Any]], preferences: dict[str, Any]
    ) -> list[dict[str, Any]]:
        pass

    def generate_plan(self, owner: Owner, date: Date) -> DailyPlan:
        pass
