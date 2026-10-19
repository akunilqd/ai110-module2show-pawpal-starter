"""Checks for multi-pet scheduling and core task-management behavior."""

from datetime import date
import unittest
from unittest.mock import patch

from pawpal_system import Owner, Pet, Scheduler, Task


class PawPalTests(unittest.TestCase):
    def setUp(self):
        self.owner = Owner("Jordan", 30)
        self.dog = Pet("Mochi", 24, "dog")
        self.cat = Pet("Luna", 12, "cat")
        self.owner.add_pet(self.dog)
        self.owner.add_pet(self.cat)
        self.walk = Task("Walk", 20, priority="medium")
        self.feed = Task("Feed", 10, priority="high")
        self.dog.add_task(self.walk)
        self.cat.add_task(self.feed)
        self.scheduler = Scheduler(self.owner)

    def test_multi_pet_plan_uses_owner_method_and_exact_budget(self):
        with patch.object(
            self.owner, "get_all_tasks", wraps=self.owner.get_all_tasks
        ) as get_tasks:
            plan = self.scheduler.generate_plan(date.today())
        get_tasks.assert_called_once_with()
        self.assertEqual(
            [(entry["pet"], entry["task"]) for entry in plan["scheduled_tasks"]],
            [(self.cat, self.feed), (self.dog, self.walk)],
        )
        self.assertEqual(plan["total_duration"], 30)
        self.assertEqual(plan["remaining_minutes"], 0)
        self.assertEqual(plan["date"], date.today())
        self.assertEqual(self.owner.available_minutes, 30)
        self.assertFalse(self.feed.completed)

    def test_oversized_task_does_not_block_smaller_tasks(self):
        self.cat.edit_task(self.feed.task_id, duration_minutes=40)
        plan = self.scheduler.generate_plan()
        self.assertEqual(plan["scheduled_tasks"][0]["task"], self.walk)
        self.assertEqual(plan["unscheduled_tasks"][0]["task"], self.feed)
        self.assertEqual(plan["remaining_minutes"], 10)

    def test_completion_across_pets_and_reset(self):
        self.scheduler.mark_task_complete(self.feed.task_id)
        self.assertEqual(self.scheduler.get_pending_tasks(), [(self.dog, self.walk)])
        # Completing a daily task also registers tomorrow's unfinished occurrence.
        self.assertEqual(len(self.owner.get_all_tasks()), 3)
        self.feed.reset_completion()
        self.assertEqual(len(self.scheduler.get_pending_tasks()), 2)
        with self.assertRaises(ValueError):
            self.scheduler.mark_task_complete("missing")

    def test_preference_breaks_priority_ties(self):
        self.cat.edit_task(self.feed.task_id, priority="medium")
        tasks = self.owner.get_all_tasks()
        self.assertEqual(self.scheduler.sort_tasks(tasks)[0][1], self.walk)
        self.owner.update_preference("prefer_short_tasks", True)
        self.assertEqual(self.scheduler.sort_tasks(tasks)[0][1], self.feed)

    def test_task_edit_preserves_identity_and_is_atomic(self):
        self.walk.mark_complete()
        task_id = self.walk.task_id
        self.dog.edit_task(task_id, description="Evening walk", frequency="twice daily")
        self.assertEqual(self.walk.description, "Evening walk")
        self.assertEqual(self.walk.task_id, task_id)
        self.assertTrue(self.walk.completed)
        with self.assertRaises(ValueError):
            self.dog.edit_task(task_id, description="Changed", duration_minutes=-1)
        self.assertEqual(self.walk.description, "Evening walk")

    def test_remove_pet_and_task_updates_owner_results(self):
        self.dog.remove_task(self.walk.task_id)
        self.assertEqual(self.owner.get_all_tasks(), [(self.cat, self.feed)])
        self.owner.remove_pet(self.cat)
        self.assertEqual(self.owner.get_all_tasks(), [])

    def test_empty_and_zero_budget_plans(self):
        self.assertEqual(Scheduler(Owner("Alex", 0)).generate_plan()["scheduled_tasks"], [])
        self.owner.update_available_time(0)
        plan = self.scheduler.generate_plan()
        self.assertEqual(plan["scheduled_tasks"], [])
        self.assertEqual(len(plan["unscheduled_tasks"]), 2)

    def test_invalid_values_and_duplicate_registration(self):
        for minutes in (0, -1, True, 1.5):
            with self.subTest(minutes=minutes), self.assertRaises(ValueError):
                Task("Walk", minutes)
        with self.assertRaises(ValueError):
            Task("Walk", 10, priority="urgent")
        with self.assertRaises(ValueError):
            Task("", 10)
        with self.assertRaises(ValueError):
            self.owner.update_available_time(-1)
        with self.assertRaises(ValueError):
            self.dog.add_task(self.walk)
        with self.assertRaises(ValueError):
            self.owner.add_pet(self.dog)


if __name__ == "__main__":
    unittest.main()
