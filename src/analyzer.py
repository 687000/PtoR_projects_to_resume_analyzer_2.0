import re

VALID_TAGS = {
    "frontend_architecture",
    "vue_web",
    "state_store_design",
    "api_interface_definition",
    "platform_coordination",
    "workflow_complexity",
    "middle_office",
    "cross_functional",
}

VALID_CATEGORIES = {
    "web_app",
    "mobile",
    "backend",
    "data",
    "devops",
    "platform",
    "other",
}

# Keyword → tag
_KEYWORD_TAG: list[tuple[str, str]] = [
    ("vue", "vue_web"),
    ("vuex", "state_store_design"),
    ("pinia", "state_store_design"),
    ("react", "frontend_architecture"),
    ("angular", "frontend_architecture"),
    ("redux", "state_store_design"),
    ("zustand", "state_store_design"),
    ("rest api", "api_interface_definition"),
    ("graphql", "api_interface_definition"),
    ("openapi", "api_interface_definition"),
    ("swagger", "api_interface_definition"),
    ("interface design", "api_interface_definition"),
    ("workflow", "workflow_complexity"),
    ("bpmn", "workflow_complexity"),
    ("pipeline", "workflow_complexity"),
    ("middle office", "middle_office"),
    ("middleware", "middle_office"),
    ("middle platform", "middle_office"),
    ("ios", "platform_coordination"),
    ("android", "platform_coordination"),
    ("cross-platform", "platform_coordination"),
    ("mobile", "platform_coordination"),
    ("cross-functional", "cross_functional"),
    ("coordinate", "cross_functional"),
    ("collaborat", "cross_functional"),
]

# Keyword lists → category
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "web_app": ["vue", "react", "angular", "frontend", "web app", "html", "css", "ui component"],
    "mobile": ["ios", "android", "flutter", "swift", "kotlin", "mobile app", "react native"],
    "backend": ["fastapi", "django", "express", "spring", "node.js", "server", "postgres", "mysql", "database", "sql"],
    "data": ["analytics", "machine learning", "ml model", "etl", "pandas", "tensorflow", "pytorch", "data pipeline"],
    "devops": ["docker", "kubernetes", "k8s", "ci/cd", "jenkins", "terraform", "aws", "gcp", "azure", "deployment"],
    "platform": ["platform", "microservice", "middleware", "infrastructure", "sdk", "framework"],
}

_ACTION_VERBS = [
    "Built", "Designed", "Implemented", "Developed", "Led", "Coordinated",
    "Defined", "Architected", "Delivered", "Established", "Optimized",
    "Migrated", "Refactored", "Integrated", "Automated",
]


def analyze_project(raw_text: str, context: dict) -> dict:
    """
    Analyze project text and user-provided context using rule-based extraction.

    No external LLM calls. Tags and category are keyword-matched; output fields
    are structured from the provided context and extracted sentences.

    Returns a structured project record ready for storage.
    """
    combined = raw_text + " " + " ".join(str(v) for v in context.values())
    combined_lower = combined.lower()

    tags = _detect_tags(combined_lower)
    category = _detect_category(combined_lower)
    title = _extract_title(raw_text, context)

    t1 = context.get("t1_responsibilities", "").strip()
    t2 = context.get("t2_responsibilities", "").strip()
    outcomes = context.get("outcomes", "").strip()
    challenges = context.get("challenges", "").strip()
    arch = context.get("architecture_details", "").strip()
    coordination = context.get("coordination", "").strip()
    background = context.get("business_background", "").strip()
    team_req = context.get("team_client_requirements", "").strip()
    pm = context.get("pm_decisions", "").strip()

    highlights = _extract_highlights(raw_text, combined_lower)
    bullets = _build_bullets([t1, t2, arch, coordination])

    summary = _build_summary(title, t1, t2, outcomes, raw_text)
    ownership_desc = _build_ownership_desc(background, pm, t1, t2, coordination)

    result = {
        "title": title,
        "category": category,
        "tags": tags,
        "ownership_classification": {
            "background": " ".join(filter(None, [background, team_req, pm])) or "(not provided)",
            "t1_contribution": t1 or "(not provided)",
            "t2_contribution": t2 or "(not provided)",
            "coordination": coordination or "(not provided)",
            "outcome": outcomes or "(not provided)",
        },
        "summary": summary,
        "ownership_description": ownership_desc,
        "technical_highlights": highlights or ["(no technical highlights extracted — add more context)"],
        "resume_bullets": bullets or ["(add T1/T2 responsibilities to generate bullets)"],
        "interview_answer": _build_star(context),
        "self_intro": _build_self_intro(title, t1, t2),
        "talking_points": _build_talking_points(tags, challenges, t1),
    }

    _validate(result)
    result["context"] = context
    return result


def _detect_tags(text_lower: str) -> list[str]:
    found = set()
    for keyword, tag in _KEYWORD_TAG:
        if keyword in text_lower:
            found.add(tag)
    return sorted(found)


def _detect_category(text_lower: str) -> str:
    scores: dict[str, int] = {cat: 0 for cat in VALID_CATEGORIES}
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[cat] += 1
    best = max(scores, key=lambda c: scores[c])
    return best if scores[best] > 0 else "other"


def _extract_title(raw_text: str, context: dict) -> str:
    # First non-empty line of raw text, trimmed
    for line in raw_text.splitlines():
        line = line.strip().lstrip("#").strip()
        if line and len(line) <= 80:
            return line
    return "Untitled Project"


def _extract_highlights(raw_text: str, combined_lower: str) -> list[str]:
    highlights = []
    # Split into sentences and score by keyword density
    sentences = re.split(r"[.!?\n]+", raw_text)
    for sentence in sentences:
        s = sentence.strip()
        if len(s) < 20:
            continue
        sl = s.lower()
        score = sum(1 for kw, _ in _KEYWORD_TAG if kw in sl)
        if score >= 1:
            highlights.append(s)
    return highlights[:6]


def _build_bullets(fields: list[str]) -> list[str]:
    bullets = []
    for field in fields:
        if not field:
            continue
        parts = re.split(r"[.\n;]+", field)
        for part in parts:
            part = part.strip()
            if len(part) < 15:
                continue
            if not any(part.startswith(v) for v in _ACTION_VERBS):
                part = f"Implemented {part[0].lower()}{part[1:]}"
            bullets.append(part)
    return bullets[:8]


def _build_summary(title: str, t1: str, t2: str, outcomes: str, raw_text: str) -> str:
    parts = []
    if t1:
        parts.append(t1[:200])
    if t2:
        parts.append(t2[:200])
    if outcomes:
        parts.append(outcomes[:150])
    if parts:
        return " ".join(parts)
    # Fall back to first paragraph of raw text
    for para in raw_text.split("\n\n"):
        para = para.strip()
        if len(para) > 30:
            return para[:400]
    return raw_text[:300].strip()


def _build_ownership_desc(background: str, pm: str, t1: str, t2: str, coordination: str) -> str:
    parts = []
    if background or pm:
        ctx = " ".join(filter(None, [background, pm]))
        parts.append(f"Project context (not user work): {ctx}")
    if t1:
        parts.append(f"Technical analysis and design: {t1}")
    if t2:
        parts.append(f"Implementation: {t2}")
    if coordination:
        parts.append(f"Coordination: {coordination}")
    return "\n".join(parts) if parts else "(no ownership context provided)"


def _build_star(context: dict) -> str:
    situation = context.get("business_background", "") or "the project"
    task = context.get("t1_responsibilities", "") or context.get("t2_responsibilities", "") or "deliver technical implementation"
    action = context.get("t2_responsibilities", "") or context.get("architecture_details", "") or "built and shipped the solution"
    result = context.get("outcomes", "") or "completed delivery"
    return (
        f"Situation: {situation}\n"
        f"Task: {task}\n"
        f"Action: {action}\n"
        f"Result: {result}"
    )


def _build_self_intro(title: str, t1: str, t2: str) -> str:
    contrib = t1 or t2
    if contrib:
        short = contrib[:120].rstrip(",; ")
        return f"{title} — {short}"
    return title


def _build_talking_points(tags: list[str], challenges: str, t1: str) -> list[str]:
    points = []
    tag_labels = {
        "vue_web": "Vue.js frontend development",
        "state_store_design": "State management design (Pinia/Vuex)",
        "api_interface_definition": "API and interface design",
        "frontend_architecture": "Frontend architecture decisions",
        "workflow_complexity": "Complex workflow design",
        "platform_coordination": "Cross-platform coordination",
        "middle_office": "Middle-office / platform system",
        "cross_functional": "Cross-functional team collaboration",
    }
    for tag in tags:
        if tag in tag_labels:
            points.append(tag_labels[tag])
    if challenges:
        points.append(f"Challenges navigated: {challenges[:100]}")
    if t1:
        points.append(f"T1 scope: {t1[:100]}")
    return points[:6]


def _validate(result: dict) -> None:
    required = [
        "title", "category", "tags", "ownership_classification",
        "summary", "ownership_description", "technical_highlights",
        "resume_bullets", "interview_answer", "self_intro", "talking_points",
    ]
    for key in required:
        if key not in result:
            raise ValueError(f"Analysis response missing required field: '{key}'")

    if result["category"] not in VALID_CATEGORIES:
        result["category"] = "other"

    result["tags"] = [t for t in result["tags"] if t in VALID_TAGS]
