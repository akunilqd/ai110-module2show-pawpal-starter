# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation Summary

The backend in `pawpal_system.py` uses four classes: `Task` stores an activity's
description, duration, frequency, priority, and completion status; `Pet` manages its
tasks; `Owner` manages pets and gathers their tasks through `get_all_tasks()`;
and `Scheduler` uses that method to plan across all pets. It skips completed tasks,
sorts by priority, and selects tasks within the owner's time budget, reporting
scheduled tasks, tasks that did not fit, and remaining minutes.

`main.py` displays the plan as terminal tables, including time sorting and filtering.
`app.py` connects the backend to Streamlit and keeps the owner in session state.
Completing a daily or weekly task through `Scheduler.mark_task_complete(task_id)`
adds a separate unfinished occurrence to the same pet, preserving the original as
completed. Its due date is one or seven days after the completion date (today by
default). Repeated completion does not create duplicates. Other
frequencies do not repeat automatically. Plans include overdue tasks and exclude
future occurrences. Tests cover task management, recurrence, and multi-pet planning.

`Task.mark_complete()` only changes completion status. `Scheduler` handles
recurrence: it skips completed tasks, completes an unfinished task, and adds its
next daily or weekly occurrence. Use the Scheduler method for recurring tasks.
Tasks keep their time, duration, and priority. `Scheduler.detect_conflicts()` groups
unfinished tasks by due date and start time, returning warning messages when a
slot is shared by tasks for the same pet or different pets. Plans include these
warnings for selected tasks; the terminal demo and Streamlit display them without
stopping or moving tasks. This lightweight check detects identical start times;
overlapping durations with different start times are not checked.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output


Run the terminal demo with `python main.py`:

```text
==============================================================
PAWPAL+ | Today's Schedule
Date: 19/10/2026 | Owner: Khoa
Pets: 2 | Available time: 40 minutes
==============================================================

ORIGINAL ORDER
+-----+---------+----------+------------+-------+----------+----------+-----------+
| No. | Pet     | Task     | Due date   | Time  | Duration | Priority | Status    |
+-----+---------+----------+------------+-------+----------+----------+-----------+
| 1   | niki    | Walk     | 2026-10-19 | 17:30 | 30 min   | Medium   | Pending   |
| 2   | niki    | Feeding  | 2026-10-19 | 08:00 | 10 min   | High     | Completed |
| 3   | niki    | Feeding  | 2026-10-20 | 08:00 | 10 min   | High     | Pending   |
| 4   | skibidi | Feeding  | 2026-10-19 | 17:30 | 10 min   | High     | Pending   |
| 5   | skibidi | Walk     | 2026-10-19 | 18:00 | 30 min   | Medium   | Pending   |
| 6   | skibidi | Brushing | 2026-10-19 | 12:15 | 20 min   | Low      | Pending   |
+-----+---------+----------+------------+-------+----------+----------+-----------+

ALL TASKS SORTED BY TIME
+-----+---------+----------+------------+-------+----------+----------+-----------+
| No. | Pet     | Task     | Due date   | Time  | Duration | Priority | Status    |
+-----+---------+----------+------------+-------+----------+----------+-----------+
| 1   | niki    | Feeding  | 2026-10-19 | 08:00 | 10 min   | High     | Completed |
| 2   | niki    | Feeding  | 2026-10-20 | 08:00 | 10 min   | High     | Pending   |
| 3   | skibidi | Brushing | 2026-10-19 | 12:15 | 20 min   | Low      | Pending   |
| 4   | niki    | Walk     | 2026-10-19 | 17:30 | 30 min   | Medium   | Pending   |
| 5   | skibidi | Feeding  | 2026-10-19 | 17:30 | 10 min   | High     | Pending   |
| 6   | skibidi | Walk     | 2026-10-19 | 18:00 | 30 min   | Medium   | Pending   |
+-----+---------+----------+------------+-------+----------+----------+-----------+

COMPLETED TASKS
+-----+------+---------+------------+-------+----------+----------+-----------+
| No. | Pet  | Task    | Due date   | Time  | Duration | Priority | Status    |
+-----+------+---------+------------+-------+----------+----------+-----------+
| 1   | niki | Feeding | 2026-10-19 | 08:00 | 10 min   | High     | Completed |
+-----+------+---------+------------+-------+----------+----------+-----------+

PENDING TASKS FOR NIKI (SORTED BY TIME)
+-----+------+------+------------+-------+----------+----------+---------+
| No. | Pet  | Task | Due date   | Time  | Duration | Priority | Status  |
+-----+------+------+------------+-------+----------+----------+---------+
| 1   | niki | Walk | 2026-10-19 | 17:30 | 30 min   | Medium   | Pending |
+-----+------+------+------------+-------+----------+----------+---------+

NEXT DAILY OCCURRENCE (EXCLUDED FROM TODAY'S PLAN)
+-----+------+---------+------------+-------+----------+----------+---------+
| No. | Pet  | Task    | Due date   | Time  | Duration | Priority | Status  |
+-----+------+---------+------------+-------+----------+----------+---------+
| 1   | niki | Feeding | 2026-10-20 | 08:00 | 10 min   | High     | Pending |
+-----+------+---------+------------+-------+----------+----------+---------+

SCHEDULED TASKS
+-----+---------+---------+------------+-------+----------+----------+---------+
| No. | Pet     | Task    | Due date   | Time  | Duration | Priority | Status  |
+-----+---------+---------+------------+-------+----------+----------+---------+
| 1   | skibidi | Feeding | 2026-10-19 | 17:30 | 10 min   | High     | Pending |
| 2   | niki    | Walk    | 2026-10-19 | 17:30 | 30 min   | Medium   | Pending |
+-----+---------+---------+------------+-------+----------+----------+---------+

UNSCHEDULED TASKS - NOT ENOUGH TIME
+-----+---------+----------+------------+-------+----------+----------+---------+
| No. | Pet     | Task     | Due date   | Time  | Duration | Priority | Status  |
+-----+---------+----------+------------+-------+----------+----------+---------+
| 1   | skibidi | Walk     | 2026-10-19 | 18:00 | 30 min   | Medium   | Pending |
| 2   | skibidi | Brushing | 2026-10-19 | 12:15 | 20 min   | Low      | Pending |
+-----+---------+----------+------------+-------+----------+----------+---------+

CONFLICT WARNINGS
WARNING: Time conflict on 2026-10-19 at 17:30: skibidi: Feeding; niki: Walk.

Scheduled: 2 tasks
Total duration: 40 minutes
Remaining time: 0 minutes

Tasks are considered by priority. If one does not fit, the next is checked.
Tasks with equal priority keep their original order.
The time-sorting view uses HH:MM; the plan uses priority and duration.
Matching dates and start times produce warnings; tasks are not moved automatically.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The Scheduler retrieves tasks across all pets through `Owner.get_all_tasks()`.

| Feature | Method(s) | Behavior |
|---------|-----------|----------|
| Time sorting | `Scheduler.sort_by_time()` | Sorts validated `HH:MM` start times; untimed tasks go last. Equal times keep their original order. |
| Priority sorting | `Scheduler.sort_tasks()` | Orders high, medium, then low priority. Optionally prefers shorter durations when priorities tie. |
| Filtering | `Scheduler.filter_tasks()` | Filters by completion status, pet name (case insensitive), or latest due date; filters can be combined. |
| Daily planning | `Scheduler.get_pending_tasks()`, `Scheduler.generate_plan()` | Includes unfinished tasks due by the selected date. Fits tasks into the minute budget and continues after a task does not fit. |
| Conflict warnings | `Scheduler.detect_conflicts()` | Groups unfinished tasks by due date and start time across pets. Returns warnings without stopping or rescheduling; plans report conflicts among selected tasks. |
| Recurring tasks | `Scheduler.mark_task_complete()` | Completes the original and adds a new task to the same pet: daily = completion date + 1 day, weekly = + 7 days. Already completed tasks are skipped; other frequencies do not repeat. |

Time sorting is a separate view; the daily plan selects tasks by priority and
duration. Conflict detection checks exact start-time matches, so partial overlaps
are not detected. The implementation keeps explicit loops where they make the
algorithm easier to read. Tasks carry dates and times but no timezone information.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
