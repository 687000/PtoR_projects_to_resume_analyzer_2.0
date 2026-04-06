import re
from src.ai.client import complete_json

TECH_KEYWORDS = [
    "javascript", "typescript", "python", "java", "go", "rust", "c++", "c#", "ruby", "php",
    "vue", "react", "angular", "svelte", "next.js", "nuxt", "vite", "webpack",
    "node.js", "express", "fastapi", "django", "flask", "spring", "rails",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd",
    "rest api", "graphql", "grpc", "websocket", "kafka", "rabbitmq",
    "tailwind", "css", "sass", "html", "pinia", "vuex", "redux",
]

DOMAIN_KEYWORDS = {
    "web_app": ["web app", "spa", "frontend", "ui", "dashboard", "portal"],
    "mobile": ["ios", "android", "mobile", "react native", "flutter"],
    "backend": ["backend", "server-side", "microservices", "api service"],
    "platform": ["platform", "internal tool", "middleware", "shared service"],
    "middle_office": ["middle office", "middle platform", "internal platform"],
    "data": ["data", "analytics", "ml", "machine learning", "pipeline", "etl"],
    "devops": ["devops", "infrastructure", "cloud", "ci/cd", "deployment"],
}

COLLABORATION_KEYWORDS = [
    "cross-functional", "cross-team", "agile", "scrum", "stakeholder",
    "mentor", "lead", "coordinate", "align", "product owner", "design",
    "pm", "product manager", "backend team", "mobile team",
]

SENIORITY_KEYWORDS = {
    "junior": ["junior", "entry level", "0-2 years", "1+ year"],
    "mid": ["mid-level", "3+ years", "2-4 years", "3-5 years"],
    "senior": ["senior", "5+ years", "4+ years", "6+ years"],
    "lead": ["lead", "staff", "principal", "tech lead", "team lead"],
}


def _extract_fallback(text: str) -> dict:
    lower = text.lower()

    tech_stack = [kw for kw in TECH_KEYWORDS if kw in lower]

    domain = []
    for d, kws in DOMAIN_KEYWORDS.items():
        if any(kw in lower for kw in kws):
            domain.append(d)

    collaboration = [kw for kw in COLLABORATION_KEYWORDS if kw in lower]

    expected_level = "not_stated"
    min_years = None
    ownership_signals = []
    for level, kws in SENIORITY_KEYWORDS.items():
        if any(kw in lower for kw in kws):
            expected_level = level
            break

    years_match = re.search(r"(\d+)\+?\s*years?", lower)
    if years_match:
        min_years = int(years_match.group(1))

    if any(w in lower for w in ["own", "lead", "architect", "decision", "independent"]):
        ownership_signals.append("independent decision-making")
    if any(w in lower for w in ["mentor", "coach", "guide junior"]):
        ownership_signals.append("mentoring")

    role_category = "other"
    if any(w in lower for w in ["frontend", "ui", "vue", "react"]):
        role_category = "frontend"
    elif any(w in lower for w in ["backend", "server", "api"]):
        role_category = "backend"
    elif any(w in lower for w in ["full stack", "fullstack"]):
        role_category = "fullstack"
    elif any(w in lower for w in ["data", "ml", "machine learning"]):
        role_category = "data"

    title_match = re.search(r"(senior|lead|staff|principal|mid|junior)?\s*(frontend|backend|full.?stack|software|data|platform)\s*(engineer|developer|architect)", lower)
    title = title_match.group(0).title() if title_match else "Software Engineer"

    return {
        "title": title,
        "company": None,
        "extracted_requirements": {
            "tech_stack": tech_stack[:15],
            "seniority_requirement": {
                "min_years": min_years,
                "expected_level": expected_level,
                "ownership_signals": ownership_signals,
            },
            "domain": domain or ["web_app"],
            "collaboration": collaboration[:10],
            "role_category": role_category,
        },
    }


def _build_prompt(raw_text: str) -> str:
    return f"""You are analyzing a job description to extract structured hiring requirements for a software engineering role.

## Job Description
{raw_text[:3000]}

## Task
Extract requirements into the following categories. Return ONLY valid JSON:

{{
  "title": "string (job title extracted from JD)",
  "company": "string or null",
  "extracted_requirements": {{
    "tech_stack": ["lowercase exact terms — e.g. vue, typescript, rest api"],
    "seniority_requirement": {{
      "min_years": null,
      "expected_level": "junior | mid | senior | lead | principal | not_stated",
      "ownership_signals": ["e.g. independent decision-making", "architecture ownership", "team leadership"]
    }},
    "domain": ["web_app | mobile | backend | platform | middle_office | data | devops"],
    "collaboration": ["e.g. cross-team coordination", "agile", "stakeholder interaction"],
    "role_category": "string (e.g. frontend, backend, fullstack, data, platform)"
  }}
}}

Rules:
- Only include what is explicitly stated or strongly implied
- Do not invent requirements
- tech_stack entries must be lowercase exact terms
- domain entries must be from: web_app, mobile, backend, platform, middle_office, data, devops"""


def analyze_jd(source: dict) -> dict:
    raw_text = source.get("raw_text", "")
    try:
        result = complete_json(_build_prompt(raw_text))
    except Exception:
        result = _extract_fallback(raw_text)

    result.setdefault("title", "Software Engineer Role")
    result.setdefault("company", None)
    result.setdefault("extracted_requirements", {})
    req = result["extracted_requirements"]
    req.setdefault("tech_stack", [])
    req.setdefault("seniority_requirement", {"min_years": None, "expected_level": "not_stated", "ownership_signals": []})
    req.setdefault("domain", [])
    req.setdefault("collaboration", [])
    req.setdefault("role_category", "other")

    return {
        "title": result["title"],
        "company": result["company"],
        "source": {
            "source_type": source.get("source_type", "text"),
            "raw_text": raw_text,
            "source_reference": source.get("source_reference", ""),
        },
        "extracted_requirements": req,
        "match_results": {"projects": []},
        "seniority_fit": None,
        "seniority_fit_reason": None,
    }
