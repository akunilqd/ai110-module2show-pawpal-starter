"""JSON save/load helpers; domain logic remains in the four backend classes."""

from datetime import date
import json
from pathlib import Path
import tempfile

from pawpal_system import Owner, Pet, Task


DATA_PATH = Path(__file__).resolve().parent / "data" / "pawpal.json"


def save_owner(owner: Owner, path: str | Path = DATA_PATH) -> None:
    """Atomically save owner details, pets, and complete task records as UTF-8 JSON."""
    payload = {
        "schema_version": 1,
        "owner": {
            "name": owner.name,
            "available_minutes": owner.available_minutes,
            "preferences": dict(owner.preferences),
            "pets": [
                {
                    "name": pet.name, "age_months": pet.age_months,
                    "species": pet.species, "care_needs": list(pet.care_needs),
                    "tasks": [
                        {
                            "task_id": task.task_id, "description": task.description,
                            "duration_minutes": task.duration_minutes,
                            "frequency": task.frequency, "priority": task.priority,
                            "completed": task.completed, "time": task.time,
                            "due_date": task.due_date.isoformat(),
                        }
                        for task in pet.tasks
                    ],
                }
                for pet in owner.pets
            ],
        },
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent,
            prefix=target.name + ".", suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(text + "\n")
        temporary_path.replace(target)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _record(value) -> dict:
    """Require a JSON object before reading its fields."""
    if not isinstance(value, dict):
        raise ValueError("Expected an object in saved data.")
    return value


def _text(value) -> str:
    """Require a string rather than silently coercing malformed saved fields."""
    if not isinstance(value, str):
        raise ValueError("Expected a text field in saved data.")
    return value


def _items(value) -> list:
    """Require a JSON list before iterating pets, tasks, or care needs."""
    if not isinstance(value, list):
        raise ValueError("Expected a list in saved data.")
    return value


def load_owner(path: str | Path = DATA_PATH) -> Owner:
    """Validate JSON and return a new Owner with restored pets, tasks, dates, and IDs."""
    payload = _record(json.loads(Path(path).read_text(encoding="utf-8")))
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported saved-data version.")
    try:
        data = _record(payload["owner"])
        owner = Owner(_text(data["name"]), data["available_minutes"])
        for key, value in _record(data["preferences"]).items():
            owner.update_preference(key, value)
        seen_ids = set()
        for pet_data in _items(data["pets"]):
            pet_data = _record(pet_data)
            pet = Pet(
                _text(pet_data["name"]), pet_data["age_months"], _text(pet_data["species"])
            )
            pet.update_care_needs([_text(need) for need in _items(pet_data["care_needs"])])
            for task_data in _items(pet_data["tasks"]):
                task_data = _record(task_data)
                task_id = _text(task_data["task_id"])
                if not task_id.strip() or task_id in seen_ids:
                    raise ValueError("Saved task IDs must be nonempty and unique.")
                task = Task(
                    _text(task_data["description"]), task_data["duration_minutes"],
                    _text(task_data["frequency"]), _text(task_data["priority"]),
                    task_data["completed"], task_data["time"],
                    date.fromisoformat(_text(task_data["due_date"])),
                )
                task.task_id = task_id
                seen_ids.add(task_id)
                pet.add_task(task)
            owner.add_pet(pet)
        return owner
    except (KeyError, TypeError) as error:
        raise ValueError("Saved data is missing required fields or has invalid types.") from error
