# Architecture

**Product:** Project-to-Resume Analyzer

> Related documents:
> - Product requirements: [project-specs/product-requirements.md](project-specs/product-requirements.md)
> - Output schema: [project-specs/OUTPUT-SCHEMA.md](project-specs/OUTPUT-SCHEMA.md)
> - Glossary: [GLOSSARY.md](GLOSSARY.md)
> - Data model: [project-specs/data-model.md](project-specs/data-model.md)
> - API endpoints: [project-specs/api-endpoints.md](project-specs/api-endpoints.md)

---

## 1. Purpose

This system supports two related workflows:

1. **Project analysis**
   Turn project materials into structured project records that can be reused for resume writing, interview preparation, and job-description matching.

2. **Job description analysis**
   Turn job descriptions into structured requirement records that can be reused for project matching and tailored resume output generation.

Both workflows share the same core architecture:

- normalize all inputs into a common structure
- extract structured signals from text using layered analysis logic
- persist records in JSON-backed stores
- expose functionality through REST APIs, CLI commands, and a Vue frontend

The two workflows diverge after normalization:

- the **project pipeline** focuses on contribution analysis, ownership clarity, and reusable project narratives
- the **JD pipeline** focuses on requirement extraction, deduplication, and downstream project matching

---

## 2. High-Level Architecture

### 2.1 Project Analysis Pipeline

```text
Project materials (text / file / URL / Notion)
    ↓
Input Parser
    ↓
Normalized source object + provenance map
    ↓
User context form
    ↓
Project Analyzer
    ↓
Structured project record
    ↓
Project Store
    ↓
Application Services
    ↓
REST API / CLI / Vue UI
````

### 2.2 Job Description Analysis Pipeline

```text
Job description (text / file / URL / Notion)
    ↓
Input Parser
    ↓
Normalized source object + provenance map
    ↓
JD Analyzer
    ↓
Structured JD target record
    ↓
JD Store
    ↓
Matching / Scoring Engine
    ↓
Ranked matches + tailored output candidates
    ↓
Application Services
    ↓
REST API / CLI / Vue UI
```

### 2.3 Shared Supporting Layers

```text
User Profile Store
    ↓
Matching / Scoring Engine

Shared Storage Layer
Shared Application Services Layer
Shared Delivery Interfaces
```

---

## 3. Core Architectural Principles

1. **Normalized input first**
   Every supported source is converted into the same internal structure before analysis begins.

2. **Local-first persistence, remote-capable ingestion**
   Core records are stored locally in JSON-backed files, while ingestion may read from remote sources such as URLs and Notion.

3. **Separation of source evidence and user context**
   Source text provides evidence. User-supplied context clarifies ownership, intent, scope, and impact.

4. **Ownership clarity for project analysis**
   Background information is stored separately from the user’s actual contributions.
   When extracted source text and user-provided contribution context differ, user-provided contribution context is treated as the primary attribution source.

5. **Structured outputs over free-form generation**
   The system produces fixed-schema records for reliable storage, retrieval, comparison, and downstream generation.

6. **Evidence-based generation**
   Generated summaries, bullets, highlights, and matching outputs should remain traceable to parsed source material and user-provided context.

7. **Single business-logic path across interfaces**
   REST API, CLI, and frontend should rely on the same application service boundaries so behavior remains consistent across interfaces.

---

## 4. System Layers

## 4.1 Input Parsing Layer

**Module:** `src/parser.py`

The parser converts all supported inputs into a single normalized structure.

### Normalized Output Contract

```json
{
  "raw_text": "string",
  "source_type": "text | file | url | notion",
  "source_reference": "filename | URL | page_id",
  "metadata": {},
  "provenance": {
    "segments": [
      {
        "segment_id": "string",
        "text": "string",
        "location": {
          "page": 1,
          "section": "Overview",
          "offset_start": 0,
          "offset_end": 120
        }
      }
    ]
  }
}
```

### Supported Inputs

| Input Type                                        | Parsing Method                          |
| ------------------------------------------------- | --------------------------------------- |
| Plain text                                        | pass-through                            |
| PDF                                               | `pdfplumber`                            |
| `.txt` / `.md`                                    | `Path.read_text()`                      |
| `.html` / `.htm`                                  | `BeautifulSoup` with content extraction |
| Images (`.jpg`, `.png`, `.bmp`, `.tiff`, `.webp`) | OCR via Tesseract + Pillow              |
| URL                                               | `requests` + `BeautifulSoup`            |
| Notion page URL                                   | Notion API block traversal              |

### Responsibility

This layer is responsible only for ingestion, normalization, and provenance capture.

It does **not**:

* classify content
* score fit
* generate final structured records
* make persistence decisions

---

## 4.2 Project Analysis Layer

**Module:** `src/analyzer.py`

This layer converts normalized project content plus user context into structured project records.

### Responsibilities

* separate background context from user contributions
* derive project tags and category
* generate reusable project summaries, bullets, and highlights
* produce interview-prep artifacts
* preserve evidence links between source material, user context, and generated outputs
* attach role-emphasis metadata for later reframing

### Inputs

* normalized project source object
* user-provided context form

### Outputs

* structured project analysis record
* reusable summary, bullets, and highlights
* short self-introduction
* interview-prep artifacts
* role-emphasis metadata
* evidence references for generated fields

### Important Boundary

This layer generates **project-centric reusable content**.

It does **not** generate JD-specific final recommendations or ranking decisions.
Any **tailored bullet candidates** produced for a specific job description belong to the matching layer, not the project analyzer.

---

## 4.3 Job Description Analysis Layer

**Module:** `src/jd_analyzer.py`

This layer converts a normalized job description into structured requirement signals.

### Extracted Signal Types

1. `tech_stack`
2. `collaboration_signals`
3. `domain_context`
4. `seniority_signals`
5. `role_category`

### Additional Responsibilities

* normalize JD language into reusable comparison fields
* identify duplicate or overlapping JD targets where relevant
* preserve evidence references for extracted requirement signals

### Responsibility Boundary

This layer does **not** evaluate saved projects directly.
Its role is to transform raw JD text into structured requirements that can later be compared against saved project records.

---

## 4.4 Matching and Scoring Layer

**Module:** `src/matcher.py` *(or equivalent matching module)*

This layer compares a JD target record against saved project records.

### Inputs

* JD extracted requirements
* saved project records
* project tags, category, and analysis content
* user profile data from `data/user_profile.json`

### Outputs

* ranked project matches
* fit score
* score breakdown
* tailored bullet candidates for a specific JD
* optional deduplication and comparison metadata

### Scoring Dimensions

The matching layer ranks saved projects using multiple fit dimensions derived from the JD target, project records, and candidate profile context.

### Seniority Alignment Input

`seniority_alignment` is computed from the relationship between:

* JD seniority expectations
* candidate profile information in `data/user_profile.json`

This alignment reflects candidate-level fit signals such as:

* education
* years of experience
* self-described level

It is separate from project depth and project evidence.

### Tailored Output Boundary

This layer may generate **JD-specific tailored bullet candidates** by transforming or selecting from project analysis outputs in light of the JD target.

That makes the distinction explicit:

* **project analyzer** → reusable project bullets
* **matching layer** → job-specific tailored bullet candidates

---

## 4.5 Profile and Configuration Layer

**Files / Modules:** `data/user_profile.json` and related loaders

This layer provides persistent candidate-level context used across matching and tailoring workflows.

### Responsibilities

* store reusable candidate profile data
* expose profile signals to matching logic
* separate candidate-level facts from project-level facts and JD-level facts

### Example Profile Fields

* years of experience
* education
* target seniority
* preferred role category
* optional domain preferences

### Boundary

This layer does **not** parse project materials or JDs.
It provides supporting context to downstream scoring and tailoring logic.

---

## 4.6 Storage Layer

**Modules:** `src/store.py`, `src/jd_store.py`, and optional profile/config loaders

The storage layer persists structured records in append-oriented JSON files.

### Project Store

**File:** `data/projects.json`

Provides operations for:

* loading projects
* saving a project
* retrieving a project
* updating a project
* deleting a project

### JD Store

**File:** `data/jd_targets.json`

Provides operations for:

* saving JD targets
* retrieving JD targets
* updating JD targets
* deleting JD targets
* storing deduplication metadata
* storing match result references or embedded match snapshots, depending on implementation

### Optional Match Storage

If match outputs are persisted separately, they should be stored in an explicit file such as:

* `data/matches.json`

If match outputs are embedded into JD target records, the data model should define:

* ranking result shape
* score breakdown shape
* tailored output shape
* timestamp / invalidation metadata

### Storage Role in the Architecture

The storage layer is the persistence boundary between analysis logic and delivery interfaces.

It allows the same records to be used consistently by:

* REST API
* CLI
* frontend UI

---

## 4.7 Application Services Layer

**Suggested Modules:** service-level orchestration modules between interface layers and core logic

This layer coordinates multi-step workflows across parser, analyzer, matcher, and storage components.

### Responsibilities

* orchestrate upload → parse → analyze → save flows
* orchestrate JD parse → analyze → match → persist flows
* enforce consistent business behavior across API and CLI
* isolate interface concerns from domain logic

### Why This Layer Exists

Without a shared service layer, API and CLI may evolve into separate orchestration paths with inconsistent validation, persistence behavior, or output formatting.

This layer provides a single business-logic path across interfaces.

---

## 4.8 API Layer

**Module:** `src/api.py`

The API layer exposes parsing, analysis, retrieval, persistence, and matching functions.

### Responsibilities

* route client requests to application services
* enforce service boundaries between clients and backend modules
* provide stable API contracts for project and JD workflows

For detailed endpoint definitions, see `project-specs/api-endpoints.md`.

### API Role in the Architecture

The API is the service boundary used by the frontend and any external client that needs structured access to the system.

It should call shared application services rather than reimplement workflow logic.

---

## 4.9 CLI Layer

**Module:** `src/cli.py`

The CLI provides direct workflows on top of the same application services used by the API.

### Core Commands

| Command       | Purpose                                         |
| ------------- | ----------------------------------------------- |
| `upload`      | parse input, collect context, analyze, and save |
| `list`        | list saved projects                             |
| `get <id>`    | retrieve one project                            |
| `update <id>` | edit context and re-run analysis                |
| `delete <id>` | remove a project                                |
| `match`       | analyze a JD and rank saved projects            |

### CLI Role in the Architecture

The CLI is an alternative interface to the same core services used by the API and frontend.

It should not bypass shared orchestration logic.

---

## 4.10 Frontend Layer

**Stack:** Vue 3 + Pinia + Vite

The frontend provides the user-facing workflow for:

* uploading project materials
* entering context
* reviewing generated project results
* browsing saved projects
* uploading job descriptions
* reviewing matched projects and tailored outputs

### Component Structure

```text
App.vue
├─ ProjectsPage
│  ├─ ProjectUploader
│  │  ├─ ContextForm
│  │  └─ AnalysisResult
│  └─ ProjectGrid
│     └─ ProjectCard
│
└─ ResumePage
   ├─ JDUploader
   │  ├─ FormatSelector
   │  ├─ DeduplicationPrompt
   │  └─ MatchingResults
   └─ JDList
      ├─ JDCard
      └─ CustomResumeItem
```

### Frontend Role in the Architecture

The frontend is a presentation layer over the REST API.

It does **not** own:

* parsing logic
* storage rules
* scoring logic
* business orchestration

---

## 5. End-to-End Data Flow

## 5.1 Project Analysis Flow

```text
User submits project material
    ↓
Parser normalizes the source and captures provenance
    ↓
User provides context
    ↓
Project analyzer separates background from contributions
    ↓
Project analyzer classifies tags/category
    ↓
Project analyzer generates reusable structured outputs
    ↓
Project record is saved
    ↓
Record becomes available through services, API, CLI, and UI
```

## 5.2 Job Matching Flow

```text
User submits job description
    ↓
Parser normalizes the source and captures provenance
    ↓
JD analyzer extracts requirement signals
    ↓
Saved projects are loaded from project store
    ↓
User profile is loaded from profile store
    ↓
Matching layer scores each project
    ↓
Ranked results and tailored output candidates are produced
    ↓
Results are stored or attached to JD target records
    ↓
Frontend / API / CLI displays fit results and tailored outputs
```

---

## 6. Data Model

Detailed data model definitions are maintained in `project-specs/data-model.md`.

This data model should include the persistent shapes for:

* project records
* JD target records
* match results or embedded match snapshots
* section-level evidence references
* ownership boundaries
* profile data dependencies where required

---

## 7. Architectural Boundaries

To keep the system understandable and maintainable, each layer has a distinct responsibility.

| Layer                | Owns                                                   | Does Not Own                                |
| -------------------- | ------------------------------------------------------ | ------------------------------------------- |
| Parser               | ingestion, normalization, provenance capture           | generation, scoring, persistence decisions  |
| Project Analyzer     | ownership mapping, tagging, reusable project outputs   | persistence, JD-specific ranking            |
| JD Analyzer          | requirement extraction, JD signal structuring          | project scoring logic                       |
| Matching Layer       | project-to-JD comparison, fit scoring, tailored output | raw parsing, generic project analysis       |
| Profile Layer        | candidate-level context                                | project parsing, JD extraction              |
| Storage              | persistence and retrieval                              | UI or business interpretation               |
| Application Services | workflow orchestration and consistency across clients  | interface presentation                      |
| API                  | service access                                         | core domain logic                           |
| CLI                  | command-line interaction                               | storage internals, duplicated orchestration |
| Frontend             | presentation and user interaction                      | backend analysis, scoring, persistence      |
