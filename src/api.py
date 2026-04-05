import json
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.analyzer import analyze_project
from src.jd_analyzer import analyze_jd, check_duplicate, improve_bullets
from src.parser import parse_input
import src.store as store_module
from src.store import (
    delete_project,
    get_project,
    load_projects,
    save_project,
    update_project,
)
import src.jd_store as jd_store_module
from src.jd_store import (
    delete_jd_target,
    get_jd_target,
    load_jd_targets,
    save_jd_target,
    update_jd_target,
)

# Resolve store paths relative to project root regardless of working directory
store_module.STORE_PATH = Path(__file__).parent.parent / "data" / "projects.json"
jd_store_module.JD_STORE_PATH = Path(__file__).parent.parent / "data" / "jd_targets.json"

app = FastAPI(title="Project-to-Resume Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


class Context(BaseModel):
    business_background: str = ""
    team_client_requirements: str = ""
    pm_decisions: str = ""
    t1_responsibilities: str = ""
    t2_responsibilities: str = ""
    architecture_details: str = ""
    coordination: str = ""
    challenges: str = ""
    outcomes: str = ""


class AnalyzeRequest(BaseModel):
    source: str
    context: Context


class SaveRequest(BaseModel):
    analysis: dict
    raw_text: str
    source_metadata: dict = {}


class PatchRequest(BaseModel):
    context: Context
    reanalyze: bool = False
    resume_bullets: list[str] | None = None


@app.get("/api/projects")
def list_projects_endpoint():
    return load_projects()


@app.get("/api/projects/{project_id}")
def get_project_endpoint(project_id: str):
    p = get_project(project_id)
    if not p:
        raise HTTPException(404, "Not found")
    return p


@app.post("/api/analyze")
def analyze_source(req: AnalyzeRequest):
    try:
        parsed = parse_input(req.source)
    except (ValueError, ImportError) as e:
        raise HTTPException(422, str(e))
    analysis = analyze_project(parsed["raw_text"], req.context.model_dump())
    return {
        **analysis,
        "raw_text": parsed["raw_text"],
        "source_metadata": parsed["metadata"],
    }


@app.post("/api/analyze/file")
async def analyze_file_endpoint(files: list[UploadFile] = File(...), context: str = "{}"):
    ctx = json.loads(context)
    all_texts: list[str] = []
    all_metadata: list[dict] = []

    for file in files:
        content = await file.read()
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(413, f"File '{file.filename}' exceeds 10 MB limit")

        suffix = Path(file.filename or "upload").suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            parsed = parse_input(tmp_path)
        except (ValueError, ImportError) as e:
            raise HTTPException(422, f"{file.filename}: {e}")
        finally:
            os.unlink(tmp_path)

        all_texts.append(parsed["raw_text"])
        all_metadata.append(parsed["metadata"])

    raw_text = "\n\n".join(all_texts)
    source_metadata = (
        all_metadata[0] if len(all_metadata) == 1
        else {"files": all_metadata, "count": len(all_metadata)}
    )

    analysis = analyze_project(raw_text, ctx)
    return {
        **analysis,
        "raw_text": raw_text,
        "source_metadata": source_metadata,
    }


@app.post("/api/projects")
def save_project_endpoint(req: SaveRequest):
    project = {
        **req.analysis,
        "raw_text": req.raw_text,
        "source_metadata": req.source_metadata,
    }
    return save_project(project)


@app.patch("/api/projects/{project_id}")
def patch_project_endpoint(project_id: str, req: PatchRequest):
    p = get_project(project_id)
    if not p:
        raise HTTPException(404, "Not found")

    if req.reanalyze:
        analysis = analyze_project(p.get("raw_text", ""), req.context.model_dump())
        updated = update_project(project_id, {**analysis, "context": req.context.model_dump()})
    else:
        patch_data: dict = {"context": req.context.model_dump()}
        if req.resume_bullets is not None:
            patch_data["resume_bullets"] = req.resume_bullets
        updated = update_project(project_id, patch_data)

    return updated


@app.delete("/api/projects/{project_id}")
def delete_project_endpoint(project_id: str):
    if not delete_project(project_id):
        raise HTTPException(404, "Not found")
    return {"ok": True}


# ---------------------------------------------------------------------------
# JD Target endpoints
# ---------------------------------------------------------------------------

class JDAnalyzeRequest(BaseModel):
    source: str


class JDSaveRequest(BaseModel):
    analysis: dict
    raw_jd_text: str
    source_metadata: dict = {}


class JDPatchRequest(BaseModel):
    # Re-run matching only — no JD re-parse needed
    # If project_ids is provided, only match against those projects
    project_ids: list[str] | None = None


@app.get("/api/jd-targets")
def list_jd_targets():
    return load_jd_targets()


@app.get("/api/jd-targets/{target_id}")
def get_jd_target_endpoint(target_id: str):
    t = get_jd_target(target_id)
    if not t:
        raise HTTPException(404, "Not found")
    return t


@app.post("/api/jd/analyze")
def analyze_jd_source(req: JDAnalyzeRequest):
    try:
        parsed = parse_input(req.source)
    except (ValueError, ImportError) as e:
        raise HTTPException(422, str(e))
    projects = load_projects()
    analysis = analyze_jd(parsed["raw_text"], projects)
    duplicate = check_duplicate(analysis["extracted_requirements"], load_jd_targets())
    return {
        **analysis,
        "raw_jd_text": parsed["raw_text"],
        "source_metadata": parsed["metadata"],
        "duplicate": duplicate,
    }


@app.post("/api/jd/analyze/file")
async def analyze_jd_file(file: UploadFile, _: str = "{}"):
    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(413, "File exceeds 10 MB limit")

    suffix = Path(file.filename or "upload").suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parsed = parse_input(tmp_path)
    except (ValueError, ImportError) as e:
        raise HTTPException(422, str(e))
    finally:
        os.unlink(tmp_path)

    projects = load_projects()
    analysis = analyze_jd(parsed["raw_text"], projects)
    duplicate = check_duplicate(analysis["extracted_requirements"], load_jd_targets())
    return {
        **analysis,
        "raw_jd_text": parsed["raw_text"],
        "source_metadata": {"filename": file.filename},
        "duplicate": duplicate,
    }


@app.post("/api/jd-targets")
def save_jd_target_endpoint(req: JDSaveRequest):
    target = {
        **req.analysis,
        "raw_jd_text": req.raw_jd_text,
        "source_metadata": req.source_metadata,
    }
    return save_jd_target(target)


@app.patch("/api/jd-targets/{target_id}")
def rematch_jd_target(target_id: str, req: JDPatchRequest = JDPatchRequest()):
    """Re-run matching against the current project pool, optionally filtered by project_ids."""
    t = get_jd_target(target_id)
    if not t:
        raise HTTPException(404, "Not found")
    projects = load_projects()
    if req.project_ids is not None:
        allowed = set(req.project_ids)
        projects = [p for p in projects if p.get("id") in allowed]
    analysis = analyze_jd(t["raw_jd_text"], projects)
    updated = update_jd_target(
        target_id,
        {
            "extracted_requirements": analysis["extracted_requirements"],
            "matched_projects": analysis["matched_projects"],
        },
    )
    return updated


class ImproveBulletsRequest(BaseModel):
    bullets: list[str]


@app.post("/api/jd-targets/{target_id}/improve-bullets")
def improve_bullets_endpoint(target_id: str, req: ImproveBulletsRequest):
    t = get_jd_target(target_id)
    if not t:
        raise HTTPException(404, "Not found")
    return improve_bullets(req.bullets, t.get("raw_jd_text", ""))


@app.patch("/api/jd-targets/{target_id}/bullets")
def update_jd_bullets(target_id: str, payload: dict):
    """Persist bullet edits (included toggle, text edits, reorder) from the frontend."""
    t = get_jd_target(target_id)
    if not t:
        raise HTTPException(404, "Not found")
    updated = update_jd_target(target_id, {"matched_projects": payload["matched_projects"]})
    return updated


@app.delete("/api/jd-targets/{target_id}")
def delete_jd_target_endpoint(target_id: str):
    if not delete_jd_target(target_id):
        raise HTTPException(404, "Not found")
    return {"ok": True}
