# Prompt Spec: JD → Project Match + Tailored Bullets

This document describes the matching pipeline: how a job description is parsed into requirements, how existing project bullets are matched and selected, and how new bullets are optionally generated on demand.

---

## User Profile

Seniority matching is based on the candidate's profile, not on project properties. The profile is stored in `data/user_profile.json` and provided as input to every stage.

```json
{
  "education": [
    { "degree": "Bachelor | Master | PhD | Other", "field": "e.g. Computer Science" }
  ],
  "years_of_experience": 4,
  "self_described_level": "junior | mid | mid-senior | senior | lead | principal",
  "notes": "Optional free-text for additional context (e.g. domain focus, career gaps)"
}
```

This profile is read-only at match time. The user updates it manually in settings.

---

## Pipeline Overview

```
User profile (education, YoE, level)  ─────────────────────────────┐
Raw JD text                                                        │
  → Stage 1: Extract requirements     (LLM; fallback: rule-based)  │
  → Stage 2: Match & select bullets   (LLM; fallback: rule-based) ─┘
  → Stage 3: Generate new bullets     (LLM only; triggered by explicit user action)
```

**Rematch Action** reruns Stage 1 + Stage 2 only. Stage 3 is never triggered automatically.

---

## Stage 1: Requirements Extraction (LLM)

Extract structured requirements from the raw JD text.

### Prompt

```
You are analyzing a job description to extract structured hiring requirements for a software engineering role.

## Job Description
{jd_text}

## Task
Extract requirements into the following categories:

- tech_stack: specific languages, frameworks, libraries, and tools explicitly required or strongly preferred
- seniority_requirement: the expected experience level of the candidate — describe as a structured object:
    - min_years: minimum years of experience required (integer or null if not stated)
    - expected_level: one of junior | mid | senior | lead | principal | not_stated
    - ownership_signals: list of ownership expectations mentioned (e.g. "independent decision-making", "architecture ownership", "team leadership")
- domain: application domains the role operates in — choose from: web_app, mobile, backend, platform, middle_office, data, devops
- collaboration: cross-functional signals — agile practices, stakeholder interaction, team coordination, mentoring

Return JSON:
{
  "tech_stack": ["..."],
  "seniority_requirement": {
    "min_years": null,
    "expected_level": "senior",
    "ownership_signals": ["..."]
  },
  "domain": ["..."],
  "collaboration": ["..."]
}

Rules:
- Only include what is explicitly stated or strongly implied in the JD
- Do not invent requirements
- tech_stack entries should be lowercase exact terms (e.g. "vue", "typescript", "rest api")
- domain entries must be from the allowed list above
```

### Fallback (rule-based)

Keyword scan of lowercased JD text against fixed keyword lists for tech, domain, and collaboration. Seniority is extracted by matching title keywords (senior/lead/principal/staff) and year patterns (e.g. "5+ years").

---

## Stage 2: Match & Select Bullets (LLM)

Match the extracted requirements against all saved projects. For each project, select the best bullet(s) from its existing `summary_bullet` and `resume_bullets`.

Seniority is evaluated once at the top level by comparing the JD's `seniority_requirement` against the user's profile. It informs the overall match context but is **not** re-evaluated per project.

### Priority order for bullet matching

1. **Tech stack** — does the bullet demonstrate the required technologies?
2. **Domain** — does the project category or tags align with the JD domain?
3. **Collaboration** — does the project show cross-functional or team coordination signals?

Seniority is handled separately — see "Seniority Evaluation" below.

### Selection rules

- **`summary_bullet` has higher weight** than `resume_bullets`. Prefer it when it is relevant.
- Select **at most one bullet per project** unless the fit is exceptionally strong (tech + domain + collaboration all satisfied).
- The selected bullet must be self-contained: a reader unfamiliar with the project should understand the tech and relevance without extra context.
- **No duplication**: if two bullets across different projects cover the same technology and outcome, select only the more relevant one.

### Seniority Evaluation

Before scoring projects, evaluate whether the user's profile meets the JD's seniority requirement. This produces a `seniority_fit` field that is passed to the LLM as context.

```
user profile:
  years_of_experience: {years_of_experience}
  self_described_level: {self_described_level}
  education: {education_list}

jd seniority requirement:
  min_years: {min_years}
  expected_level: {expected_level}
  ownership_signals: {ownership_signals}

seniority_fit: "meets" | "partial" | "below"
```

Rules for computing `seniority_fit`:

| Condition | Result |
| --------- | ------ |
| YoE ≥ min_years AND level matches or exceeds expected_level | `meets` |
| YoE within 1 year of min_years OR level is one step below | `partial` |
| YoE significantly below OR level is two+ steps below | `below` |
| JD has no seniority requirement (`not_stated`) | `meets` |

### Prompt

```
You are a senior resume editor helping a software engineer select the most relevant resume bullets for a job application.

## Candidate Profile
- Years of experience: {years_of_experience}
- Self-described level: {self_described_level}
- Education: {education_list}  (e.g. "Bachelor in Computer Science, Master in Software Engineering")
- Notes: {notes}

## Seniority Fit
The candidate's profile has been evaluated against the JD's seniority requirement: {seniority_fit}
({seniority_fit_reason})

## Job Requirements
- Tech stack: {tech_stack}
- Domain: {domain}
- Collaboration signals: {collaboration}
- Seniority expected: {expected_level} (min {min_years} years)

## Candidate Projects
{projects_block}

Each project is listed with:
- project_id
- summary_bullet (primary standalone bullet — higher weight)
- resume_bullets (supporting detail bullets)
- category and tags

## Task
For each project, decide whether to include it and which bullet(s) to select.

Selection rules:
1. Match priority: tech stack match > domain alignment > collaboration signals
2. summary_bullet has higher weight — prefer it when relevant
3. Select at most one bullet per project unless the project satisfies all three match dimensions (tech + domain + collaboration)
4. If two bullets across different projects are near-identical in tech and outcome, select only the more relevant one — avoid duplication
5. A selected bullet must be self-contained: it must clearly explain what was built, which technologies were used, and why it is relevant, without needing project context
6. If a project has no relevant match to the job requirements, exclude it entirely
7. If seniority_fit is "below", prefer bullets that demonstrate ownership, decision-making, or cross-functional scope — these help compensate for the gap

Return JSON:
{
  "seniority_fit": "meets" | "partial" | "below",
  "seniority_fit_reason": "one sentence",
  "matched_projects": [
    {
      "project_id": "...",
      "fit_score": 0-100,
      "fit_reason": "one sentence explaining the match",
      "addressed_requirements": ["list of matched requirement terms"],
      "selected_bullets": [
        {
          "text": "exact bullet text copied from input",
          "source": "summary_bullet" | "resume_bullet",
          "included": true | false
        }
      ]
    }
  ]
}

Rules:
- fit_score reflects tech + domain + collaboration match only (not seniority)
- Only projects with fit_score ≥ 45 should have included: true bullets
- Do not rewrite or paraphrase bullet text — copy it exactly
- Do not invent requirements or match signals not present in the job description
- Sort matched_projects by fit_score descending
```

### Fallback (rule-based)

1. Compute `seniority_fit` by comparing `user_profile.years_of_experience` and `user_profile.self_described_level` against extracted seniority requirement using the tier table above.
2. Score each project across three dimensions (tech 50%, domain 30%, collaboration 20%) using keyword overlap.
3. `summary_bullet` is always placed first (pinned — not sorted with the rest).
4. Remaining `resume_bullets` are sorted by tech-keyword overlap.
5. Auto-select based on fit score tier:

| `fit_score` | Bullets included |
| ----------- | ---------------- |
| ≥ 85        | up to 2 (summary + 1 supporting, if non-duplicative) |
| ≥ 65        | 1 (summary_bullet preferred) |
| ≥ 45        | 1 (summary_bullet preferred) |
| < 45        | 0 |

---

## Stage 3: Bullet Generation (LLM only — explicit user action)

Triggered only when the user clicks **"Generate Bullets"** for a specific project within the JD view. Never runs automatically during analyze or rematch.

Generates new tailored bullets using the dedicated `jd-tailored-bullets-prompt.md` which combines the project's context with the JD requirements to produce 2-3 bullets that directly address specific JD requirements while tracing back to project evidence.

**See:** `docs/project-specs/prompts/jd-tailored-bullets-prompt.md` for the complete prompt specification.

---

## Output Shape (Stage 2 result)

```json
{
  "seniority_fit": "partial",
  "seniority_fit_reason": "Candidate has 4 years of experience; JD requires 5+, but ownership signals are present.",
  "matched_projects": [
    {
      "project_id": "...",
      "project_title": "...",
      "fit_score": 72,
      "fit_reason": "Strong Vue and TypeScript match; domain aligns with web_app.",
      "addressed_requirements": ["vue", "typescript", "web_app"],
      "selected_bullets": [
        {
          "text": "...",
          "source": "summary_bullet",
          "included": true
        },
        {
          "text": "...",
          "source": "resume_bullet",
          "included": false
        }
      ]
    }
  ]
}
```

Results are sorted by `fit_score` descending.
