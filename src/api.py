import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src import services, store, jd_store

app = FastAPI(title="PtoR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


# ── Pydantic models ───────────────────────────────────────────────────────────

class ContextBackground(BaseModel):
    business_background: str = ""
    team_client_requirements: str = ""
    pm_product_decisions: str = ""


class ContextContributions(BaseModel):
    t1_responsibilities: str = ""
    t2_responsibilities: str = ""
    architecture_details: str = ""
    cross_functional_coordination: str = ""
    challenges_constraints_tradeoffs: str = ""
    outcomes_impact: str = ""


class ProjectContext(BaseModel):
    background: ContextBackground = ContextBackground()
    contributions: ContextContributions = ContextContributions()


class AnalyzeTextRequest(BaseModel):
    text: str = ""
    url: str = ""
    notion_url: str = ""
    context: ProjectContext = ProjectContext()


class SaveProjectRequest(BaseModel):
    source: dict
    context: dict
    analysis: dict


class UpdateProjectRequest(BaseModel):
    context: Optional[dict] = None
    resume_bullets: Optional[list] = None
    title: Optional[str] = None
    reanalyze: bool = False


class AnalyzeJDRequest(BaseModel):
    text: str = ""
    url: str = ""


class SaveJDRequest(BaseModel):
    jd: dict
    save_and_match: bool = True


class RewriteBulletsRequest(BaseModel):
    bullets: list


class UpdateJDRequest(BaseModel):
    extracted_requirements: Optional[dict] = None
    title: Optional[str] = None
    match_results: Optional[dict] = None


# ── Project endpoints ─────────────────────────────────────────────────────────

@app.get("/api/projects")
def list_projects():
    return store.list_projects()


@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@app.post("/api/analyze")
def analyze_project(req: AnalyzeTextRequest):
    ctx = req.context.model_dump()
    try:
        if req.notion_url:
            return services.analyze_project_notion(req.notion_url, ctx)
        if req.url:
            return services.analyze_project_url(req.url, ctx)
        if req.text:
            from src import parser, analyzer
            source = parser.parse_text(req.text)
            result = analyzer.analyze_project(source, ctx)
            return {"source": source, **result}
        raise HTTPException(400, "Provide text, url, or notion_url")
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/analyze/file")
async def analyze_project_file(
    files: List[UploadFile] = File(...),
    context: str = Form(default="{}")
):
    import json
    try:
        ctx = json.loads(context)
    except Exception:
        ctx = {}

    tmp_paths = []
    try:
        for file in files:
            suffix = Path(file.filename).suffix.lower()
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(await file.read())
                tmp_paths.append((tmp.name, file.filename))

        from src import parser, analyzer
        paths = [p for p, _ in tmp_paths]
        source = parser.parse_files(paths)
        source["source_reference"] = ", ".join(fn for _, fn in tmp_paths)
        result = analyzer.analyze_project(source, ctx)
        return {"source": source, **result}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        for p, _ in tmp_paths:
            os.unlink(p)


@app.post("/api/projects")
def save_project(req: SaveProjectRequest):
    try:
        return services.save_analyzed_project(req.source, req.context, req.analysis)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.patch("/api/projects/{project_id}")
def update_project(project_id: str, req: UpdateProjectRequest):
    updates = {}
    if req.title is not None:
        updates["title"] = req.title
    if req.resume_bullets is not None:
        project = store.get_project(project_id)
        if not project:
            raise HTTPException(404, "Project not found")
        analysis = project.get("analysis", {})
        analysis["resume_bullets"] = req.resume_bullets
        updates["analysis"] = analysis
    if req.context is not None:
        if req.reanalyze:
            try:
                return services.update_project_context(project_id, req.context, reanalyze=True)
            except ValueError as e:
                raise HTTPException(404, str(e))
        else:
            updates["context"] = req.context
    if not updates:
        raise HTTPException(400, "No updates provided")
    result = store.update_project(project_id, updates)
    if not result:
        raise HTTPException(404, "Project not found")
    return result


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    if not store.delete_project(project_id):
        raise HTTPException(404, "Project not found")
    return {"deleted": project_id}


# ── JD endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/jd-targets")
def list_jd_targets():
    return jd_store.list_jd_targets()


@app.get("/api/jd-targets/{jd_id}")
def get_jd_target(jd_id: str):
    target = jd_store.get_jd_target(jd_id)
    if not target:
        raise HTTPException(404, "JD target not found")
    return target


@app.post("/api/jd/analyze")
def analyze_jd(req: AnalyzeJDRequest):
    try:
        if req.url:
            result = services.analyze_jd_url(req.url)
        elif req.text:
            result = services.analyze_jd_text(req.text)
        else:
            raise HTTPException(400, "Provide text or url")
        dup = services.check_jd_duplicate(result)
        return {"jd": result, "duplicate_check": dup}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/jd/analyze/file")
async def analyze_jd_file(files: List[UploadFile] = File(...)):
    tmp_paths = []
    try:
        for file in files:
            suffix = Path(file.filename).suffix.lower()
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(await file.read())
                tmp_paths.append(tmp.name)
        from src import parser, jd_analyzer
        source = parser.parse_files(tmp_paths)
        result = jd_analyzer.analyze_jd(source)
        dup = services.check_jd_duplicate(result)
        return {"jd": result, "duplicate_check": dup}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        for p in tmp_paths:
            os.unlink(p)


@app.post("/api/jd/match")
def match_jd(jd: dict):
    try:
        return services.run_matching(jd)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/jd-targets")
def save_jd_target(req: SaveJDRequest):
    try:
        if req.save_and_match:
            return services.save_jd_with_matching(req.jd)
        return jd_store.save_jd_target(req.jd)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/jd-targets/{jd_id}/rematch")
def rematch_jd(jd_id: str):
    try:
        return services.rematch_jd(jd_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.patch("/api/jd-targets/{jd_id}")
def update_jd_target(jd_id: str, req: UpdateJDRequest):
    updates = {}
    if req.title is not None:
        updates["title"] = req.title
    if req.extracted_requirements is not None:
        updates["extracted_requirements"] = req.extracted_requirements
    if req.match_results is not None:
        updates["match_results"] = req.match_results
    if not updates:
        raise HTTPException(400, "No updates provided")
    result = jd_store.update_jd_target(jd_id, updates)
    if not result:
        raise HTTPException(404, "JD target not found")
    return result


@app.delete("/api/jd-targets/{jd_id}")
def delete_jd_target(jd_id: str):
    if not jd_store.delete_jd_target(jd_id):
        raise HTTPException(404, "JD target not found")
    return {"deleted": jd_id}


@app.post("/api/jd/{jd_id}/rewrite-bullets")
def rewrite_bullets(jd_id: str, req: RewriteBulletsRequest):
    try:
        return services.rewrite_selected_bullets(jd_id, req.bullets)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Serve frontend ────────────────────────────────────────────────────────────

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{path:path}", include_in_schema=False)
    def serve_frontend(path: str = ""):
        index = FRONTEND_DIST / "index.html"
        if index.exists():
            return FileResponse(str(index))
        raise HTTPException(404, "Frontend not built. Run: cd frontend && npm run build")
