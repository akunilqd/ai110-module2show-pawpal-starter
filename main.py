"""Run the PawPal+ logic and display a care schedule in the terminal."""

import sys

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, entries: list[tuple[Pet, Task]]) -> None:
    """Display tasks in a table alongside their pets."""
    print(f"\n{title}")
    if not entries:
        print("  No tasks.")
        return

    priority_labels = {"high": "High", "medium": "Medium", "low": "Low"}
    rows = [("No.", "Pet", "Task", "Due date", "Time", "Duration", "Priority", "Status")]

    for number, (pet, task) in enumerate(entries, start=1):
        rows.append((
            str(number),
            pet.name,
            task.description,
            task.due_date.isoformat(),
            task.time if task.time is not None else "Not set",
            f"{task.duration_minutes} min",
            priority_labels[task.priority],
            "Completed" if task.completed else "Pending",
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
    # Add activities out of time order to demonstrate chronological sorting.
    dog.add_task(Task("Walk", 30, priority="medium", time="17:30"))
    dog.add_task(Task("Feeding", 10, priority="high", time="08:00"))

    cat = Pet("skibidi", age_months=4, species="cat")
    # Same time as Niki's walk: both tasks fit the budget but need a warning.
    cat.add_task(Task("Feeding", 10, priority="high", time="17:30"))
    cat.add_task(Task("Walk", 30, priority="medium", time="18:00"))
    cat.add_task(Task("Brushing", 20, priority="low", time="12:15"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(dog.tasks[1].task_id)
    plan = scheduler.generate_plan()

    print("=" * 62)
    print("PAWPAL+ | Today's Schedule")
    print(f"Date: {plan['date']:%d/%m/%Y} | Owner: {owner.name}")
    print(f"Pets: {len(owner.pets)} | Available time: {owner.available_minutes} minutes")
    print("=" * 62)

    print_tasks("ORIGINAL ORDER", owner.get_all_tasks())
    print_tasks("ALL TASKS SORTED BY TIME", scheduler.sort_by_time())
    print_tasks("COMPLETED TASKS", scheduler.filter_tasks(completed=True))
    print_tasks(
        "PENDING TASKS FOR NIKI (SORTED BY TIME)",
        scheduler.sort_by_time([
            (pet, task) for pet, task in scheduler.get_pending_tasks() if pet is dog
        ]),
    )
    if next_task is not None:
        print_tasks("NEXT DAILY OCCURRENCE (EXCLUDED FROM TODAY'S PLAN)", [(dog, next_task)])

    print_tasks("SCHEDULED TASKS", [
        (entry["pet"], entry["task"]) for entry in plan["scheduled_tasks"]
    ])
    print_tasks("UNSCHEDULED TASKS - NOT ENOUGH TIME", [
        (entry["pet"], entry["task"]) for entry in plan["unscheduled_tasks"]
    ])

    print("\nCONFLICT WARNINGS")
    for warning in plan["warnings"]:
        print(f"WARNING: {warning}")
    if not plan["warnings"]:
        print("No tasks share the same date and time.")

    print(f"\nScheduled: {len(plan['scheduled_tasks'])} tasks")
    print(f"Total duration: {plan['total_duration']} minutes")
    print(f"Remaining time: {plan['remaining_minutes']} minutes")
    print("\nTasks are considered by priority. If one does not fit, the next is checked.")
    print("Tasks with equal priority keep their original order.")
    print("The time-sorting view uses HH:MM; the plan uses priority and duration.")
    print("Matching dates and start times produce warnings; tasks are not moved automatically.")


if __name__ == "__main__":
    # Use UTF-8 output on Windows and when redirecting output.
    sys.stdout.reconfigure(encoding="utf-8")
    main()
