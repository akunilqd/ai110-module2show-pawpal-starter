# PawPal+

A Streamlit app and terminal demo for managing care tasks across multiple pets.

## Run

Create and activate a virtual environment, then run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Terminal demo: `python main.py`. Tests: `python -m pytest`.

## Design

| Class | Responsibility |
|-------|----------------|
| `Task` | Description, due date/time, duration, frequency, priority, and status. |
| `Pet` | Pet details and methods to add, edit, and remove tasks. |
| `Owner` | Manages pets; `get_all_tasks()` returns `(pet, task)` pairs. |
| `Scheduler` | Sorts, filters, plans, checks conflicts, and handles recurrence across pets. |

[Final UML](diagrams/uml_final.mmd) | [AI reflection](reflection.md) |
[Agent Workflow](ai_interactions.md#agent-workflow)

## Smarter Scheduling

| Feature | Scheduler method | Behavior |
|---------|------------------|----------|
| Sorting | `sort_by_time()`, `sort_tasks()` | Chronological time or priority; optionally favor shorter tasks on priority ties. |
| Filtering | `filter_tasks()` | Combine pet name, completion status, and latest due date. |
| Planning | `generate_plan()` | Fit unfinished, due tasks into the available minutes across pets. |
| Conflicts | `detect_conflicts()` | Warn about matching dates and start times without stopping the app. |
| Recurrence | `mark_task_complete()` | Add a new task for the same pet: daily = completion + 1 day; weekly = + 7 days. |
| Free-slot search | `find_next_available_slot()` | Find a duration-sized gap across pets; the UI searches 08:00-20:00. |

Conflict warnings check exact start times, while free-slot suggestions consider
full durations. Suggestions require confirmation; tasks are not moved automatically.
The greedy plan is not an optimizer. Times are timezone-free; slot search ignores
untimed tasks and previous-day spillover. Reopening a recurring task can create
another follow-up if completed again.

## Save and load

Click **Save data** in the sidebar to write `data/pawpal.json`. After restarting,
click **Load data** to restore the owner, pets, task IDs, dates, and completion
status, then regenerate the plan. Saving replaces the snapshot; there is no autosave.
Invalid files show an error without replacing current data.

Persistence uses `storage.py`, with UI changes in `app.py`, file exclusions in
`.gitignore`, and tests in `tests/test_storage.py` and `tests/test_app.py`.
Generated data files stay out of Git. Storage is one local owner snapshot.

## Demo Walkthrough

1. Save your name and available minutes, add two pets, then add their care tasks.
2. Sort by time or priority and filter by pet/status in the task overview.
3. Click **Generate schedule** to see selected tasks, remaining time, and warnings.
4. Resolve conflicts with **Suggest next available time** and **Update task time**,
   then regenerate. **Mark complete** creates daily/weekly follow-ups; **Save data**
   preserves your work.

Selected output from `python main.py`:

```text
SCHEDULED TASKS
+-----+---------+---------+------------+-------+----------+----------+---------+
| No. | Pet     | Task    | Due date   | Time  | Duration | Priority | Status  |
+-----+---------+---------+------------+-------+----------+----------+---------+
| 1   | skibidi | Feeding | 2026-10-19 | 17:30 | 10 min   | High     | Pending |
| 2   | niki    | Walk    | 2026-10-19 | 17:30 | 30 min   | Medium   | Pending |
+-----+---------+---------+------------+-------+----------+----------+---------+

WARNING: Time conflict on 2026-10-19 at 17:30: skibidi: Feeding; niki: Walk.
Next available time for Skibidi's feeding after 17:30: 18:30

Scheduled: 2 tasks
Total duration: 40 minutes
Remaining time: 0 minutes
```

## Testing PawPal+

```bash
python -m pytest
```

Tests cover sorting, filtering, recurrence, conflict warnings, multi-pet planning,
time budgets, interval search, JSON round trips, validation, and Streamlit workflows.

Successful test output:

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

**Confidence: ★★★★☆ (4/5).** All 77 tests pass. Partial-overlap warnings,
real-browser behavior, timezone support, and large-scale use need further work.
