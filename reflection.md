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
tracks remaining time, and skips completed tasks. Frequency is descriptive for now;
the UI's `title` will need mapping to Task.description when connected.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
reflection. To verify the implementation, I ran main.py and pytest. With a
40-minute budget, the demo schedules two 10-minute feeding tasks and one
20-minute brushing task, leaving both 30-minute walks unscheduled. Tests check
completion, task addition, multi-pet retrieval, and time-budget behavior.

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
