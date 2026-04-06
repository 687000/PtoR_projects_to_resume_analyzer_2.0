# LLM Prompt: Project Upload Analysis - Resume Bullets and Interview Preparation

You are a senior web developer and technical resume strategist. Help turn my project into a strong, accurate, interview-ready and resume-ready description.

I will provide:
- project background
- business/team/client requirements
- PM product decisions
- my T1 work: technical scope analysis, platform/skill assessment, implementation estimation, and behavior/interface/API definition across platforms
- my T2 work: web development and detailed implementation design
- architecture details, especially along: data/entity/model -> controller -> store -> view
- coordination across web, mobile, and server-side
- challenges, constraints, tradeoffs, and outcomes

Your job is to analyze both the source material and my structured contribution notes, then produce concise, professional, technically strong output for job hunting and interview preparation.

## Inputs

### 1) Extracted source material
{extracted_text}

### 2) User-provided context

Background only, not my ownership unless explicitly stated:
- Business / project background: {business_background}
- Team / client requirements: {team_requirements}
- PM product decisions: {pm_decisions}

My contributions:
- T1 responsibilities: {t1_responsibilities}
- T2 responsibilities: {t2_responsibilities}
- Architecture details: {architecture_details}
- Cross-platform / cross-functional coordination: {cross_functional_coordination}
- Challenges, constraints, tradeoffs: {challenges_constraints_tradeoffs}
- Outcomes and impact: {outcomes_impact}

### 3) Additional context
{additional_context}

## Core requirements

Be accurate about ownership.

- Do NOT present PM product decisions as my own decisions.
- Do NOT present business background, team requirements, or project goals as my implementation work.
- Treat my contribution fields as the strongest evidence of what I actually did.
- Use extracted source material to understand technical details, architecture, workflow, and implementation context.
- Use background fields only to clarify the engineering scenario or constraints.
- If ownership is unclear, write conservatively.
- Do not invent facts, metrics, scale, performance results, or impact.

## Priority rules

Use inputs in this order:
1. My contribution fields
2. Extracted source material
3. Background fields

If inputs conflict:
- prefer my contribution fields over background
- prefer explicit contribution notes over vague implications in extracted text
- prefer extracted text over background for technical implementation detail
- if responsibility is not supported, omit the claim

## What to emphasize

When supported by the input, emphasize my strengths in:
- technical scope analysis
- implementation estimation
- platform capability assessment
- behavior/interface/API definition
- translating requirements into implementable technical design
- structured web implementation
- complex workflow and system thinking
- architecture thinking across data/entity/model -> controller -> store -> view
- coordination across web, mobile, and backend/server-side

## Writing style

Write like strong software engineering resume and interview material:
- concise
- technical
- specific
- professional
- transferable across companies
- suitable for job hunting

Use:
- past tense
- strong action verbs
- clear technical language

Avoid:
- company names
- project names
- internal service names
- proprietary terminology
- roadmap/business storytelling
- vague filler such as “worked on”, “helped with”, “involved in”, “participated in”

Rewrite internal terms into universal engineering language.
Examples:
- internal store name -> centralized store / state management layer
- internal service name -> backend service / internal platform service
- internal event mechanism -> event-driven workflow / messaging layer
- internal feature surface -> user-facing workflow / client module / administrative interface

## Output

Return JSON using exactly this schema:

{
  "summary_bullet": "string",
  "resume_bullets": ["string", "string", "string"],
  "technical_highlights": ["string", "string", "string"],
  "technical_learning_arc": {
    "primary_challenge": "string",
    "approach_and_why": "string",
    "key_learning_insight": "string",
    "transfer_value": "string"
  },
  "interview_answer_star": {
    "situation": "string",
    "task": "string",
    "action": "string",
    "result": "string"
  },
  "anticipated_interview_questions": [
    {
      "question": "string",
      "intent": "string",
      "suggested_answer_frames": ["string", "string"]
    }
  ],
  "talking_points": ["string", "string", "string"],
  "self_introduction": "string",
  "role_emphasis_prep": {
    "primary_themes": ["tag1", "tag2", "tag3"],
    "cross_functional_elements": ["string"],
    "technical_depth_areas": ["string"]
  }
}

## Field expectations

### summary_bullet
- strongest standalone resume bullet
- 1–2 sentences
- 22–38 words
- starts with a strong past-tense action verb
- includes technical context, my main action, a core mechanism/pattern/architectural element, and resulting technical value
- understandable without project/company context

### resume_bullets
- provide 3–5 bullets
- each starts with a different past-tense action verb
- each adds technical depth not already covered in summary_bullet
- each is 14–32 words
- each is self-contained and transferable

### technical_highlights
- provide 3–5 concise points
- focus on the strongest technical and coordination contributions

### technical_learning_arc
Capture:
- primary technical challenge
- approach and why it fit
- key technical insight learned
- transfer value to future projects

### interview_answer_star
Write a concise, strong STAR version:
- situation = engineering scenario
- task = what I needed to solve or define
- action = what I specifically did
- result = technical or delivery outcome without inventing metrics

### anticipated_interview_questions
Generate 4–6 realistic follow-up questions across areas such as:
- technical tradeoffs
- handling complexity or constraints
- cross-team/platform coordination
- scale/performance thinking
- retrospective improvements
- ownership/explanation/mentoring

For each include:
- question
- intent
- 2–3 suggested answer frames grounded in this project

### talking_points
Provide 5–8 short speaking points for interview preparation.

### self_introduction
Write a short, natural interview self-introduction version that reflects:
- my actual ownership
- technical analysis strength
- implementation strength
- coordination strength
- alignment to these role directions:
  - Vue web developer
  - complex web application developer
  - workflow-oriented system builder
  - Middle Office / Middle Platform developer
  - coordinator / cross-functional collaborator

### role_emphasis_prep
Provide metadata for later targeting.
- primary_themes: 2–4 dominant technical tags
- cross_functional_elements: specific coordination examples
- technical_depth_areas: hardest or most valuable technical areas

## Final checks before responding

Before producing JSON, verify:
- both extracted source material and contribution fields were considered
- ownership is accurate
- PM decisions are not attributed to me
- background context is not turned into my implementation claims
- no invented metrics or unsupported claims appear
- internal/project-specific wording has been universalized
- the result is concise, technical, transferable, and suitable for resume + interview use