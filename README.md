# PawPal+

PawPal+ helps an owner plan care for multiple pets within a daily time budget.
A Streamlit interface and a terminal demo share the same four backend classes.

## Features

- Add multiple pets and assign separate care tasks to each one.
- Track descriptions, duration, priority, frequency, due date, time, and status.
- Sort by chronological `HH:MM` time or priority, and filter by pet or completion.
- Build a multi-pet plan of unfinished, due tasks that fits the available minutes.
- Display conflict warnings with affected pets, activities, dates, and start times.
- Complete daily/weekly tasks and automatically add their next dated occurrence.
- Suggest a duration-sized free interval across pets, then apply it through the UI.
- Save and load JSON so pet and task data survives application restarts.

## Setup and run

Create an environment:

```bash
python -m venv .venv
```

Activate it using `.\.venv\Scripts\Activate.ps1` in PowerShell or
`source .venv/bin/activate` on macOS/Linux. Then install and launch:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Run the terminal demo with:

```bash
python main.py
```

## Architecture and final UML

| Class | Responsibility |
|-------|----------------|
| `Task` | Stores a care activity, its due date/time, duration, frequency, priority, and completion status. |
| `Pet` | Stores identifying details and a collection of tasks with add, edit, and remove methods. |
| `Owner` | Manages pets and returns every pet's tasks as `(pet, task)` pairs through `get_all_tasks()`. |
| `Scheduler` | Retrieves those pairs to sort, filter, plan, detect conflicts, find available intervals, and create recurring tasks for the correct pet. |

The required Mermaid source is [diagrams/uml_final.mmd](diagrams/uml_final.mmd).
It matches the final backend methods and relationships. The original
[working draft](diagrams/uml_draft.mmd) is retained separately. Plans are
plain dictionaries; DailyPlan is not a fifth class. `storage.py` contains save/load
functions, keeping persistence separate from the four-class domain design.

## Smarter Scheduling

All algorithms retrieve tasks across pets through `Owner.get_all_tasks()`.

| Feature | Method | Behavior |
|---------|--------|----------|
| Time sorting | `Scheduler.sort_by_time()` | Orders validated `HH:MM` strings chronologically; untimed tasks go last and equal times keep input order. |
| Priority sorting | `Scheduler.sort_tasks()` | High, medium, then low priority; optionally prefer shorter durations when priorities tie. |
| Filtering | `Scheduler.filter_tasks()` | Combines completion status, case-insensitive exact pet name, and optional latest due date. |
| Daily planning | `Scheduler.get_pending_tasks()`, `Scheduler.generate_plan()` | Includes unfinished tasks due by the selected date, skips tasks exceeding remaining minutes, and continues looking for tasks that fit. |
| Conflict warnings | `Scheduler.detect_conflicts()` | Groups unfinished tasks by identical due date and start time across pets. Plans report conflicts among selected tasks. |
| Recurrence | `Scheduler.mark_task_complete()` | Completes the original and adds a new unfinished task to the same pet: daily = completion date + 1 day; weekly = + 7 days. |
| Advanced interval search | `Scheduler.find_next_available_slot()` | Sorts busy intervals across pets and scans for the earliest gap large enough for a requested duration. Handles overlaps, exact fits, excluded tasks, and no available interval. |

Time sorting is a display choice; the time-budget plan selects by priority and
duration. The greedy selection is understandable but is not an optimizer.
Exact-time warnings do not detect partial duration overlaps or move tasks.

The advanced slot search does check durations and overlapping busy intervals,
using a sort and scan in O(n log n) time. It considers unfinished timed tasks
on the selected date, ignores an optionally excluded task when rescheduling, and
returns an `HH:MM` string or `None`. The UI searches 08:00-20:00; the Python method
accepts a custom same-day window. Untimed tasks and previous-day spillover do not
reserve intervals. Dates and times do not include timezone information.

`Task.mark_complete()` only updates status. Use the Scheduler completion method
for automatic recurrence. Already completed tasks create no extra follow-up.
Other frequencies do not repeat automatically. Reopening a completed occurrence
resets its status, so completing it again may create another follow-up.

## Save and load data

1. Add pets and tasks, then click **Save data** in the sidebar.
2. PawPal+ creates `data/pawpal.json`. Saving again replaces that snapshot;
   changes are not automatically saved.
3. Restart the app or open a new session and click **Load data**.
4. The saved owner replaces the in-memory owner; generate a new schedule.

The snapshot preserves owner preferences, pet details and care needs, task IDs,
dates, times, durations, priorities, frequencies, and completion status. Missing
or malformed data produces an error without replacing the current owner.
Writing uses a temporary file and atomic replacement. This is one local owner
snapshot, not a multi-user database. Generated JSON and temporary files are ignored
by Git; session state alone would not preserve data across new sessions.

Persistence files modified: `storage.py`, `app.py`, `.gitignore`,
`tests/test_storage.py`, and `tests/test_app.py`. Direct Python usage:

```python
from storage import save_owner, load_owner

save_owner(owner, "data/pawpal.json")
restored_owner = load_owner("data/pawpal.json")
```

## Demo Walkthrough

1. **Set constraints.** Enter your name and available minutes, select whether
   shorter tasks break priority ties, and click **Save settings**.
2. **Add pets.** Register Niki and Skibidi, including species and age in months.
3. **Add tasks.** Choose the pet and supply a title, duration, priority, frequency,
   due date, and optional `HH:MM` time. Each pet receives its own Task objects.
4. **Explore.** Sort the overview by time or priority. Filter by pet, status, or
   tasks due today/overdue. These controls affect the overview, not plan selection.
5. **Plan.** With 40 available minutes, a 10-minute feeding and a 30-minute walk
   both fit. If both start today at 17:30, warnings identify the conflicting tasks
   and pets. Time metrics, selected tasks, skipped tasks, and reasoning remain visible.
6. **Resolve.** Under **Edit a task time**, choose a new start time or click
   **Suggest next available time**. Click **Update task time**, then regenerate
   the schedule. Edits invalidate the old plan; suggestions alone do not move tasks.
7. **Complete.** Select a due task and click **Mark complete**. A success message
   reports any daily/weekly follow-up. Its future date keeps it out of today's plan.
8. **Persist.** Click **Save data**. On your next visit, click **Load data** to
   restore the same pet and task history.

Overview warnings cover all unfinished tasks, including tasks hidden by filters;
plan warnings cover selected tasks. Owners can review dates and activities before
choosing a new time rather than having tasks silently rescheduled.

### Sample CLI output

`python main.py` creates an Owner, two Pets, and five initial Tasks, then shows
sorting, filtering, recurrence, conflict warnings, and a free-slot suggestion:

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

Next available time for Skibidi's feeding after 17:30: 18:30
The suggestion checks durations across all pets; no task is moved automatically.

Scheduled: 2 tasks
Total duration: 40 minutes
Remaining time: 0 minutes

Tasks are considered by priority. If one does not fit, the next is checked.
Tasks with equal priority keep their original order.
The time-sorting view uses HH:MM; the plan uses priority and duration.
Matching dates and start times produce warnings; tasks are not moved automatically.
```

## Testing PawPal+

With the environment activated, run:

```bash
python -m pytest
```

Tests cover completion, task addition/editing, chronological and priority sorting,
filtering, multi-pet ownership, time budgets, exact-time conflicts, daily/weekly
recurrence, calendar boundaries, duplicate completion, and future/overdue tasks.
Advanced tests cover overlapping busy intervals, exact-fit gaps, JSON round trips,
malformed files, preserved task IDs, and loading into an independent UI session.
Streamlit tests verify persistence, validation, filters, suggestions, and time edits.

Successful terminal output:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.7.0
rootdir: F:\AI CodePath\Project 02\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 77 items

test_pawpal_system.py ........                                           [ 10%]
tests\test_app.py ........                                               [ 20%]
tests\test_available_slots.py ..........                                 [ 33%]
tests\test_conflicts.py ......                                           [ 41%]
tests\test_pawpal.py ..                                                  [ 44%]
tests\test_recurring_tasks.py .................                          [ 66%]
tests\test_sorting_filtering.py ............                             [ 81%]
tests\test_storage.py ..............                                     [100%]

============================= 77 passed in 4.24s ==============================
```

**Confidence Level: ★★★★☆ (4/5).** All 77 tests pass.
The implemented features have reproducible checks. Exact-time warnings still
miss partial overlaps; timezone handling, real-browser behavior, larger task
lists, and multi-user storage would need further work or testing.

## Submission evidence

| Rubric item | Evidence |
|-------------|----------|
| Four-class OOP design and readable UML | [Final Mermaid source](diagrams/uml_final.mmd), [backend](pawpal_system.py) |
| Algorithms across multiple pets | Sorting, filters, conflicts, recurrence, and interval search in `Scheduler` |
| End-to-end demo | [main.py](main.py) and the fenced CLI output above |
| Meaningful passing pytest suite | [tests](tests/), [core tests](test_pawpal_system.py), and captured passing output above |
| Documentation and AI reflection | This manual and [reflection.md](reflection.md) |
| Advanced capability via agent mode | `find_next_available_slot()`, [interval tests](tests/test_available_slots.py), and [Agent Workflow](ai_interactions.md#agent-workflow) |
| Persistence stretch feature | [storage.py](storage.py), Save/Load UI, and [round-trip tests](tests/test_storage.py) |

The evidence maps to the 20 core rubric points and both optional stretch features;
final scoring remains the reviewer's decision. See [ai_interactions.md](ai_interactions.md)
for files changed, tasks given to the assistant, completed work, and corrections.
