# Product Requirements Document

**Product Name:** Project-to-Resume Analyzer  
**Version:** 0.2  
**Last updated:** 2026-04-03

> **v0.2 implementation status is marked inline:** ✅ Implemented · ⚠️ Changed from original · 🔲 Not yet implemented

---

## 1. Problem Statement

Software engineers with strong project backgrounds often struggle to articulate that experience in ways that resonate with different target roles. The problem is not a lack of experience — it is translating complex, multi-party project work into accurate, role-targeted language without:

- Overclaiming decisions made by PMs or other stakeholders
- Underselling genuine technical contributions
- Rewriting the same content from scratch for every job application

This tool solves that by structuring project knowledge once and generating reusable, role-aligned content on demand.

---

## 2. Target Users

**Primary user:** A software engineer (frontend / full-stack focus) who:
- Has worked on complex, multi-team web projects
- Is actively job searching across roles that may require different framing
- Wants accurate, professional resume content without repeating effort per application

The tool is especially relevant for roles involving:
- Vue / web frontend development
- Complex web application architecture
- Workflow-oriented and process-heavy systems
- Middle office / middle platform development
- Cross-functional coordination between web, mobile, and server teams

---

## 3. Terminology

See [GLOSSARY.md](../GLOSSARY.md) for full definitions.

| Term | Definition |
|---|---|
| **T1 responsibilities** | Technical analysis and planning: scope analysis, platform assessment, API/interface design |
| **T2 responsibilities** | Hands-on implementation: web development, detailed design, feature delivery |
| **Project context** | Background the user provides that is *not* their own work — business background, team/client requirements, PM product decisions |
| **Role-aligned version** | A reframing of the same project for a specific target role, without changing the facts |
| **JD** | Job Description |

---

## 4. Product Goal

Build a tool that converts project materials and job descriptions into interview-ready and resume-ready content through two connected workflows:

1. **Project analysis workflow** — Convert project documents and user-provided context into structured, professional descriptions of experience. ✅ Implemented
2. **Job matching workflow** — Extract requirements from a JD, compare against saved projects, and generate tailored resume content ranked by fit. 🔲 Not yet implemented

---

## 5. Main Use Cases

### Use Case A: Analyze a project ✅

A user provides project materials with structured context.

**Background context (not the user's work):**
- Project background
- Business / team / client requirements
- PM product decisions

**User contributions:**
- T1 responsibilities
- T2 responsibilities
- Architecture involvement
- Cross-platform coordination
- Challenges, constraints, outcomes

**System outputs — all implemented:** ✅
- Professional project summary
- Ownership and responsibility description (user work clearly separated from PM/team decisions)
- Key technical contributions
- Resume-style bullet points
- Interview answer version (STAR format)
- Short self-introduction version
- Interview talking points

**⚠️ Changed from v0.1:** Role-aligned versions (Vue developer, middle office, etc.) are defined in the output schema but the content is not yet role-differentiated. The same output is returned regardless of target role until LLM integration is re-enabled. 🔲

### Use Case B: Match projects to a job description 🔲

Not yet implemented. Planned behavior:
- User uploads a job post
- System extracts key requirements
- Compares against all saved project analyses
- Generates tailored bullet points ranked by fit
- Checks whether the role is similar to an existing saved target (deduplication)

---

## 6. Module Specifications

### Module A: Project Analysis ✅

#### 6.1 Inputs — supported formats ✅

| Format | Status |
|---|---|
| Plain text | ✅ |
| PDF | ✅ |
| Image / screenshot | ✅ OCR via Tesseract |
| HTML file | ✅ |
| URL (website) | ✅ |
| Notion link | ✅ requires `NOTION_TOKEN` env var |

#### 6.2 User-provided context structure ✅

| Field | Ownership |
|---|---|
| Project background | Background — not user work |
| Business / team / client requirements | Background — not user work |
| PM product decisions | Background — not user work |
| T1 responsibilities | User contribution |
| T2 responsibilities | User contribution |
| Architecture details (model, controller, store, view, APIs/interfaces) | User contribution |
| Web / mobile / server coordination | User contribution |
| Challenges, constraints, tradeoffs | User contribution |
| Outcomes and impact | User contribution |

#### 6.3 Outputs ✅

All fields generated and stored per project:

1. Professional project summary
2. Ownership and responsibility description
3. Technical and coordination highlights
4. Resume-style bullet points
5. Interview answer (STAR format)
6. Short self-introduction
7. Interview talking points

**⚠️ Changed from v0.1:** Role-aligned versions listed below are **not yet generated**. The output schema includes a `role_versions` field but it is currently empty. 🔲

- Vue web developer variant
- Complex web application developer variant
- Workflow-oriented system builder variant
- Middle Office / Middle Platform developer variant
- Cross-functional collaborator variant

#### 6.4 Output rules ✅

- Clearly attribute what is user work vs. PM / team decisions
- Do not claim PM product decisions as user work
- Emphasize: technical analysis, platform coordination, API/interface definition, structured web implementation
- Professional, concise, job-search ready

**⚠️ Changed from v0.1:** Output quality is rule-based (keyword extraction + context structuring) rather than LLM-generated prose. Content is accurate but not stylistically polished until LLM is re-connected.

---

### Module B: Job Matching 🔲

Not yet implemented. See original spec below for planned behavior.

#### 6.5 Inputs (planned)

- Plain text, PDF, screenshot, link

#### 6.6 Matching logic (planned)

1. Extract key requirements from the JD: tech stack, collaboration expectations, domain context, seniority signals
2. Compare requirements against all saved project analyses
3. Score each project's fit per requirement dimension
4. Rank projects by overall relevance

#### 6.7 Outputs (planned)

1. Ranked project list with fit scores
2. Per-project tailored bullet points matched to JD requirements
3. Resume-ready output combining top-ranked projects

#### 6.8 Deduplication rule (planned)

When a new JD is uploaded, compare against all existing saved job targets. If highly similar, prompt the user to update or reuse the existing item.

---

## 7. Information Architecture

### A. Projects Page ✅

**Project list** — implemented as a responsive card grid with: ✅
- Project title
- Category badge (color-coded)
- Technical tags
- Summary excerpt
- Created date
- View / Delete actions

**Search and filter** — implemented: ✅
- Real-time text search across title, summary, tags
- Category dropdown filter
- Tag dropdown filter

**Project upload area** — implemented as collapsible panel: ✅
- Input tabs: Text | File | URL | Notion
- Context form (two sections: Background / Contributions)
- Analysis result preview with inline editing before save
- Source text preview ("Preview extracted text")

**Project detail view** — implemented as fixed-size modal: ✅
- Tabs: Source & Context | Summary | Highlights | Resume Bullets | Interview
- Source & Context tab shows raw extracted text + all context fields
- Edit Context button → re-analyze with updated context
- Delete with confirmation

**⚠️ Changed from v0.1 wireframe:** No separate detail page — uses a modal. Inline editing of generated fields is available in the upload/review step, not the modal view step.

### B. Resume Page 🔲

Not yet implemented. Planned:
- JD upload area (text, screenshot, link, PDF)
- JD list with match results
- Deduplication prompt

---

## 8. Data Model

### Project Entity ✅

```
Project
├── id                      (uuid, auto-assigned)
├── created_at              (ISO 8601 UTC)
├── updated_at              (ISO 8601 UTC, on patch)
├── title                   (extracted from first line of input)
├── category                (detected: web_app | mobile | backend | data | devops | platform | other)
├── tags                    (detected: see GLOSSARY.md for full list)
├── summary
├── ownership_description
├── ownership_classification
│   ├── background
│   ├── t1_contribution
│   ├── t2_contribution
│   ├── coordination
│   └── outcome
├── technical_highlights    (string[])
├── resume_bullets          (string[])
├── interview_answer        (STAR format)
├── self_intro
├── talking_points          (string[])
├── context                 (the 9 user-provided form fields)
├── raw_text                (full extracted source text)
└── source_metadata         (filename | url | pages | size)
```

**⚠️ Not yet stored (planned in v0.1 schema):**
- `role_versions` — role-aligned variant content keyed by role type 🔲
- `edit_history` — append-only log of `{ timestamp, content, source: 'ai' | 'user' }` per section 🔲
- `source_materials[]` — list of multiple source files per project 🔲

### Job Description Entity 🔲

Not yet implemented. Planned schema in original PRD §8 unchanged.

---

## 9. Functional Requirements

### 9.1 Project Analysis Engine ✅

- ✅ Parse and extract text from: plain text, images (OCR), PDFs, Notion links, HTML files, URLs
- ✅ Classify extracted content by ownership type using user-provided context form
- ✅ Identify technical themes via keyword matching
- ✅ Generate all output formats from a single structured project record
- ⚠️ Content classification is form-driven, not LLM-inferred — no gap-filling for missing context

### 9.2 Job Matching Engine 🔲

Not yet implemented.

### 9.3 Editing and Reuse ✅ / 🔲

- ✅ All generated sections editable inline during the upload/review step
- ✅ One canonical project record per project; accessed via project list
- ✅ Re-analysis available via "Edit Context" in the detail modal
- 🔲 Bullet-point library (cross-referenced across JD targets) — not yet implemented
- 🔲 Edit history per output section — not yet implemented

---

## 10. User Flows

### Flow 1: Add a project ✅

1. Click "Add New Project" in the upload panel
2. Select input type tab (Text / File / URL / Notion)
3. Provide source material
4. Fill in context form (Background + Contributions sections)
5. Click "Analyze Project" — rule-based analysis runs instantly
6. Review all output fields in the tabbed result panel; edit inline as needed
7. Click "✓ Save to Projects" — project appears in the grid

### Flow 2: View and edit a project ✅

1. Click a project card → detail modal opens
2. Browse tabs: Source & Context | Summary | Highlights | Resume Bullets | Interview
3. Click "Edit Context" → context form opens pre-filled
4. Edit fields → "Save with Re-analysis" → all output fields regenerated

### Flow 3: Add a job description 🔲

Not yet implemented.

### Flow 4: Reuse for a new role 🔲

Not yet implemented.

---

## 11. Non-Functional Requirements

### Privacy and data security ✅

- All project data stored locally in `data/projects.json`
- No project content sent to any third party (no LLM calls currently)
- Notion integration only calls the Notion API when user provides a Notion URL with explicit `NOTION_TOKEN`

### Accuracy guardrails ✅

- Generated content is grounded in user-provided material — no invented contributions
- Ownership classification is driven by the context form, not inferred

### Performance targets

- ✅ Project analysis: < 1 second (rule-based, no network calls)
- ✅ Project list render: < 2 seconds
- 🔲 LLM-based analysis target: ≤ 30 seconds when re-connected
- 🔲 JD matching against 20 projects: ≤ 15 seconds (when implemented)

---

## 12. Product Principles (unchanged)

**Accuracy first** — Do not inflate ownership. Clearly separate PM decisions, team decisions, and user contributions.

**Evidence-based writing** — Generated content derives from actual project material and user-provided context.

**Structured reuse** — A project is analyzed once, then reused across many target jobs.

**Role-oriented output** — The same project can be reframed for different roles without changing the facts.
