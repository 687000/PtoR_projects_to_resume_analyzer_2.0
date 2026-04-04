import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

STORE_PATH = Path("data/projects.json")


def load_projects() -> list[dict]:
    if not STORE_PATH.exists():
        return []
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_project(project: dict) -> dict:
    projects = load_projects()
    project["id"] = str(uuid.uuid4())
    project["created_at"] = datetime.now(timezone.utc).isoformat()
    projects.append(project)
    _write(projects)
    return project


def get_project(project_id: str) -> dict | None:
    return next((p for p in load_projects() if p["id"] == project_id), None)


def update_project(project_id: str, fields: dict) -> dict | None:
    projects = load_projects()
    for i, p in enumerate(projects):
        if p["id"] == project_id:
            projects[i] = {**p, **fields, "updated_at": datetime.now(timezone.utc).isoformat()}
            _write(projects)
            return projects[i]
    return None


def delete_project(project_id: str) -> bool:
    projects = load_projects()
    new_list = [p for p in projects if p["id"] != project_id]
    if len(new_list) == len(projects):
        return False
    _write(new_list)
    return True


def _write(projects: list[dict]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
