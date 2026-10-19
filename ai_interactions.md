# AI Interactions

## Agent Workflow

**Task requested:** Finalize PawPal+ against the rubric, including the advanced
algorithm and persistence stretch features. Keep the four-class domain design and
verify that the UI, demo, UML, documentation, and tests agree.

**What the agent completed:** The Codex coding assistant inspected the repository,
edited related files, and ran the terminal demo and pytest. It added a next-slot
search across pets and JSON persistence, then exercised both through the UI.

| Files modified | Work completed |
|----------------|----------------|
| `pawpal_system.py`, `tests/test_available_slots.py` | Added and tested `Scheduler.find_next_available_slot()`, a duration-aware interval search across all pets. |
| `storage.py`, `tests/test_storage.py`, `.gitignore` | Added atomic UTF-8 JSON save/load, restored IDs and dates, validation, and ignored generated data files. |
| `app.py`, `tests/test_app.py` | Connected sorting, filtering, warnings, recurrence, time suggestions, and Save/Load controls; tested independent sessions. |
| `main.py` | Demonstrated out-of-order tasks, filters, recurrence, conflict warnings, and a suggested free interval. |
| `diagrams/uml_final.mmd`, `README.md`, `reflection.md`, `ai_interactions.md` | Matched the final architecture and documented behavior, test evidence, tradeoffs, and the workflow. |

**Manual corrections and design decisions:** The user rejected the extra
Task.next_occurrence reference and asked to put recurrence in Scheduler. The user
also requested merging complete_task and mark_task_complete into one method and
clarified that daily recurrence is today plus one day. These corrections are in
the final implementation. The user requested reverting the first demo rewrite,
then later asked for a polished English output and a shorter reflection.

During the rubric audit, the agent kept exact-time warnings lightweight and added
interval search as a separate suggestion rather than silently moving tasks. No
additional manual code corrections were needed after the final tests passed.
The user should review the first-person reflection to confirm it represents their
experience before submitting.

**Verification:** `python main.py` prints a cross-pet conflict and suggests 18:30
for a task that would otherwise collide. `python -m pytest` covers the backend,
Streamlit workflow, interval search, JSON round trips, bad input files, and loading
into a new session. The README contains actual captured output. An AST comparison
checks the final UML's method names against all four domain classes.
