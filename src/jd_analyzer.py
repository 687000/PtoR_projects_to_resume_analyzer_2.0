import re

_TECH_KEYWORDS = [
    "vue", "react", "angular", "svelte", "typescript", "javascript",
    "python", "java", "go", "rust", "node.js", "express",
    "rest api", "graphql", "grpc", "openapi", "swagger",
    "redux", "pinia", "vuex", "zustand",
    "docker", "kubernetes", "aws", "gcp", "azure",
    "sql", "postgres", "mysql", "mongodb", "redis",
    "webpack", "vite", "rollup",
    "css", "html", "sass", "tailwind",
    "git", "ci/cd", "jenkins",
    "ios", "android", "flutter", "swift", "kotlin",
]

_COLLAB_KEYWORDS = [
    "cross-functional", "cross functional", "collaborate", "collaboration",
    "coordination", "stakeholder", "product manager", "designer",
    "agile", "scrum", "sprint", "team lead", "mentoring", "mentor",
]

_SENIORITY_KEYWORDS = [
    "senior", "lead", "principal", "staff", "architect", "technical lead",
    "3+ years", "4+ years", "5+ years", "6+ years", "7+ years",
    "ownership", "independent",
]

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "web_app":    ["web", "frontend", "ui", "spa", "web application", "browser", "component"],
    "mobile":     ["mobile", "ios", "android", "react native", "flutter"],
    "backend":    ["backend", "server", "api", "microservice", "database"],
    "platform":   ["platform", "infrastructure", "sdk", "framework", "middleware"],
    "middle_office": ["middle office", "middle platform", "workflow", "bpmn"],
    "data":       ["data", "analytics", "ml", "machine learning", "pipeline"],
    "devops":     ["devops", "deployment", "ci/cd", "infrastructure"],
}


def analyze_jd(raw_jd_text: str, projects: list[dict]) -> dict:
    """Extract requirements from a JD and match against saved projects."""
    text_lower = raw_jd_text.lower()
    requirements = _extract_requirements(text_lower)
    role_title = _extract_role_title(raw_jd_text)
    company = _extract_company(raw_jd_text)
    matched = _match_projects(requirements, projects, text_lower)
    return {
        "role_title": role_title,
        "company": company,
        "extracted_requirements": requirements,
        "matched_projects": matched,
    }


def check_duplicate(
    new_requirements: dict, existing_targets: list[dict]
) -> dict | None:
    """Return the most similar existing target if Jaccard similarity >= 0.7."""
    new_set = set(
        new_requirements.get("tech_stack", []) + new_requirements.get("domain", [])
    )
    if not new_set:
        return None
    best_score = 0.0
    best_target = None
    for target in existing_targets:
        existing_reqs = target.get("extracted_requirements", {})
        existing_set = set(
            existing_reqs.get("tech_stack", []) + existing_reqs.get("domain", [])
        )
        if not existing_set:
            continue
        union = len(new_set | existing_set)
        score = len(new_set & existing_set) / union if union else 0.0
        if score > best_score:
            best_score = score
            best_target = target
    return best_target if best_score >= 0.7 else None


def _extract_requirements(text_lower: str) -> dict:
    tech = [kw for kw in _TECH_KEYWORDS if kw in text_lower]
    collab = [kw for kw in _COLLAB_KEYWORDS if kw in text_lower]
    seniority = [kw for kw in _SENIORITY_KEYWORDS if kw in text_lower]
    domain = [
        name
        for name, keywords in _DOMAIN_KEYWORDS.items()
        if any(kw in text_lower for kw in keywords)
    ]
    return {
        "tech_stack": tech,
        "collaboration": collab,
        "domain": domain,
        "seniority": seniority,
    }


def _extract_role_title(raw_text: str) -> str:
    for line in raw_text.splitlines():
        line = line.strip().lstrip("#").strip()
        if line and len(line) <= 80:
            return line
    return "Unknown Role"


def _extract_company(raw_text: str) -> str | None:
    patterns = [
        r"(?:at|@)\s+([A-Z][A-Za-z0-9&\s,\.]{1,40}?)(?:\s*[\n,!]|$)",
        r"Company:\s*([A-Za-z0-9&\s\.]{1,40})",
        r"About\s+([A-Z][A-Za-z0-9&\s]{1,30}?)[\n:]",
    ]
    for pat in patterns:
        m = re.search(pat, raw_text)
        if m:
            name = m.group(1).strip().rstrip(".,")
            if 2 <= len(name) <= 50:
                return name
    return None


def _match_projects(
    requirements: dict, projects: list[dict], jd_lower: str
) -> list[dict]:
    results = []
    for project in projects:
        score, addressed = _score_project(requirements, project)
        bullets = _select_bullets(project, requirements)
        results.append({
            "project_id": project["id"],
            "project_title": project.get("title", "Untitled"),
            "fit_score": score,
            "addressed_requirements": addressed,
            "tailored_bullets": [
                {"text": b, "included": True, "source": "generated", "order": i}
                for i, b in enumerate(bullets)
            ],
        })
    results.sort(key=lambda r: r["fit_score"], reverse=True)
    return results


def _score_project(requirements: dict, project: dict) -> tuple[int, list[str]]:
    addressed: list[str] = []
    project_text = _project_text(project).lower()

    # Tech stack overlap — 40%
    tech_reqs = requirements.get("tech_stack", [])
    if tech_reqs:
        matched_tech = [kw for kw in tech_reqs if kw in project_text]
        tech_score = len(matched_tech) / len(tech_reqs)
        addressed.extend(matched_tech)
    else:
        tech_score = 0.5

    # Domain relevance — 25%
    domain_reqs = requirements.get("domain", [])
    project_category = project.get("category", "other")
    project_tags_text = " ".join(project.get("tags", []))
    domain_matches = [
        d for d in domain_reqs if d == project_category or d in project_tags_text
    ]
    domain_score = min(len(domain_matches) / max(len(domain_reqs), 1), 1.0)
    addressed.extend(domain_matches)

    # Collaboration — 20%
    collab_reqs = requirements.get("collaboration", [])
    has_coord = bool(project.get("context", {}).get("coordination", "").strip())
    has_cross = "cross_functional" in project.get("tags", [])
    if collab_reqs:
        collab_score = 1.0 if (has_coord or has_cross) else 0.2
        if has_coord or has_cross:
            addressed.append("cross-team collaboration")
    else:
        collab_score = 0.5

    # Seniority — 15%
    seniority_reqs = requirements.get("seniority", [])
    has_t1 = bool(project.get("context", {}).get("t1_responsibilities", "").strip())
    if seniority_reqs:
        seniority_score = 1.0 if has_t1 else 0.3
        if has_t1:
            addressed.append("technical design ownership")
    else:
        seniority_score = 0.5

    raw = (
        tech_score * 0.40
        + domain_score * 0.25
        + collab_score * 0.20
        + seniority_score * 0.15
    )
    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped = []
    for item in addressed:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return round(raw * 100), deduped


def _project_text(project: dict) -> str:
    ctx = project.get("context", {})
    return " ".join(
        filter(
            None,
            [
                project.get("raw_text", ""),
                project.get("summary", ""),
                " ".join(project.get("tags", [])),
                ctx.get("t1_responsibilities", ""),
                ctx.get("t2_responsibilities", ""),
                ctx.get("architecture_details", ""),
            ],
        )
    )


def _select_bullets(project: dict, requirements: dict) -> list[str]:
    bullets = project.get("resume_bullets", [])
    if not bullets:
        return []
    tech_reqs = set(requirements.get("tech_stack", []))
    scored = sorted(
        bullets,
        key=lambda b: sum(1 for kw in tech_reqs if kw in b.lower()),
        reverse=True,
    )
    return scored[:4]
