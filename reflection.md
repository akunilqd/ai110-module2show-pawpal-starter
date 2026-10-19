# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My design uses four classes:

- **Owner:** Manages available time, preferences, and pets.
- **Pet:** Stores pet information and manages care needs and tasks.
- **DailyPlan:** Holds scheduled and unscheduled tasks, calculates remaining time,
  and explains the plan.
- **Scheduler:** Sorts tasks and creates a plan using availability and preferences.

An Owner has Pets, and each planned task references its Pet. The Scheduler reads
these objects without duplicating their data.

**b. Design changes**

I renamed `time` to `available_minutes` for clarity, added `edit_task()` to support
editing, and made total duration calculated to avoid outdated values.

To match Step 1, I replaced DailyPlan with Task, which stores description,
duration, frequency, priority, and completion status. Plans are now dictionaries.
Owner.get_all_tasks() returns every pet's tasks paired with its pet, and Scheduler
uses this method to plan across multiple pets. The implementation validates inputs,
tracks remaining time, and skips completed tasks. Daily and weekly completion now
creates a dated follow-up through Scheduler. The Streamlit UI uses these classes
and stores the Owner in session state.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers completion status, due date, priority, and available
minutes. It can prefer shorter tasks when priorities match. Only unfinished tasks
due by the plan date are considered, and tasks cannot exceed the remaining budget.

**b. Tradeoffs**

Conflict detection checks identical due dates and start times instead of full
duration overlaps. Grouping tasks by date and time keeps the logic simple and
produces warnings without interrupting planning. However, an 08:00 task lasting
30 minutes and an 08:15 task will not trigger a warning. This is reasonable for
the first version; checking intervals would make a future version more accurate.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to brainstorm the UML, create and implement the classes, review their
relationships, format the terminal schedule, and draft tests and docstrings.
AI suggested using Owner.get_all_tasks() for multi-pet scheduling and separate
Task objects for each pet so completion status is independent. I accepted both.
Questions about how Scheduler retrieves tasks and how to print the plan were
especially helpful for understanding how the objects work together.

**b. Judgment and verification**

I reverted the first AI rewrite of main.py so I could review my own version,
then requested a polished output. I also asked AI to shorten an overly long
reflection. To verify the implementation, I ran main.py and pytest. The current
40-minute demo schedules a 10-minute feeding and a 30-minute walk and prints a
warning because both start at 17:30. Tests cover sorting, filtering, conflicts,
recurrence, and the Streamlit workflow.

When reviewing detect_conflicts(), AI suggested keeping dictionary grouping
instead of comparing every task pair and using an explicit loop to build warning
messages. I accepted the loop because it is easier to read than a compact list
comprehension. Both versions use the same grouping and sorting strategy, so this
change improves readability rather than claiming a performance improvement.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
