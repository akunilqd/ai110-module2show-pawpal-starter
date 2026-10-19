"""Exercise the UI's session state and multi-pet planning workflow."""

from pathlib import Path
from datetime import date, timedelta

from streamlit.testing.v1 import AppTest


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
