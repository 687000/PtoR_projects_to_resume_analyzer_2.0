import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

JD_STORE_PATH = Path("data/jd_targets.json")


def load_jd_targets() -> list[dict]:
    if not JD_STORE_PATH.exists():
        return []
    return json.loads(JD_STORE_PATH.read_text(encoding="utf-8"))


def save_jd_target(target: dict) -> dict:
    targets = load_jd_targets()
    target["id"] = str(uuid.uuid4())
    target["created_at"] = datetime.now(timezone.utc).isoformat()
    targets.append(target)
    _write(targets)
    return target


def get_jd_target(target_id: str) -> dict | None:
    return next((t for t in load_jd_targets() if t["id"] == target_id), None)


def update_jd_target(target_id: str, fields: dict) -> dict | None:
    targets = load_jd_targets()
    for i, t in enumerate(targets):
        if t["id"] == target_id:
            targets[i] = {
                **t,
                **fields,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            _write(targets)
            return targets[i]
    return None


def delete_jd_target(target_id: str) -> bool:
    targets = load_jd_targets()
    new_list = [t for t in targets if t["id"] != target_id]
    if len(new_list) == len(targets):
        return False
    _write(new_list)
    return True


def _write(targets: list[dict]) -> None:
    JD_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    JD_STORE_PATH.write_text(
        json.dumps(targets, indent=2, ensure_ascii=False), encoding="utf-8"
    )
