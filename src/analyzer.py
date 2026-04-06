import re
from src.ai.client import complete_json

TAGS = [
    "vue_web", "state_store_design", "frontend_architecture",
    "api_interface_definition", "workflow_complexity",
    "platform_coordination", "middle_office", "cross_functional",
]

CATEGORIES = ["web_app", "mobile", "backend", "data", "devops", "platform", "other"]

TAG_KEYWORDS = {
    "vue_web": ["vue", "vuex", "pinia", "vite", "nuxt"],
    "state_store_design": ["pinia", "vuex", "redux", "state management", "store", "zustand"],
    "frontend_architecture": ["react", "angular", "component", "frontend architecture", "spa"],
    "api_interface_definition": ["rest api", "graphql", "api contract", "openapi", "swagger", "interface design"],
    "workflow_complexity": ["workflow", "multi-step", "bpmn", "pipeline", "state machine", "orchestration"],
    "platform_coordination": ["cross-platform", "web and mobile", "multi-platform", "platform coordination"],
    "middle_office": ["middle office", "middle platform", "internal platform", "shared platform", "middleware"],
    "cross_functional": ["cross-functional", "cross-team", "design handoff", "product", "qa", "backend team"],
}

CATEGORY_KEYWORDS = {
    "web_app": ["vue", "react", "angular", "frontend", "web", "spa", "vite", "webpack"],
    "mobile": ["ios", "android", "react native", "flutter", "mobile"],
    "backend": ["api", "server", "database", "sql", "node.js", "django", "fastapi", "spring"],
    "data": ["data pipeline", "etl", "analytics", "ml", "machine learning", "spark", "airflow"],
    "devops": ["ci/cd", "docker", "kubernetes", "terraform", "infrastructure", "cloud", "aws", "gcp"],
    "platform": ["internal platform", "middleware", "shared service", "platform"],
}


def detect_tags(text: str) -> list:
    lower = text.lower()
    return [tag for tag, kws in TAG_KEYWORDS.items() if any(kw in lower for kw in kws)]


def detect_category(text: str) -> str:
    lower = text.lower()
    scores = {cat: sum(1 for kw in kws if kw in lower) for cat, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"


def _build_prompt(source: dict, context: dict) -> str:
    contributions = context.get("contributions", {})
    background = context.get("background", {})
    return f"""You are a professional resume writer and senior software engineer.

Analyze the project materials and user-provided context below. Generate structured resume and interview preparation content.

## Extracted source material
{source.get("raw_text", "")[:4000]}

## User-provided context

Background (NOT the user's work):
- Business / project background: {background.get("business_background", "")}
- Team / client requirements: {background.get("team_client_requirements", "")}
- PM product decisions: {background.get("pm_product_decisions", "")}

User Contributions:
- T1 responsibilities (scope analysis, API/interface design): {contributions.get("t1_responsibilities", "")}
- T2 responsibilities (implementation, web development): {contributions.get("t2_responsibilities", "")}
- Architecture details: {contributions.get("architecture_details", "")}
- Cross-platform / cross-functional coordination: {contributions.get("cross_functional_coordination", "")}
- Challenges, constraints, tradeoffs: {contributions.get("challenges_constraints_tradeoffs", "")}
- Outcomes and impact: {contributions.get("outcomes_impact", "")}

## Rules
- User Contributions fields are the primary source for the user's actual work
- Background fields clarify engineering context only — do NOT attribute them to the user
- Use extracted source material to fill in technical detail, but defer to Contributions for ownership
- Do NOT invent facts, metrics, or responsibilities
- Use universal technical language; remove all company/product/team names
- All bullets use past tense, start with a different strong action verb
- summary_bullet: 22-38 words, standalone, context + action + outcome
- resume_bullets: 3-5 bullets, 14-32 words each
- If no Contributions fields are filled, use extracted text for technical context only

Return ONLY valid JSON with this exact structure:
{{
  "title": "string (short project title inferred from content)",
  "summary": "string (2-3 sentence professional summary)",
  "summary_bullet": "string (22-38 words, standalone resume bullet)",
  "ownership_description": "string",
  "self_introduction": "string (1-2 sentences)",
  "resume_bullets": ["string", "string", "string"],
  "technical_highlights": ["string", "string", "string"],
  "talking_points": ["string", "string", "string"],
  "interview_answer_star": {{
    "situation": "string",
    "task": "string",
    "action": "string",
    "result": "string"
  }},
  "technical_learning_arc": {{
    "primary_challenge": "string",
    "approach_and_why": "string",
    "key_learning_insight": "string",
    "transfer_value": "string"
  }},
  "anticipated_interview_questions": [
    {{
      "question": "string",
      "intent": "string",
      "suggested_answer_frames": ["string", "string"]
    }}
  ],
  "role_emphasis_prep": {{
    "primary_themes": ["string"],
    "cross_functional_elements": ["string"],
    "technical_depth_areas": ["string"]
  }}
}}"""


def analyze_project(source: dict, context: dict) -> dict:
    raw_text = source.get("raw_text", "")
    combined = raw_text + " " + str(context)
    tags = detect_tags(combined)
    category = detect_category(combined)

    try:
        result = complete_json(_build_prompt(source, context))
    except Exception as e:
        result = _fallback_analysis(source, context)

    title = result.pop("title", "Untitled Project")
    return {
        "title": title,
        "category": category,
        "tags": tags,
        "analysis": {
            "summary": result.get("summary", ""),
            "summary_bullet": result.get("summary_bullet", ""),
            "ownership_description": result.get("ownership_description", ""),
            "self_introduction": result.get("self_introduction", ""),
            "resume_bullets": result.get("resume_bullets", []),
            "technical_highlights": result.get("technical_highlights", []),
            "talking_points": result.get("talking_points", []),
            "interview_answer_star": result.get("interview_answer_star", {}),
            "technical_learning_arc": result.get("technical_learning_arc", {}),
            "anticipated_interview_questions": result.get("anticipated_interview_questions", []),
            "role_emphasis_prep": result.get("role_emphasis_prep", {}),
        },
    }


def _fallback_analysis(source: dict, context: dict) -> dict:
    contributions = context.get("contributions", {})
    raw = source.get("raw_text", "")
    t2 = contributions.get("t2_responsibilities", "")
    outcomes = contributions.get("outcomes_impact", "")

    summary_bullet = ""
    if t2:
        summary_bullet = f"Implemented {t2[:60].strip()}."
    elif raw:
        summary_bullet = raw[:80].strip() + "."

    return {
        "title": "Project",
        "summary": raw[:200] if raw else "Project analysis pending.",
        "summary_bullet": summary_bullet,
        "ownership_description": t2 or "See contributions.",
        "self_introduction": summary_bullet[:120] if summary_bullet else "",
        "resume_bullets": [summary_bullet] if summary_bullet else [],
        "technical_highlights": [],
        "talking_points": [],
        "interview_answer_star": {},
        "technical_learning_arc": {},
        "anticipated_interview_questions": [],
        "role_emphasis_prep": {"primary_themes": [], "cross_functional_elements": [], "technical_depth_areas": []},
    }
