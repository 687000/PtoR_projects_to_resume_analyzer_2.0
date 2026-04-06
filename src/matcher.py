import json
from pathlib import Path
from src.ai.client import complete_json

PROFILE_FILE = Path(__file__).parent.parent / "data" / "user_profile.json"

LEVEL_ORDER = ["junior", "mid", "mid-senior", "senior", "lead", "principal"]


def _load_profile() -> dict:
    if PROFILE_FILE.exists():
        return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    return {"years_of_experience": 0, "self_described_level": "mid", "education": [], "notes": ""}


def _compute_seniority_fit(profile: dict, seniority_req: dict) -> tuple:
    expected = seniority_req.get("expected_level", "not_stated")
    min_years = seniority_req.get("min_years")
    yoe = profile.get("years_of_experience", 0)
    level = profile.get("self_described_level", "mid")

    if expected == "not_stated":
        return "meets", "JD has no explicit seniority requirement."

    level_idx = LEVEL_ORDER.index(level) if level in LEVEL_ORDER else 2
    exp_idx = LEVEL_ORDER.index(expected) if expected in LEVEL_ORDER else 2

    years_ok = min_years is None or yoe >= min_years
    years_close = min_years is not None and (min_years - yoe) <= 1
    level_ok = level_idx >= exp_idx
    level_close = (exp_idx - level_idx) == 1

    if years_ok and level_ok:
        return "meets", f"Candidate has {yoe} YoE and is {level}-level, meeting requirements."
    if years_close or level_close:
        return "partial", f"Candidate has {yoe} YoE ({level}-level); JD expects {expected} with {min_years}+ years."
    return "below", f"Candidate has {yoe} YoE ({level}-level); JD expects {expected} with {min_years}+ years."


def _collect_all_bullets(project: dict) -> list:
    """Return all bullets for a project as list of {text, source}."""
    analysis = project.get("analysis", {})
    bullets = []
    sb = analysis.get("summary_bullet", "")
    if sb:
        bullets.append({"text": sb, "source": "summary_bullet"})
    for i, b in enumerate(analysis.get("resume_bullets", [])):
        if b:
            bullets.append({"text": b, "source": f"resume_bullets[{i}]"})
    return bullets


def _score_fallback(project: dict, jd_req: dict) -> dict:
    analysis = project.get("analysis", {})
    tags = set(t.lower() for t in project.get("tags", []))
    category = project.get("category", "other")

    jd_tech = set(t.lower() for t in jd_req.get("tech_stack", []))
    jd_domain = set(d.lower() for d in jd_req.get("domain", []))
    jd_collab = set(c.lower() for c in jd_req.get("collaboration", []))

    combined_text = (
        " ".join(analysis.get("resume_bullets", []))
        + " " + " ".join(analysis.get("technical_highlights", []))
        + " " + analysis.get("summary_bullet", "")
        + " " + " ".join(tags)
        + " " + project.get("source", {}).get("raw_text", "")[:1000]
    ).lower()

    tech_hits = sum(1 for t in jd_tech if t in combined_text)
    tech_score = min(100, int(tech_hits / max(len(jd_tech), 1) * 100)) if jd_tech else 50

    domain_score = 100 if category in jd_domain else (
        50 if any(d in category for d in jd_domain) else 20
    )

    collab_hits = sum(1 for c in jd_collab if c in combined_text)
    collab_score = min(100, int(collab_hits / max(len(jd_collab), 1) * 100)) if jd_collab else 50

    fit_score = int(tech_score * 0.5 + domain_score * 0.3 + collab_score * 0.2)

    addressed = []
    if tech_score >= 40:
        addressed.extend(list(jd_tech)[:3])
    if domain_score >= 50:
        addressed.extend(list(jd_domain)[:2])

    # Include ALL bullets; select top ones based on fit score
    all_bullets = _collect_all_bullets(project)
    tailored_bullets = []
    for i, b in enumerate(all_bullets):
        # Select summary_bullet and first resume_bullet if fit is good enough
        included = fit_score >= 45 and (i == 0 or (fit_score >= 70 and i == 1))
        tailored_bullets.append({
            "bullet": b["text"],
            "included": included,
            "source": "selected",
            "addresses": ["tech_stack"],
            "source_references": [b["source"]],
            "reasoning": "Auto-selected based on fit score",
            "order": i,
        })

    return {
        "project_id": project["id"],
        "project_title": project.get("title", ""),
        "fit_score": fit_score,
        "fit_reason": f"Tech overlap: {tech_score}%, domain: {domain_score}%, collaboration: {collab_score}%",
        "addressed_requirements": addressed,
        "tailored_bullets": tailored_bullets,
        "score_breakdown": {
            "tech_stack_overlap": tech_score,
            "domain_relevance": domain_score,
            "collaboration_signals": collab_score,
        },
    }


def _build_match_prompt(profile: dict, jd_req: dict, seniority_fit: str, seniority_reason: str, projects: list) -> str:
    projects_block = []
    for p in projects:
        all_bullets = _collect_all_bullets(p)
        bullets_str = "\n".join(
            f"  [{i}] ({b['source']}) {b['text']}"
            for i, b in enumerate(all_bullets)
        )
        projects_block.append(f"""project_id: {p["id"]}
title: {p.get("title", "")}
category: {p.get("category", "")}
tags: {", ".join(p.get("tags", []))}
all_bullets:
{bullets_str or "  (none)"}""")

    education_str = "; ".join(f"{e.get('degree')} in {e.get('field')}" for e in profile.get("education", []))

    return f"""You are a senior resume editor helping a software engineer select the most relevant resume bullets for a job application.

## Candidate Profile
- Years of experience: {profile.get("years_of_experience", 0)}
- Self-described level: {profile.get("self_described_level", "mid")}
- Education: {education_str}
- Notes: {profile.get("notes", "")}

## Seniority Fit
The candidate's profile has been evaluated: {seniority_fit}
({seniority_reason})

## Job Requirements
- Tech stack: {", ".join(jd_req.get("tech_stack", []))}
- Domain: {", ".join(jd_req.get("domain", []))}
- Collaboration signals: {", ".join(jd_req.get("collaboration", []))}
- Seniority expected: {jd_req.get("seniority_requirement", {}).get("expected_level", "not_stated")} (min {jd_req.get("seniority_requirement", {}).get("min_years")} years)

## Candidate Projects
{chr(10).join(projects_block)}

## Task
For each project, assess fit and decide which bullets to include.
Return ONLY valid JSON:
{{
  "seniority_fit": "{seniority_fit}",
  "seniority_fit_reason": "{seniority_reason}",
  "matched_projects": [
    {{
      "project_id": "string",
      "project_title": "string",
      "fit_score": 0,
      "fit_reason": "string",
      "addressed_requirements": ["string"],
      "included_bullet_indices": [0, 1]
    }}
  ]
}}

Rules:
- fit_score 0-100 based on tech + domain + collaboration only (not seniority)
- Only projects with fit_score >= 45 should appear in matched_projects
- included_bullet_indices: indices from the all_bullets list above that should be pre-selected
- summary_bullet (index 0) has higher weight — prefer including it when relevant
- Select at most 2 bullets per project unless all three dimensions are satisfied
- Sort by fit_score descending"""


def match_jd_against_projects(jd_target: dict, projects: list) -> dict:
    if not projects:
        return {"seniority_fit": "meets", "seniority_fit_reason": "No projects to evaluate.", "matched_projects": []}

    profile = _load_profile()
    jd_req = jd_target.get("extracted_requirements", {})
    seniority_req = jd_req.get("seniority_requirement", {})
    seniority_fit, seniority_reason = _compute_seniority_fit(profile, seniority_req)

    # Build project bullet lookup
    project_bullets = {p["id"]: _collect_all_bullets(p) for p in projects}

    try:
        llm_result = complete_json(_build_match_prompt(profile, jd_req, seniority_fit, seniority_reason, projects))
        matched = []
        for mp in llm_result.get("matched_projects", []):
            project = next((p for p in projects if p["id"] == mp["project_id"]), None)
            if not project:
                continue
            all_bullets = project_bullets[project["id"]]
            included_indices = set(mp.get("included_bullet_indices", [0]))
            tailored_bullets = [
                {
                    "bullet": b["text"],
                    "included": i in included_indices,
                    "source": "selected",
                    "addresses": ["tech_stack"],
                    "source_references": [b["source"]],
                    "reasoning": mp.get("fit_reason", ""),
                    "order": i,
                }
                for i, b in enumerate(all_bullets)
            ]
            matched.append({
                "project_id": mp["project_id"],
                "project_title": mp.get("project_title", project.get("title", "")),
                "fit_score": mp.get("fit_score", 0),
                "fit_reason": mp.get("fit_reason", ""),
                "addressed_requirements": mp.get("addressed_requirements", []),
                "tailored_bullets": tailored_bullets,
                "score_breakdown": {
                    "tech_stack_overlap": 0,
                    "domain_relevance": 0,
                    "collaboration_signals": 0,
                    "seniority_alignment": 0,
                },
            })
        return {
            "seniority_fit": llm_result.get("seniority_fit", seniority_fit),
            "seniority_fit_reason": llm_result.get("seniority_fit_reason", seniority_reason),
            "matched_projects": sorted(matched, key=lambda x: x["fit_score"], reverse=True),
        }
    except Exception:
        results = [_score_fallback(p, jd_req) for p in projects]
        results = [r for r in results if r["fit_score"] >= 45]
        results.sort(key=lambda x: x["fit_score"], reverse=True)
        return {
            "seniority_fit": seniority_fit,
            "seniority_fit_reason": seniority_reason,
            "matched_projects": results,
        }


def rewrite_selected_bullets(jd_target: dict, selected_bullets: list) -> dict:
    """Rewrite selected bullet texts to be more tailored to the JD."""
    jd_req = jd_target.get("extracted_requirements", {})

    if not selected_bullets:
        return {"rewritten_bullets": []}

    bullet_list = "\n".join(f"{i + 1}. {b}" for i, b in enumerate(selected_bullets))

    prompt = f"""You are a professional technical resume writer.

Rewrite each resume bullet below to better match the target job description.
Use ONLY the facts present in the original bullet — do not fabricate details.
Each rewritten bullet must be 14-32 words, start with an action verb, and use past tense.

## Target Job
Role: {jd_target.get("title", "Software Engineer")}
Company: {jd_target.get("company", "Unknown")}
Tech stack: {", ".join(jd_req.get("tech_stack", []))}
Seniority: {jd_req.get("seniority_requirement", {}).get("expected_level", "not_stated")}
Domain: {", ".join(jd_req.get("domain", []))}
Collaboration: {", ".join(jd_req.get("collaboration", []))}
Role category: {jd_req.get("role_category", "")}

## Original Bullets
{bullet_list}

Return ONLY valid JSON:
{{
  "rewritten_bullets": [
    {{
      "original": "exact original text",
      "rewritten": "rewritten bullet text"
    }}
  ]
}}

Rules:
- Rewrite EVERY bullet — the array length must equal the input count ({len(selected_bullets)})
- No fabrication — only rephrase and reframe using existing content
- Emphasize technologies and skills that match the JD when present in the original
- Lead with JD-required technology if it appears in the original bullet"""

    try:
        return complete_json(prompt)
    except Exception:
        return {
            "rewritten_bullets": [{"original": b, "rewritten": b} for b in selected_bullets]
        }
