# Glossary

Terms used throughout this project and its generated content.

---

## Ownership & Contribution Types

**T1 Responsibilities**
Technical analysis and planning work that happens *before* implementation. Includes: scope analysis, platform/skill assessment, implementation estimation, cross-platform behavior definition, API and interface design.

**T2 Responsibilities**
Hands-on implementation work. Includes: web development, component implementation, detailed design, feature delivery, bug fixing.

**Project Context (Background)**
Information about a project that is *not* the engineer's own work — business background, team or client requirements, PM product decisions. This content is recorded for accuracy but is not attributed to the engineer in generated output.

**Ownership Classification**
The system's separation of a project record into what belongs to the engineer (T1, T2, coordination, outcomes) vs. what is background context (business requirements, PM decisions). Prevents over-claiming and under-claiming in resume content.

---

## Output Formats

**Role-Aligned Version**
A reframing of the same project for a specific target role (e.g. Vue web developer, middle office developer) without changing the underlying facts. Same evidence, different emphasis.

**Resume Bullet**
A single accomplishment statement beginning with a strong action verb, grounded in specific project evidence. Format: `[Action verb] + [what you did] + [impact/result]`.

**STAR Answer (Interview Answer)**
A structured response to "tell me about a project" using: **S**ituation, **T**ask, **A**ction, **R**esult. Generated from the ownership classification and outcome fields.

**Talking Points**
Short phrases for interview discussions. Each point maps to a detected technical theme or a specific challenge/outcome from the project context.

**Self-Introduction**
A 1–2 sentence version of the project suitable for quick introductions or the "about me" portion of an interview.

---

## Analysis Tags

Tags are detected by keyword matching against the uploaded content and context fields.

| Tag | Meaning |
|---|---|
| `vue_web` | Vue.js frontend development (Vue 2 or 3) |
| `state_store_design` | State management design — Pinia, Vuex, Redux |
| `frontend_architecture` | Frontend architecture decisions — React, Angular, component system design |
| `api_interface_definition` | Defining REST APIs, GraphQL schemas, or cross-service interfaces |
| `workflow_complexity` | Complex workflow design — multi-step processes, BPMN, pipeline architecture |
| `platform_coordination` | Cross-platform coordination — web + mobile + server collaboration |
| `middle_office` | Middle-office or middle-platform systems — internal tooling, shared platforms, middleware |
| `cross_functional` | Cross-functional team collaboration — working across design, product, QA, or other engineering teams |

---

## Project Categories

Categories are auto-detected from keyword frequency in the uploaded content.

| Category | Description |
|---|---|
| `web_app` | Frontend or full-stack web applications |
| `mobile` | iOS, Android, or cross-platform mobile |
| `backend` | Server-side systems, APIs, databases |
| `data` | Analytics, ML, data pipelines, ETL |
| `devops` | CI/CD, infrastructure, cloud, containers |
| `platform` | Internal platforms, middleware, shared frameworks |
| `other` | No dominant category detected |

---

## Input Sources

| Source Type | How it works |
|---|---|
| Plain text | Passed directly to the analyzer |
| PDF | Text extracted page-by-page via pdfplumber |
| Image / screenshot | OCR via Tesseract (requires `brew install tesseract`) |
| HTML file | Tags stripped via BeautifulSoup; prefers `<article>` or `<main>` content |
| URL | Fetched with requests, HTML stripped same as above |
| Notion page | Fetched via Notion API block traversal; requires `NOTION_TOKEN` in `.env` |

---

## Job Description (JD)

A job posting uploaded by the user to trigger the **Job Matching** workflow. The system extracts requirements, scores saved projects by fit, and generates tailored resume output ranked by relevance. *(Job matching is a planned module — not yet implemented.)*
