# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My original design used Owner for availability and pets, Pet for care needs and
tasks, DailyPlan for the schedule and explanation, and Scheduler for planning.
Keeping these responsibilities separate made the relationships easier to explain.

**b. Design changes**

I replaced DailyPlan with Task to match the project requirements. Task stores an
activity's duration, time, due date, frequency, priority, and status; plans are
now dictionaries. Owner.get_all_tasks() returns pet-task pairs so Scheduler can
work across all pets without losing ownership. I also moved recurrence entirely
into Scheduler and removed the extra next_occurrence reference and duplicate
completion method. The final UML reflects these decisions.
Persistence lives in storage.py as save/load functions, so the domain still has
four classes. An optional next-slot search adds duration-aware suggestions.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler selects unfinished tasks due by the plan date, orders them by
priority, and fits them into the available minutes. An optional preference favors
shorter tasks when priorities match. Time sorting is a separate display choice.

**b. Tradeoffs**

Conflict detection checks identical due dates and start times instead of full
duration overlaps. This keeps the code understandable and returns warnings without
stopping the app. However, an 08:00 task lasting 30 minutes and an 08:15 task will
not trigger a warning. The greedy time-budget plan is also easy to follow but does
not guarantee the best possible combination of tasks.
The separate next-slot search checks duration intervals when suggesting a new
time. JSON snapshots keep persistence simple, but users must explicitly save and
load, and the file is not a multi-user database.

## 3. AI Collaboration

**a. How you used AI**

Chat explanations helped me understand constructors, object references, session
state, and how Scheduler retrieves tasks from Owner. Automatic file editing was
most effective for keeping the backend, UI, tests, and UML consistent. Running
main.py and pytest provided concrete feedback instead of relying on generated code.

I organized requests by design, implementation, UI, testing, and documentation
within one ongoing chat, rather than separate chat sessions. These phase-specific
requests kept each step focused. In future, separate sessions could make phases
easier to revisit, with the code and UML supplying shared context.

**b. Judgment and verification**

I rejected the more complex recurrence design that stored next_occurrence on
Task. I asked AI to move recurrence into Scheduler and combine complete_task and
mark_task_complete into one method. This left Task responsible for its own status
and Scheduler responsible for creating and attaching recurring tasks.

I also accepted a plain loop for conflict warnings instead of a compact list
comprehension because readability mattered more than shorter code. I verified
changes with backend tests, Streamlit interaction tests, and the terminal demo.

## 4. Testing and Verification

**a. What you tested**

Tests cover completion, task addition and editing, sorting, filters, multi-pet
ownership, budgets, daily and weekly recurrence, calendar boundaries, future and
overdue tasks, duplicate completion, and exact-time conflicts. UI tests verify
session persistence, validation, filtered tables, and resolving a conflict by
editing a task time. These checks protect both the logic and its connection to UI.
Additional tests verify interval search across pets, exact-fit gaps, JSON round
trips, malformed files, and restoring tasks in a new Streamlit session.

**b. Confidence**

My confidence is 4/5 for the implemented features. The full test suite passes,
but I would next test partial overlaps, real-browser interaction, larger task
lists, and reopening completed recurring tasks. Passing tests supports confidence
in the tested behaviors; it does not prove every possible case works.

## 5. Reflection

**a. What went well**

The same four backend classes now support both the terminal demo and Streamlit.
Multi-pet planning, conflict warnings, recurrence, time suggestions, and JSON
save/load work together while preserving the four-class design.

**b. What you would improve**

I would extend conflict warnings to partial overlaps, support per-owner storage,
and add broader task editing. JSON now preserves data between runs. Time
suggestions help resolve warnings, but the owner still chooses whether to apply
them rather than having tasks move silently.

**c. Key takeaway**

Being the lead architect means choosing responsibilities, keeping scope manageable,
and checking that the UI, algorithms, tests, and documentation agree. AI helped
with implementation, but I still needed to question unnecessary complexity,
understand the behavior, and decide which suggestions fit the project.
