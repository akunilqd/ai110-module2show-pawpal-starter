"""Run the PawPal+ logic and display a care schedule in the terminal."""

import sys

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, entries: list[dict]) -> None:
    """Display tasks in a table alongside their pets."""
    print(f"\n{title}")
    if not entries:
        print("  No tasks.")
        return

    priority_labels = {"high": "High", "medium": "Medium", "low": "Low"}
    rows = [("No.", "Pet", "Task", "Duration", "Priority")]

    for number, entry in enumerate(entries, start=1):
        pet, task = entry["pet"], entry["task"]
        rows.append((
            str(number),
            pet.name,
            task.description,
            f"{task.duration_minutes} min",
            priority_labels[task.priority],
        ))

    widths = [max(len(cell) for cell in column) for column in zip(*rows)]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    print(border)
    for index, row in enumerate(rows):
        print("| " + " | ".join(
            cell.ljust(width) for cell, width in zip(row, widths)
        ) + " |")
        if index == 0:
            print(border)
    print(border)


def main() -> None:
    owner = Owner("Khoa", available_minutes=40)

    dog = Pet("niki", age_months=2, species="dog")
    dog.add_task(Task("Walk", 30, priority="medium"))
    dog.add_task(Task("Feeding", 10, priority="high"))

    cat = Pet("skibidi", age_months=4, species="cat")
    cat.add_task(Task("Feeding", 10, priority="high"))
    cat.add_task(Task("Walk", 30, priority="medium"))
    cat.add_task(Task("Brushing", 20, priority="low"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("=" * 62)
    print("PAWPAL+ | Today's Schedule")
    print(f"Date: {plan['date']:%d/%m/%Y} | Owner: {owner.name}")
    print(f"Pets: {len(owner.pets)} | Available time: {owner.available_minutes} minutes")
    print("=" * 62)

    print_tasks("SCHEDULED TASKS", plan["scheduled_tasks"])
    print_tasks("UNSCHEDULED TASKS - NOT ENOUGH TIME", plan["unscheduled_tasks"])

    print(f"\nScheduled: {len(plan['scheduled_tasks'])} tasks")
    print(f"Total duration: {plan['total_duration']} minutes")
    print(f"Remaining time: {plan['remaining_minutes']} minutes")
    print("\nTasks are considered by priority. If one does not fit, the next is checked.")
    print("Tasks with equal priority keep their original order.")


if __name__ == "__main__":
    # Use UTF-8 output on Windows and when redirecting output.
    sys.stdout.reconfigure(encoding="utf-8")
    main()
