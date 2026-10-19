"""Streamlit interface for the PawPal+ pet-care logic layer."""

from datetime import date as Date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task
from storage import DATA_PATH, load_owner, save_owner


def task_rows(entries: list[tuple[Pet, Task]]) -> list[dict]:
    """Turn pet-task pairs into readable table rows."""
    return [
        {
            "Pet": pet.name,
            "Task": task.description,
            "Minutes": task.duration_minutes,
            "Time": task.time if task.time is not None else "Not set",
            "Frequency": task.frequency,
            "Due date": task.due_date.isoformat(),
            "Priority": task.priority.title(),
            "Status": "Completed" if task.completed else "Pending",
        }
        for pet, task in entries
    ]


st.set_page_config(page_title="PawPal+", page_icon="\U0001F43E", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Khoa", 40)

with st.sidebar:
    st.subheader("Saved data")
    st.caption("Save your pets and tasks, then load them on your next visit.")
    if st.button("Save data", key="save_data"):
        try:
            save_owner(st.session_state.owner, DATA_PATH)
        except (OSError, ValueError) as error:
            st.error(f"Could not save data: {error}")
        else:
            st.success("Pets and tasks saved.")
    if st.button("Load data", key="load_data"):
        try:
            restored_owner = load_owner(DATA_PATH)
        except (OSError, ValueError) as error:
            st.error(f"Could not load data: {error}")
        else:
            st.session_state.clear()
            st.session_state.owner = restored_owner
            st.session_state.loaded_notice = True
            st.rerun()
    if st.session_state.pop("loaded_notice", False):
        st.success("Saved pets and tasks restored.")

owner = st.session_state.owner

st.title("PawPal+")
st.write("Add your pets and their care tasks, then build a plan for your available time.")

st.subheader("Owner settings")
with st.form("owner_settings"):
    owner_name = st.text_input("Owner name", value=owner.name, key="owner_name")
    available_minutes = st.number_input(
        "Available time (minutes)", min_value=0,
        value=owner.available_minutes, key="available_minutes",
    )
    prefer_short = st.checkbox(
        "Prefer shorter tasks when priorities are equal",
        value=owner.preferences["prefer_short_tasks"], key="prefer_short",
    )
    save_owner = st.form_submit_button("Save settings")

if save_owner:
    if not owner_name.strip():
        st.error("Please enter an owner name.")
    else:
        owner.update_available_time(int(available_minutes))
        owner.update_preference("prefer_short_tasks", prefer_short)
        owner.name = owner_name.strip()
        st.session_state.pop("plan", None)
        st.success("Owner settings saved.")

st.subheader("Add a pet")
with st.form("add_pet"):
    pet_name = st.text_input("Pet name", key="pet_name")
    species = st.selectbox("Species", ["dog", "cat", "other"], key="species")
    age = st.number_input("Age in months", min_value=0, value=12, key="pet_age")
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    try:
        pet = Pet(pet_name, int(age), species)
        owner.add_pet(pet)
    except ValueError as error:
        st.error(str(error))
    else:
        st.session_state.pop("plan", None)
        st.success(f"Added {pet.name}!")

if owner.pets:
    st.table([
        {"Pet": pet.name, "Species": pet.species, "Age (months)": pet.age_months}
        for pet in owner.pets
    ])
else:
    st.info("Add a pet to start creating care tasks.")

st.subheader("Add a task")
if owner.pets:
    with st.form("add_task"):
        pet_index = st.selectbox(
            "Choose a pet", options=list(range(len(owner.pets))),
            format_func=lambda i: f"{i + 1}. {owner.pets[i].name} ({owner.pets[i].species})",
            key="task_pet",
        )
        task_title = st.text_input("Task title", key="task_title")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20, key="duration",
        )
        priority = st.selectbox(
            "Priority", ["low", "medium", "high"], index=2, key="priority",
        )
        frequency = st.text_input("Frequency", value="daily", key="frequency")
        task_time = st.text_input("Time (HH:MM, optional)", key="task_time", placeholder="08:30")
        due_date = st.date_input("Due date", key="due_date")
        st.caption("Daily and weekly tasks create their next occurrence when completed.")
        add_task = st.form_submit_button("Add task")

    if add_task:
        try:
            task = Task(
                task_title, int(duration), frequency, priority,
                time=task_time.strip() or None, due_date=due_date,
            )
            selected_pet = owner.pets[pet_index]
            selected_pet.add_task(task)
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state.pop("plan", None)
            st.success(f"Added task for {selected_pet.name}!")

scheduler = Scheduler(owner)
editable_tasks = scheduler.filter_tasks(completed=False)
if editable_tasks:
    st.subheader("Edit a task time")
    editable_by_id = {task.task_id: (pet, task) for pet, task in editable_tasks}
    edit_id = st.selectbox(
        "Task to reschedule", options=list(editable_by_id),
        format_func=lambda key: (
            f"{editable_by_id[key][0].name}: {editable_by_id[key][1].description} "
            f"(due {editable_by_id[key][1].due_date})"
        ), key="edit_task_id",
    )
    edit_pet, edit_task = editable_by_id[edit_id]
    edit_time_key = f"edit_time_{edit_id}"
    if edit_time_key not in st.session_state:
        st.session_state[edit_time_key] = edit_task.time or ""
    if st.button("Suggest next available time"):
        suggested_time = scheduler.find_next_available_slot(
            edit_task.duration_minutes, date=edit_task.due_date,
            exclude_task_id=edit_id,
        )
        if suggested_time is None:
            st.warning("No free interval fits this task between 08:00 and 20:00.")
        else:
            st.session_state[edit_time_key] = suggested_time
            st.info(f"Suggested {suggested_time}. Click 'Update task time' to apply it.")
    with st.form("edit_task_time"):
        new_time = st.text_input(
            "New time (HH:MM)", key=edit_time_key,
        )
        save_time = st.form_submit_button("Update task time")
    if save_time:
        try:
            edit_pet.edit_task(edit_id, time=new_time.strip())
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state.pop("plan", None)
            st.success(f"Updated {edit_pet.name}'s task to {edit_task.time}.")

pending_tasks = scheduler.get_pending_tasks()
if pending_tasks:
    with st.form("complete_task"):
        tasks_by_id = {task.task_id: (pet, task) for pet, task in pending_tasks}
        task_id = st.selectbox(
            "Task to complete", options=list(tasks_by_id),
            format_func=lambda task_id: (
                f"{tasks_by_id[task_id][0].name}: "
                f"{tasks_by_id[task_id][1].description} "
                f"(due {tasks_by_id[task_id][1].due_date})"
            ),
            key="completion_task",
        )
        complete_task = st.form_submit_button("Mark complete")

    if complete_task:
        next_task = scheduler.mark_task_complete(task_id)
        st.session_state.pop("plan", None)
        if next_task is not None:
            st.success(f"Task completed. Next occurrence added for {next_task.due_date}.")
        else:
            st.success("Task completed.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.subheader("Task overview")
    pet_filter = st.selectbox(
        "Filter by pet", ["All pets", *dict.fromkeys(pet.name for pet in owner.pets)],
        key="pet_filter",
    )
    status_filter = st.selectbox(
        "Filter by status", ["All statuses", "Pending", "Completed"], key="status_filter",
    )
    due_only = st.checkbox("Due today or overdue only", key="due_only")
    sort_order = st.selectbox(
        "Sort tasks by", ["Time", "Priority", "Original order"], key="sort_order",
    )
    completed = {"All statuses": None, "Pending": False, "Completed": True}[status_filter]
    visible_tasks = scheduler.filter_tasks(
        completed=completed,
        pet_name=None if pet_filter == "All pets" else pet_filter,
        due_on=Date.today() if due_only else None,
    )
    if sort_order == "Time":
        visible_tasks = scheduler.sort_by_time(visible_tasks)
    elif sort_order == "Priority":
        visible_tasks = scheduler.sort_tasks(visible_tasks)
    st.caption(f"Showing {len(visible_tasks)} of {len(all_tasks)} care tasks.")
    if visible_tasks:
        st.table(task_rows(visible_tasks))
    else:
        st.info("No tasks match these filters. Try another pet or status.")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.write("Conflicts to review across all pets")
        for warning in conflicts:
            st.warning(warning)
        st.info(
            "These tasks start together. Change one start time under 'Edit a task time', "
            "then generate the schedule again. Tasks are not moved automatically."
        )
else:
    st.info("No care tasks yet.")

st.divider()
st.subheader("Today's schedule")
st.caption(f"Planning for {owner.name} with {owner.available_minutes} available minutes.")

if st.button("Generate schedule", disabled=not all_tasks):
    st.session_state.plan = scheduler.generate_plan()

if "plan" in st.session_state:
    plan = st.session_state.plan
    for warning in plan.get("warnings", []):
        st.warning(warning)
    if plan.get("warnings"):
        st.caption("Update a conflicting task's time above, then generate the schedule again.")
    elif plan["scheduled_tasks"]:
        st.success("Schedule generated with no identical date and start-time conflicts.")
    st.write(f"Date: {plan['date']:%d/%m/%Y}")
    used, remaining = st.columns(2)
    used.metric("Scheduled time", f"{plan['total_duration']} min")
    remaining.metric("Remaining time", f"{plan['remaining_minutes']} min")

    st.write("Scheduled tasks")
    if plan["scheduled_tasks"]:
        st.table(task_rows([
            (entry["pet"], entry["task"]) for entry in plan["scheduled_tasks"]
        ]))
    else:
        st.info("No unfinished tasks fit the available time.")

    if plan["unscheduled_tasks"]:
        st.warning("These tasks did not fit the remaining time:")
        st.table(task_rows([
            (entry["pet"], entry["task"]) for entry in plan["unscheduled_tasks"]
        ]))

    st.write(plan["explanation"])
