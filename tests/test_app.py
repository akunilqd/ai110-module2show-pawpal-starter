"""Exercise the UI's session state and multi-pet planning workflow."""

from pathlib import Path
from datetime import date, timedelta

from streamlit.testing.v1 import AppTest

from pawpal_system import Owner, Pet, Task
import storage


APP = Path(__file__).resolve().parents[1] / "app.py"


def submit(app, label):
    """Click a button by label and rerun the simulated app."""
    next(button for button in app.button if button.label == label).click().run()
    assert not app.exception


def test_multi_pet_schedule_and_session_persistence():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert not app.exception
    assert next(b for b in app.button if b.label == "Generate schedule").disabled

    for name in ("Niki", "Skibidi"):
        app.text_input(key="pet_name").set_value(name)
        submit(app, "Add pet")

    for pet_index, title, duration, priority in (
        (0, "Walk", 30, "medium"),
        (1, "Feeding", 10, "high"),
        (1, "Brushing", 20, "low"),
    ):
        app.selectbox(key="task_pet").set_value(pet_index)
        app.text_input(key="task_title").set_value(title)
        app.number_input(key="duration").set_value(duration)
        app.selectbox(key="priority").set_value(priority)
        submit(app, "Add task")

    submit(app, "Generate schedule")
    plan = app.session_state["plan"]
    assert [e["pet"].name for e in plan["scheduled_tasks"]] == ["Skibidi", "Niki"]
    assert plan["total_duration"] == 40
    assert plan["unscheduled_tasks"][0]["task"].description == "Brushing"

    app.run()
    assert not app.exception
    assert len(app.session_state["owner"].pets) == 2
    assert len(app.session_state["owner"].get_all_tasks()) == 3
    assert app.session_state["plan"]["total_duration"] == 40

    app.number_input(key="available_minutes").set_value(0)
    submit(app, "Save settings")
    assert "plan" not in app.session_state
    submit(app, "Generate schedule")
    assert app.session_state["plan"]["scheduled_tasks"] == []
    assert len(app.session_state["plan"]["unscheduled_tasks"]) == 3


def test_empty_inputs_show_errors_without_creating_objects():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    submit(app, "Add pet")
    assert app.error
    assert app.session_state["owner"].pets == []

    app.text_input(key="pet_name").set_value("Mochi")
    submit(app, "Add pet")
    submit(app, "Add task")
    assert app.error
    assert app.session_state["owner"].get_all_tasks() == []

    app.text_input(key="owner_name").set_value("   ")
    submit(app, "Save settings")
    assert app.error
    assert app.session_state["owner"].name == "Khoa"


def test_completing_weekly_task_adds_followup_and_invalidates_plan():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    app.text_input(key="pet_name").set_value("Niki")
    submit(app, "Add pet")
    app.text_input(key="task_title").set_value("Brushing")
    app.text_input(key="frequency").set_value("weekly")
    submit(app, "Add task")
    submit(app, "Generate schedule")
    assert len(app.session_state["plan"]["scheduled_tasks"]) == 1

    submit(app, "Mark complete")
    tasks = app.session_state["owner"].pets[0].tasks
    assert len(tasks) == 2
    assert tasks[0].completed is True
    assert tasks[1].completed is False
    assert tasks[1].due_date == date.today() + timedelta(days=7)
    assert "plan" not in app.session_state

    app.run()
    assert not app.exception
    assert len(app.session_state["owner"].pets[0].tasks) == 2
    submit(app, "Generate schedule")
    assert app.session_state["plan"]["scheduled_tasks"] == []


def test_overview_sorting_and_filters_use_all_pets():
    owner = Owner("Khoa", 60)
    dog, cat = Pet("Niki", 12), Pet("Skibidi", 6)
    dog.add_task(Task("Walk", 20, time="18:00", priority="low"))
    dog.add_task(Task("Done feeding", 10, time="08:00", completed=True))
    cat.add_task(Task("Brushing", 10, time="12:00", priority="high"))
    cat.add_task(Task("Tomorrow", 10, time="07:00", due_date=date.today() + timedelta(days=1)))
    owner.add_pet(dog)
    owner.add_pet(cat)
    app = AppTest.from_file(str(APP), default_timeout=15)
    app.session_state["owner"] = owner
    app.run()
    assert not app.exception
    assert app.table[-1].value["Task"].tolist() == [
        "Tomorrow", "Done feeding", "Brushing", "Walk",
    ]

    app.selectbox(key="status_filter").set_value("Pending")
    app.checkbox(key="due_only").check().run()
    assert app.table[-1].value["Task"].tolist() == ["Brushing", "Walk"]
    app.selectbox(key="pet_filter").set_value("Niki").run()
    assert app.table[-1].value["Task"].tolist() == ["Walk"]

    app.selectbox(key="pet_filter").set_value("All pets")
    app.selectbox(key="sort_order").set_value("Priority").run()
    assert app.table[-1].value["Task"].tolist() == ["Brushing", "Walk"]
    assert len(owner.get_all_tasks()) == 4


def test_conflict_warning_can_be_resolved_by_editing_time():
    owner = Owner("Khoa", 60)
    for name, description in (("Niki", "Walk"), ("Skibidi", "Feeding")):
        pet = Pet(name, 12)
        pet.add_task(Task(description, 10, time="08:00"))
        owner.add_pet(pet)
    app = AppTest.from_file(str(APP), default_timeout=15)
    app.session_state["owner"] = owner
    app.run()
    assert not app.exception
    warning = app.warning[0].value
    assert all(text in warning for text in ("08:00", "Niki", "Skibidi", "Walk", "Feeding"))
    assert any("Change one start time" in item.value for item in app.info)
    submit(app, "Generate schedule")
    assert len(app.session_state["plan"]["warnings"]) == 1

    task = owner.pets[0].tasks[0]
    app.text_input(key=f"edit_time_{task.task_id}").set_value("09:00")
    submit(app, "Update task time")
    assert task.time == "09:00"
    assert "plan" not in app.session_state
    assert not app.warning
    submit(app, "Generate schedule")
    assert app.session_state["plan"]["warnings"] == []
    assert len(app.session_state["plan"]["scheduled_tasks"]) == 2
    assert app.success


def test_suggested_time_can_be_applied_without_overlapping_other_pet():
    owner = Owner("Khoa", 60)
    for name in ("Niki", "Skibidi"):
        pet = Pet(name, 12)
        pet.add_task(Task("Care", 10, time="08:00"))
        owner.add_pet(pet)
    app = AppTest.from_file(str(APP), default_timeout=15)
    app.session_state["owner"] = owner
    app.run()
    submit(app, "Suggest next available time")
    task = owner.pets[0].tasks[0]
    assert app.text_input(key=f"edit_time_{task.task_id}").value == "08:10"
    assert task.time == "08:00"
    submit(app, "Update task time")
    assert task.time == "08:10"
    assert not app.warning


def test_save_and_load_restore_data_in_a_new_app_session(tmp_path, monkeypatch):
    path = tmp_path / "pawpal.json"
    monkeypatch.setattr(storage, "DATA_PATH", path)
    owner = Owner("Saved owner", 25)
    pet = Pet("Niki", 12)
    pet.add_task(Task("Feeding", 10))
    owner.add_pet(pet)
    app = AppTest.from_file(str(APP), default_timeout=15)
    app.session_state["owner"] = owner
    app.run()
    submit(app, "Save data")
    assert path.exists()

    restored_app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert restored_app.session_state["owner"].pets == []
    submit(restored_app, "Load data")
    restored = restored_app.session_state["owner"]
    assert restored.name == "Saved owner"
    assert restored_app.text_input(key="owner_name").value == "Saved owner"
    assert len(restored.get_all_tasks()) == 1
    assert restored.pets[0].tasks[0].task_id == pet.tasks[0].task_id


def test_loading_missing_file_keeps_current_owner(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_PATH", tmp_path / "missing.json")
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    owner = app.session_state["owner"]
    submit(app, "Load data")
    assert app.error
    assert app.session_state["owner"] is owner
