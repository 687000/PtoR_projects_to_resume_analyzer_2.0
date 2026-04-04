import json
import pytest
from pathlib import Path

import src.store as store_module


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store_path = tmp_path / "data" / "projects.json"
    monkeypatch.setattr(store_module, "STORE_PATH", store_path)


def _make_project(**kwargs) -> dict:
    base = {"title": "Test Project", "category": "web_app", "tags": ["vue_web"]}
    base.update(kwargs)
    return base


def test_save_and_load():
    p = store_module.save_project(_make_project())
    assert "id" in p
    assert "created_at" in p
    projects = store_module.load_projects()
    assert len(projects) == 1
    assert projects[0]["id"] == p["id"]


def test_get_project():
    p = store_module.save_project(_make_project(title="Alpha"))
    found = store_module.get_project(p["id"])
    assert found is not None
    assert found["title"] == "Alpha"


def test_get_project_not_found():
    assert store_module.get_project("nonexistent-id") is None


def test_update_project():
    p = store_module.save_project(_make_project(title="Old Title"))
    updated = store_module.update_project(p["id"], {"title": "New Title"})
    assert updated["title"] == "New Title"
    assert updated["id"] == p["id"]
    assert "updated_at" in updated
    # Original fields preserved
    assert updated["category"] == "web_app"


def test_update_project_not_found():
    result = store_module.update_project("no-such-id", {"title": "X"})
    assert result is None


def test_delete_project():
    p = store_module.save_project(_make_project())
    deleted = store_module.delete_project(p["id"])
    assert deleted is True
    assert store_module.load_projects() == []


def test_delete_project_not_found():
    result = store_module.delete_project("no-such-id")
    assert result is False


def test_multiple_projects():
    ids = [store_module.save_project(_make_project(title=f"P{i}"))["id"] for i in range(3)]
    projects = store_module.load_projects()
    assert len(projects) == 3

    store_module.delete_project(ids[1])
    remaining = store_module.load_projects()
    assert len(remaining) == 2
    assert all(p["id"] != ids[1] for p in remaining)


def test_load_returns_empty_list_when_no_file():
    assert store_module.load_projects() == []
