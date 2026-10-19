"""Verify persistence across independent save/load calls and malformed data."""

from datetime import date
import json

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task
from storage import load_owner, save_owner


def sample_owner():
    owner = Owner("Khoa", 75)
    owner.update_preference("prefer_short_tasks", True)
    for name, species in (("Niki", "dog"), ("Mochi \u732b", "cat")):
        pet = Pet(name, 12, species)
        pet.update_care_needs(["Daily exercise"])
        pet.add_task(Task("Feeding", 10, time="08:00", due_date=date(2026, 10, 19)))
        owner.add_pet(pet)
    Scheduler(owner).mark_task_complete(owner.pets[0].tasks[0].task_id, date(2026, 10, 19))
    return owner


def test_json_round_trip_preserves_all_data_and_recurring_state(tmp_path):
    owner = sample_owner()
    path = tmp_path / "data" / "pawpal.json"
    save_owner(owner, path)
    restored = load_owner(path)
    copy_path = tmp_path / "copy.json"
    save_owner(restored, copy_path)
    assert json.loads(path.read_text(encoding="utf-8")) == json.loads(copy_path.read_text(encoding="utf-8"))
    assert restored is not owner
    assert restored.pets[0] is not owner.pets[0]
    assert len(restored.pets) == 2
    assert len(restored.get_all_tasks()) == 3
    completed = restored.pets[0].tasks[0]
    assert Scheduler(restored).mark_task_complete(completed.task_id) is None
    assert len(restored.pets[0].tasks) == 2
    assert list(path.parent.glob("*.tmp")) == []


def test_save_can_replace_an_existing_file(tmp_path):
    path = tmp_path / "pawpal.json"
    save_owner(sample_owner(), path)
    save_owner(Owner("New owner", 20), path)
    assert load_owner(path).name == "New owner"
    assert load_owner(path).pets == []


@pytest.mark.parametrize("contents", ["not JSON", "[]", "{}", '{"schema_version": 2}',
                                        '{"schema_version": 1, "owner": {}}'])
def test_invalid_saved_data_is_rejected(tmp_path, contents):
    path = tmp_path / "bad.json"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(ValueError):
        load_owner(path)


@pytest.mark.parametrize("field,value", [
    ("duration_minutes", -1), ("completed", "yes"), ("due_date", "invalid"),
    ("description", 123), ("time", "25:00"), ("task_id", ""),
])
def test_invalid_task_fields_are_rejected(tmp_path, field, value):
    path = tmp_path / "pawpal.json"
    save_owner(sample_owner(), path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["owner"]["pets"][0]["tasks"][0][field] = value
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_owner(path)


def test_duplicate_ids_are_rejected_and_missing_files_report_errors(tmp_path):
    path = tmp_path / "pawpal.json"
    with pytest.raises(FileNotFoundError):
        load_owner(path)
    save_owner(sample_owner(), path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["owner"]["pets"][1]["tasks"][0]["task_id"] = data["owner"]["pets"][0]["tasks"][0]["task_id"]
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        load_owner(path)
