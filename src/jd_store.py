import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DATA_FILE = Path(__file__).parent.parent / "data" / "jd_targets.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> list:
    if not DATA_FILE.exists():
        return []
    text = DATA_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return json.loads(text)


def _save(targets: list) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(targets, indent=2, ensure_ascii=False), encoding="utf-8")


def list_jd_targets() -> list:
    return _load()


def get_jd_target(jd_id: str) -> Optional[dict]:
    for t in _load():
        if t.get("id") == jd_id:
            return t
    return None


def save_jd_target(target: dict) -> dict:
    targets = _load()
    now = _now()
    if not target.get("id"):
        target["id"] = str(uuid.uuid4())
    target.setdefault("created_at", now)
    target["updated_at"] = now
    targets.insert(0, target)
    _save(targets)
    return target


def update_jd_target(jd_id: str, updates: dict) -> Optional[dict]:
    targets = _load()
    for i, t in enumerate(targets):
        if t.get("id") == jd_id:
            t.update(updates)
            t["updated_at"] = _now()
            targets[i] = t
            _save(targets)
            return t
    return None


def delete_jd_target(jd_id: str) -> bool:
    targets = _load()
    new_list = [t for t in targets if t.get("id") != jd_id]
    if len(new_list) == len(targets):
        return False
    _save(new_list)
    return True
