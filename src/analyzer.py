import os
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
    Analyze project text and context. Uses LLM when ANTHROPIC_API_KEY is set,
    falls back to rule-based extraction otherwise.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            result = _analyze_with_llm(raw_text, context)
            _validate(result)
            result["context"] = context
            return result
        except Exception:
            pass  # fall through to rule-based

    return _analyze_rule_based(raw_text, context)


def _analyze_with_llm(raw_text: str, context: dict) -> dict:
    from src.ai.client import complete_json

    t1           = context.get("t1_responsibilities", "").strip()
    t2           = context.get("t2_responsibilities", "").strip()
    arch         = context.get("architecture_details", "").strip()
    outcomes     = context.get("outcomes", "").strip()
    challenges   = context.get("challenges", "").strip()
    coordination = context.get("coordination", "").strip()
    background   = context.get("business_background", "").strip()
    team_req     = context.get("team_client_requirements", "").strip()
    pm           = context.get("pm_decisions", "").strip()

    context_block = "\n".join(filter(None, [
        f"Business background (NOT the engineer's work): {background}" if background else "",
        f"Team/client requirements: {team_req}" if team_req else "",
        f"PM decisions: {pm}" if pm else "",
        f"T1 — Design & architecture scope (engineer's own work): {t1}" if t1 else "",
        f"T2 — Implementation (engineer's own work): {t2}" if t2 else "",
        f"Architecture details: {arch}" if arch else "",
        f"Cross-team coordination: {coordination}" if coordination else "",
        f"Challenges & tradeoffs: {challenges}" if challenges else "",
        f"Outcomes & impact: {outcomes}" if outcomes else "",
    ]))

    valid_tags = sorted(VALID_TAGS)
    valid_cats = sorted(VALID_CATEGORIES)

    prompt = f"""You are analyzing a software engineer's project to produce structured resume content.

--- RAW PROJECT TEXT ---
{raw_text[:3000]}

--- ENGINEER-PROVIDED CONTEXT ---
{context_block or "(none provided)"}

--- TASK ---
Produce a JSON object with exactly these fields:

{{
  "title": "Project title — extract from the raw text or infer from context (≤80 chars)",
  "category": "One of: {', '.join(valid_cats)}",
  "tags": ["Pick relevant tags from this list only: {', '.join(valid_tags)}"],
  "summary": "2–3 sentence paragraph describing what the engineer built technically and what it enabled. Written in third person, past tense. Use ONLY universal engineering language — do NOT include company names, product names, project names, internal platform names (e.g. no 'v9.4', no platform codenames), designer names, stakeholder names, or any internal organizational terminology.",
  "ownership_description": "Paragraph clearly separating business context (background/PM decisions) from the engineer's own T1 design work and T2 implementation. Use universal engineering language — replace all internal names, platform labels, and team-specific terminology with generic technical descriptions.",
  "technical_highlights": [
    "3–5 specific technical achievements. Each is one sentence naming the concrete system, pattern, or decision — not generic praise. No internal names or product references."
  ],
  "interview_answer": "STAR format answer (4 paragraphs labelled Situation / Task / Action / Result) the engineer can speak aloud in an interview. ~150 words total. Use universal language — no company, product, or internal system names.",
  "self_intro": "One sentence (≤25 words) the engineer can use to introduce this project verbally. No internal names.",
  "talking_points": ["3–5 short bullet topics the engineer should be ready to discuss in depth"]
}}

Rules:
- Only use facts present in the raw text and context above — do not invent details
- Tags must be chosen only from the provided list; omit any that don't apply
- Category must be exactly one of the provided values
- Strip all internal names: no company names, product names, project names, internal platform names, version labels, designer names, stakeholder names, or team-specific terminology anywhere in the output"""

    result = complete_json(prompt, max_tokens=2048)

    # Generate resume bullets via the dedicated prompt
    bullets_result = _generate_resume_bullets(
        task_description=raw_text[:3000],
        additional_context=context_block or "(none provided)",
    )
    result["summary_bullet"] = bullets_result.get("summary_bullet", "")
    result["resume_bullets"] = bullets_result.get("resume_bullets", [])

    # Merge ownership_classification from raw context (not LLM-generated)
    result["ownership_classification"] = {
        "background": " ".join(filter(None, [background, team_req, pm])) or "(not provided)",
        "t1_contribution": t1 or "(not provided)",
        "t2_contribution": t2 or "(not provided)",
        "coordination": coordination or "(not provided)",
        "outcome": outcomes or "(not provided)",
    }

    return result


def _generate_resume_bullets(task_description: str, additional_context: str) -> dict:
    """
    Calls the LLM using the resume-bullets-prompt spec.
    Returns {"summary_bullet": "...", "resume_bullets": ["...", ...]}.
    """
    from src.ai.client import complete_json

    prompt = f"""You are a professional resume writer specializing in software engineering roles.

Your task is to convert a software engineer's project task description into polished, technically strong resume bullets that are also useful for technical interview preparation.

## Goal

Produce output that focuses only on the **universal technical work**:
- what was changed
- in what engineering scenario
- what mechanism, pattern, or system behavior was involved
- what technically improved as a result

Remove all project-specific background and internal wording.

The output should be reusable in any software engineering context and understandable without knowledge of the original company, product, team, or project.

---

## Input

**Task description:**
{task_description}

**Additional context (optional):**
{additional_context}

---

## Output Format

Return a JSON object with exactly this structure:

{{
  "summary_bullet": "...",
  "resume_bullets": [
    "...",
    "...",
    "..."
  ]
}}

---

## Required Behavior

### 1) summary_bullet — primary standalone bullet

Must:
- be exactly one sentence
- start with a strong past-tense action verb
- include the technical context or scenario
- state the main technical action
- mention the core mechanism, pattern, or architectural change
- describe the resulting technical improvement or effect when stated or clearly implied
- be **22–38 words**
- be understandable without any project title or extra explanation

### 2) resume_bullets — supporting bullets (3–5)

Each must:
- start with a different past-tense action verb (no verb repeated across all bullets including summary_bullet)
- add specific technical detail not fully covered in summary_bullet
- describe a concrete implementation, refactor, safeguard, optimization, integration, or system behavior
- use universal technical language
- be **14–32 words**
- be self-contained and readable without project or product context

---

## Universalization Rules

Do NOT include: company names, project names, team names, feature names, initiative names, internal architecture labels, internal service names, product names, customer or business background, roadmap context, proprietary terminology, or product-domain wording that would not transfer to another engineering environment.

Replace internal names with generic technical descriptions:
- named store/hook/function → "a centralized store", "a state management hook", "a client-side utility"
- internal service name → "a backend service", "an internal platform service", "a processing service"
- internal event system → "an event bus", "an asynchronous messaging layer", "an event-driven workflow"
- feature flag label → "a feature flag", "a configuration toggle"
- product surface name → "a user-facing interface", "a client module", "an administrative workflow"

---

## Technical Language for Web / Software Engineering Roles

Write at the level of a strong mid-to-senior software engineer. Use concrete engineering language:

- For frontend/web: component architecture, reactivity model, state management (Pinia/Vuex/Redux), lifecycle hooks, virtual DOM, lazy loading, code splitting, composable/hook patterns, API layer design, form validation, event delegation, render optimization
- For backend/API: REST/GraphQL endpoint design, middleware pipeline, request validation, authentication/authorization flow, ORM query optimization, async processing, caching strategy, error handling pattern
- For system/platform: service abstraction, dependency injection, event-driven architecture, pub/sub pattern, retry/fallback logic, interface contract, modular decomposition

Avoid vague product-level descriptions like "enabled users to...", "allowed the team to...", "improved the experience of...". These are not engineering bullets.

---

## Content Constraints

- Do NOT invent facts, metrics, scale, latency, reliability, or performance results
- Only use details explicitly stated or clearly implied by the input
- Use past tense throughout
- Do not use vague filler: "worked on", "helped with", "was involved in", "contributed to"
- Do not write business summaries, product summaries, mini design docs, or stakeholder context"""

    return complete_json(prompt, max_tokens=1024)


def _analyze_rule_based(raw_text: str, context: dict) -> dict:
    combined = raw_text + " " + " ".join(str(v) for v in context.values())
    combined_lower = combined.lower()

    tags = _detect_tags(combined_lower)
    category = _detect_category(combined_lower)
    title = _extract_title(raw_text, context)

    t1           = context.get("t1_responsibilities", "").strip()
    t2           = context.get("t2_responsibilities", "").strip()
    outcomes     = context.get("outcomes", "").strip()
    challenges   = context.get("challenges", "").strip()
    arch         = context.get("architecture_details", "").strip()
    coordination = context.get("coordination", "").strip()
    background   = context.get("business_background", "").strip()
    team_req     = context.get("team_client_requirements", "").strip()
    pm           = context.get("pm_decisions", "").strip()

    highlights = _extract_highlights(raw_text, combined_lower)
    bullets = _build_bullets([t1, t2, arch, coordination])

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
        "summary": _build_summary(title, t1, t2, outcomes, raw_text),
        "ownership_description": _build_ownership_desc(background, pm, t1, t2, coordination),
        "technical_highlights": highlights or ["(no technical highlights extracted — add more context)"],
        "summary_bullet": "(LLM required for resume bullets — set ANTHROPIC_API_KEY)",
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
        "summary_bullet", "resume_bullets", "interview_answer", "self_intro", "talking_points",
    ]
    for key in required:
        if key not in result:
            raise ValueError(f"Analysis response missing required field: '{key}'")

    if result["category"] not in VALID_CATEGORIES:
        result["category"] = "other"

    result["tags"] = [t for t in result["tags"] if t in VALID_TAGS]
