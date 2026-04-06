import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DATA_FILE = Path(__file__).parent.parent / "data" / "projects.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> list:
    if not DATA_FILE.exists():
        return []
    text = DATA_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return json.loads(text)


def _save(projects: list) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")


def list_projects() -> list:
    return _load()


def get_project(project_id: str) -> Optional[dict]:
    for p in _load():
        if p.get("id") == project_id:
            return p
    return None


def save_project(project: dict) -> dict:
    projects = _load()
    now = _now()
    if not project.get("id"):
        project["id"] = str(uuid.uuid4())
    project.setdefault("created_at", now)
    project["updated_at"] = now
    projects.insert(0, project)
    _save(projects)
    return project


def update_project(project_id: str, updates: dict) -> Optional[dict]:
    projects = _load()
    for i, p in enumerate(projects):
        if p.get("id") == project_id:
            p.update(updates)
            p["updated_at"] = _now()
            projects[i] = p
            _save(projects)
            return p
    return None


def delete_project(project_id: str) -> bool:
    projects = _load()
    new_list = [p for p in projects if p.get("id") != project_id]
    if len(new_list) == len(projects):
        return False
    _save(new_list)
    return True
