"""Application services layer — orchestrates multi-step workflows."""
import re
from src import parser, analyzer, jd_analyzer, matcher, store, jd_store


# ── Project workflow ──────────────────────────────────────────────────────────

def analyze_project_text(text: str, context: dict) -> dict:
    source = parser.parse_text(text)
    return analyzer.analyze_project(source, context)


def analyze_project_url(url: str, context: dict) -> dict:
    source = parser.parse_url(url)
    return analyzer.analyze_project(source, context)


def analyze_project_notion(url: str, context: dict, notion_token: str = None) -> dict:
    source = parser.parse_notion(url, token=notion_token)
    return analyzer.analyze_project(source, context)


def analyze_project_file(path: str, context: dict) -> dict:
    source = parser.parse_file(path)
    return analyzer.analyze_project(source, context)


def save_analyzed_project(source: dict, context: dict, analysis_result: dict) -> dict:
    project = {
        "title": analysis_result.get("title", "Untitled Project"),
        "category": analysis_result.get("category", "other"),
        "tags": analysis_result.get("tags", []),
        "source": {
            "source_type": source.get("source_type", "text"),
            "raw_text": source.get("raw_text", ""),
            "source_reference": source.get("source_reference", ""),
        },
        "context": context,
        "analysis": analysis_result.get("analysis", {}),
        "role_versions": {},
    }
    return store.save_project(project)


def upload_and_analyze_text(text: str, context: dict) -> dict:
    source = parser.parse_text(text)
    result = analyzer.analyze_project(source, context)
    return save_analyzed_project(source, context, result)


def update_project_context(project_id: str, context: dict, reanalyze: bool = True) -> dict:
    project = store.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")
    updates = {"context": context}
    if reanalyze:
        source = project.get("source", {})
        result = analyzer.analyze_project(source, context)
        updates["analysis"] = result.get("analysis", {})
        updates["title"] = result.get("title", project.get("title", ""))
        updates["category"] = result.get("category", project.get("category", "other"))
        updates["tags"] = result.get("tags", project.get("tags", []))
    return store.update_project(project_id, updates)


# ── JD workflow ───────────────────────────────────────────────────────────────

def analyze_jd_text(text: str) -> dict:
    source = parser.parse_text(text)
    return jd_analyzer.analyze_jd(source)


def analyze_jd_url(url: str) -> dict:
    source = parser.parse_url(url)
    return jd_analyzer.analyze_jd(source)


def analyze_jd_file(path: str) -> dict:
    source = parser.parse_file(path)
    return jd_analyzer.analyze_jd(source)


def check_jd_duplicate(new_jd: dict) -> dict:
    """Compare new JD against existing targets. Returns {is_duplicate, similar_id, similarity}."""
    existing = jd_store.list_jd_targets()
    if not existing:
        return {"is_duplicate": False, "similar_id": None, "similarity": 0.0, "similar_title": None}

    new_tech = set(t.lower() for t in new_jd.get("extracted_requirements", {}).get("tech_stack", []))
    new_domain = set(d.lower() for d in new_jd.get("extracted_requirements", {}).get("domain", []))
    new_collab = set(c.lower() for c in new_jd.get("extracted_requirements", {}).get("collaboration", []))
    new_set = new_tech | new_domain | new_collab

    best_sim = 0.0
    best_id = None
    best_title = None

    for ex in existing:
        ex_tech = set(t.lower() for t in ex.get("extracted_requirements", {}).get("tech_stack", []))
        ex_domain = set(d.lower() for d in ex.get("extracted_requirements", {}).get("domain", []))
        ex_collab = set(c.lower() for c in ex.get("extracted_requirements", {}).get("collaboration", []))
        ex_set = ex_tech | ex_domain | ex_collab

        if not new_set or not ex_set:
            continue
        intersection = len(new_set & ex_set)
        union = len(new_set | ex_set)
        sim = intersection / union if union > 0 else 0.0
        if sim > best_sim:
            best_sim = sim
            best_id = ex["id"]
            best_title = ex.get("title", "")

    return {
        "is_duplicate": best_sim >= 0.70,
        "similar_id": best_id if best_sim >= 0.70 else None,
        "similarity": best_sim,
        "similar_title": best_title if best_sim >= 0.70 else None,
    }


def run_matching(jd_target: dict) -> dict:
    projects = store.list_projects()
    return matcher.match_jd_against_projects(jd_target, projects)


def save_jd_with_matching(jd_target: dict) -> dict:
    match_result = run_matching(jd_target)
    jd_target["match_results"] = {"projects": match_result["matched_projects"]}
    jd_target["seniority_fit"] = match_result.get("seniority_fit")
    jd_target["seniority_fit_reason"] = match_result.get("seniority_fit_reason")
    return jd_store.save_jd_target(jd_target)


def rematch_jd(jd_id: str) -> dict:
    jd_target = jd_store.get_jd_target(jd_id)
    if not jd_target:
        raise ValueError(f"JD target {jd_id} not found")
    match_result = run_matching(jd_target)
    updates = {
        "match_results": {"projects": match_result["matched_projects"]},
        "seniority_fit": match_result.get("seniority_fit"),
        "seniority_fit_reason": match_result.get("seniority_fit_reason"),
    }
    return jd_store.update_jd_target(jd_id, updates)


def rewrite_selected_bullets(jd_id: str, bullets: list) -> dict:
    jd_target = jd_store.get_jd_target(jd_id)
    if not jd_target:
        raise ValueError(f"JD target {jd_id} not found")
    return matcher.rewrite_selected_bullets(jd_target, bullets)
