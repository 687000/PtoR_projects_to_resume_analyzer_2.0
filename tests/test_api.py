import json
import pytest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

import src.store as store_module
from src.api import app

client = TestClient(app)

_PARSED_STUB = {
    "raw_text": "Built a Vue dashboard.",
    "source_type": "text_file",
    "metadata": {"filename": "project.txt"},
}

_ANALYSIS_STUB = {
    "title": "Vue Dashboard",
    "category": "web_app",
    "tags": ["vue_web"],
    "summary": "A Vue dashboard project.",
    "ownership_description": "Built the frontend.",
    "ownership_classification": {
        "background": "",
        "t1_contribution": "",
        "t2_contribution": "",
        "coordination": "",
        "outcome": "",
    },
    "technical_highlights": ["Built a dashboard"],
    "resume_bullets": ["Implemented Vue dashboard"],
    "interview_answer": "Situation: ...\nTask: ...\nAction: ...\nResult: ...",
    "self_intro": "Vue Dashboard",
    "talking_points": [],
    "context": {},
}


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store_path = tmp_path / "data" / "projects.json"
    monkeypatch.setattr(store_module, "STORE_PATH", store_path)


# ---------------------------------------------------------------------------
# POST /api/analyze/file — single file
# ---------------------------------------------------------------------------

def test_single_file_upload(tmp_path):
    f = tmp_path / "project.txt"
    f.write_text("Built a Vue dashboard.", encoding="utf-8")

    with patch("src.api.parse_input", return_value=_PARSED_STUB), \
         patch("src.api.analyze_project", return_value=_ANALYSIS_STUB):
        resp = client.post(
            "/api/analyze/file",
            files=[("files", ("project.txt", f.read_bytes(), "text/plain"))],
            data={"context": "{}"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Vue Dashboard"
    assert data["raw_text"] == "Built a Vue dashboard."


# ---------------------------------------------------------------------------
# POST /api/analyze/file — multiple files, texts concatenated
# ---------------------------------------------------------------------------

def test_multiple_files_texts_concatenated(tmp_path):
    stub_a = {**_PARSED_STUB, "raw_text": "Part A of the project."}
    stub_b = {**_PARSED_STUB, "raw_text": "Part B of the project.", "metadata": {"filename": "b.txt"}}

    captured = {}

    def fake_analyze(raw_text, ctx):
        captured["raw_text"] = raw_text
        return _ANALYSIS_STUB

    with patch("src.api.parse_input", side_effect=[stub_a, stub_b]), \
         patch("src.api.analyze_project", side_effect=fake_analyze):
        resp = client.post(
            "/api/analyze/file",
            files=[
                ("files", ("a.txt", b"Part A of the project.", "text/plain")),
                ("files", ("b.txt", b"Part B of the project.", "text/plain")),
            ],
            data={"context": "{}"},
        )

    assert resp.status_code == 200
    assert "Part A" in captured["raw_text"]
    assert "Part B" in captured["raw_text"]


def test_multiple_files_metadata_contains_list(tmp_path):
    stub_a = {**_PARSED_STUB, "raw_text": "A", "metadata": {"filename": "a.txt"}}
    stub_b = {**_PARSED_STUB, "raw_text": "B", "metadata": {"filename": "b.txt"}}

    with patch("src.api.parse_input", side_effect=[stub_a, stub_b]), \
         patch("src.api.analyze_project", return_value=_ANALYSIS_STUB):
        resp = client.post(
            "/api/analyze/file",
            files=[
                ("files", ("a.txt", b"A", "text/plain")),
                ("files", ("b.txt", b"B", "text/plain")),
            ],
            data={"context": "{}"},
        )

    assert resp.status_code == 200
    meta = resp.json()["source_metadata"]
    assert meta["count"] == 2
    assert len(meta["files"]) == 2


def test_single_file_metadata_stays_flat():
    with patch("src.api.parse_input", return_value=_PARSED_STUB), \
         patch("src.api.analyze_project", return_value=_ANALYSIS_STUB):
        resp = client.post(
            "/api/analyze/file",
            files=[("files", ("project.txt", b"Built a Vue dashboard.", "text/plain"))],
            data={"context": "{}"},
        )

    assert resp.status_code == 200
    meta = resp.json()["source_metadata"]
    assert "filename" in meta
    assert "count" not in meta


# ---------------------------------------------------------------------------
# POST /api/analyze/file — file size limit
# ---------------------------------------------------------------------------

def test_file_over_size_limit_returns_413():
    big_content = b"x" * (10 * 1024 * 1024 + 1)  # 10 MB + 1 byte
    resp = client.post(
        "/api/analyze/file",
        files=[("files", ("big.txt", big_content, "text/plain"))],
        data={"context": "{}"},
    )
    assert resp.status_code == 413


def test_size_limit_error_includes_filename():
    big_content = b"x" * (10 * 1024 * 1024 + 1)
    resp = client.post(
        "/api/analyze/file",
        files=[("files", ("oversized.pdf", big_content, "application/pdf"))],
        data={"context": "{}"},
    )
    assert resp.status_code == 413
    assert "oversized.pdf" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# POST /api/analyze/file — parse error includes filename
# ---------------------------------------------------------------------------

def test_parse_error_includes_filename():
    with patch("src.api.parse_input", side_effect=ValueError("bad format")):
        resp = client.post(
            "/api/analyze/file",
            files=[("files", ("broken.pdf", b"not a pdf", "application/pdf"))],
            data={"context": "{}"},
        )
    assert resp.status_code == 422
    assert "broken.pdf" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# POST /api/analyze — text/URL source
# ---------------------------------------------------------------------------

def test_analyze_text_source():
    with patch("src.api.parse_input", return_value=_PARSED_STUB), \
         patch("src.api.analyze_project", return_value=_ANALYSIS_STUB):
        resp = client.post(
            "/api/analyze",
            json={"source": "Built a Vue dashboard.", "context": {}},
        )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Vue Dashboard"


def test_analyze_invalid_source_returns_422():
    with patch("src.api.parse_input", side_effect=ValueError("Input text is empty.")):
        resp = client.post(
            "/api/analyze",
            json={"source": "", "context": {}},
        )
    assert resp.status_code == 422
