# Technical Architecture

**Product:** Project-to-Resume Analyzer  
**Last updated:** 2026-04-03  
**Version:** 0.2 — reflects current implementation

> For product requirements and user flows, see [project-specs/product-requirements.md](project-specs/product-requirements.md).  
> For term definitions, see [GLOSSARY.md](GLOSSARY.md).

---

## 1. System Overview

```
User input (file / text / URL / Notion)
        │
        ▼
  Input Parser  (src/parser.py)
        │
        ▼
  Rule-Based Analyzer  (src/analyzer.py)
        │
        ▼
  Structured Project Record
        │
        ├── FastAPI REST API  (src/api.py)
        │         │
        │         ▼
        │    Vue 3 Web UI  (frontend/)
        │
        └── CLI  (src/cli.py)
                  │
                  ▼
            Project Store  (src/store.py → data/projects.json)
```

Job Matching pipeline is **not yet implemented**.

---

## 2. Components

### 2.1 Input Parser — `src/parser.py` ✅

Normalizes all input into `{ raw_text, source_type, metadata }`.

| Input type | Extraction method | Status |
|---|---|---|
| Plain text | Pass-through | ✅ |
| PDF | pdfplumber | ✅ |
| `.txt` / `.md` file | `Path.read_text` | ✅ |
| `.html` / `.htm` file | BeautifulSoup — strips `<script>`, `<style>`, `<nav>`; prefers `<article>` / `<main>` | ✅ |
| Image (`.jpg`, `.png`, `.bmp`, `.tiff`, `.webp`) | Tesseract OCR via pytesseract + Pillow | ✅ |
| URL (`http://` / `https://`) | requests + BeautifulSoup | ✅ |
| Notion page URL | Notion API block traversal — requires `NOTION_TOKEN` env var | ✅ |

**⚠️ Change from v0.1:** PDF-only was the original scope. All 6 input types are now implemented.

---

### 2.2 Project Analysis Pipeline — `src/analyzer.py` ⚠️

**⚠️ Change from v0.1:** The spec called for an LLM (GPT-4o via `src/ai/client.py`). The current implementation uses rule-based extraction. `src/ai/client.py` remains present but is not called.

**Stage 1 — Content classification**  
Context fields are provided directly by the user via the context form. No LLM inference is done. Fields are mapped 1:1 to ownership buckets:

| Context field | Ownership bucket |
|---|---|
| `business_background`, `team_client_requirements`, `pm_decisions` | `background` |
| `t1_responsibilities` | `t1_contribution` |
| `t2_responsibilities` | `t2_contribution` |
| `coordination` | `coordination` |
| `outcomes` | `outcome` |

**Stage 2 — Technical theme tagging**  
Keywords matched against the combined text (raw_text + all context fields). See `GLOSSARY.md` for the full tag list.

**Stage 3 — Output generation**  
All output fields are assembled from context values and keyword-extracted sentences — no LLM prose generation. Fields that benefit most from LLM (summary polish, role-aligned versions) produce structured-but-plain output until LLM integration is re-enabled.

**🔲 Not yet implemented:** Role-aligned versions (Vue developer, middle office, etc.) — structure exists in the output schema but content is not differentiated by role.

---

### 2.3 REST API — `src/api.py` ⚠️ (new)

**⚠️ Not in v0.1 spec.** Added to serve the Vue frontend.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/projects` | List all saved projects |
| `GET` | `/api/projects/{id}` | Get one project |
| `POST` | `/api/analyze` | Parse text/URL + analyze (no save) |
| `POST` | `/api/analyze/file` | Parse uploaded file + analyze (no save) — max 10 MB |
| `POST` | `/api/projects` | Save a confirmed analysis result |
| `PATCH` | `/api/projects/{id}` | Update context; optionally re-analyze |
| `DELETE` | `/api/projects/{id}` | Delete a project |

CORS: `ALLOWED_ORIGIN` env var (default `http://localhost:5173`).

---

### 2.4 Project Store — `src/store.py` ✅

**⚠️ Change from v0.1:** Spec mentioned SQLite as an option. Current implementation is JSON only.

- Storage path: `data/projects.json` (append list, pretty-printed)
- Operations: `load_projects`, `save_project`, `get_project`, `update_project`, `delete_project`
- `update_project` merges fields and adds `updated_at` timestamp
- The `api.py` overrides `STORE_PATH` to an absolute path at import time so the server can be launched from any working directory

**🔲 Not yet implemented:** Edit history per output section (append-only log of `{timestamp, content, source}`).

---

### 2.5 CLI — `src/cli.py` ✅

Five commands, all operating directly on the store without the API server:

| Command | Description |
|---|---|
| `upload --file / --text / --url` | Parse → interactive context form → analyze → confirm → save |
| `list` | Print all saved projects |
| `get <id>` | Print full detail for one project |
| `update <id>` | Re-open context form (pre-filled) → re-analyze → confirm → save |
| `delete <id>` | Confirm and delete |

---

### 2.6 Job Matching Pipeline 🔲

**Not yet implemented.** Planned stages:

1. **JD extraction** — parse job description into `{ tech_stack, collaboration_requirements, domain_context, seniority_signals, role_category }`
2. **Scoring** — per-project fit score across requirement dimensions
3. **Output generation** — tailored bullets ranked by relevance; weak matches flagged

---

## 3. Data Storage

### File layout

```
data/
└── projects.json     ← append list of project records
```

### Project record schema

```
{
  id:                    uuid string
  created_at:            ISO 8601 UTC
  updated_at:            ISO 8601 UTC  (only if patched)
  title:                 string
  category:              web_app | mobile | backend | data | devops | platform | other
  tags:                  string[]
  summary:               string
  ownership_description: string
  ownership_classification: {
    background, t1_contribution, t2_contribution, coordination, outcome
  }
  technical_highlights:  string[]
  resume_bullets:        string[]
  interview_answer:      string
  self_intro:            string
  talking_points:        string[]
  context: {             ← the 9 context form fields as provided by the user
    business_background, team_client_requirements, pm_decisions,
    t1_responsibilities, t2_responsibilities, architecture_details,
    coordination, challenges, outcomes
  }
  raw_text:              string   ← full extracted text from the source
  source_metadata:       { filename? | url? | pages? | size? }
}
```

**⚠️ Change from v0.1:** `role_versions` (keyed by role type) and `edit_history` per section are in the PRD schema but not yet stored.

---

## 4. Frontend — `frontend/` ⚠️ (new)

**⚠️ Not in v0.1 spec.**

**Stack:** Vue 3 (Composition API) + Pinia + Vite 4. No UI component library.

### Component map

```
App.vue
└── ProjectsPage layout
    ├── ProjectUploader.vue      ← collapsible; owns two-step upload flow
    │   ├── ContextForm.vue      ← 9-field form in two accordion sections
    │   └── AnalysisResult.vue   ← tabbed output preview; editable before save
    │       └── ListEditor.vue   ← reusable add/remove list for bullet arrays
    ├── ProjectGrid.vue          ← search + category/tag filter; renders card grid
    │   └── ProjectCard.vue      ← title, category, tags, summary; inline delete confirm
    └── ProjectModal.vue         ← fixed-size detail view; Source & Context tab; edit mode
        └── ContextForm.vue      ← reused for re-analyze edit mode
```

**⚠️ Change from v0.1 planned component names:**

| v0.1 planned name | Actual name |
|---|---|
| `UploadHandler.vue` | `ProjectUploader.vue` |
| `ResultsEditor.vue` | `AnalysisResult.vue` |
| `AnalysisProgress.vue` | Spinner inside `ProjectUploader.vue` — no separate component |
| `SearchFilters.vue` | Inline in `ProjectGrid.vue` |
| `ListControls.vue` | Inline in `ProjectGrid.vue` |

### Pinia store — `stores/projects.js`

Three state domains:

```js
{
  projects: [],          // full list from GET /api/projects

  upload: {
    open, activeTab,     // 'text' | 'file' | 'url' | 'notion'
    source, file,        // input values
    context,             // 9 context fields
    analyzing, result,   // analysis in-flight + result before save
    analyzeError,
  },

  modal: {
    open, project,       // project being viewed
    editing,             // context edit mode
    editContext,         // edited copy of context
    reanalyzing,
    deleteConfirm,
  },

  search: { query, category, tag },
}
```

Computed getters: `filteredProjects`, `allCategories`, `allTags`.

### Upload flow (two-step, no auto-save)

```
Step 1: Input + context form
  → user picks tab (text/file/url/notion)
  → fills ContextForm
  → clicks "Analyze Project"
  → POST /api/analyze or /api/analyze/file
  → result stored in upload.result

Step 2: Review (AnalysisResult.vue)
  → all output fields editable inline
  → "Preview extracted text" shows raw_text
  → sticky save bar with "✓ Save to Projects"
  → POST /api/projects
  → project prepended to projects[]
  → uploader resets
```

**🔲 Not yet implemented:**
- Drag-and-drop card reordering
- Bulk select / bulk delete
- Virtual scrolling for large lists (>50 projects)
- Export (JSON / PDF summary)

---

## 5. LLM Integration — `src/ai/client.py` ⚠️

**⚠️ Change from v0.1:** The original spec planned all analysis through `complete_json()` (OpenAI GPT-4o). The current analyzer bypasses this entirely.

The adapter is retained and functional — it can be re-connected by replacing the `analyze_project` function body in `src/analyzer.py` with a call to `complete_json(prompt)`.

**🔲 Planned re-connection path:**
1. Restore `_build_prompt` in `analyzer.py`
2. Call `complete_json(prompt, max_tokens=4096)`
3. Pass result through `_validate`
4. Set `OPENAI_API_KEY` in `.env`

---

## 6. Key Engineering Constraints (unchanged)

- **No fabrication:** Generated content must reference user-provided material
- **Ownership labeling:** Background context and user contributions must remain clearly separated
- **Local-first:** All data stored locally; no cloud sync without explicit user action
- **Performance targets:** Analysis ≤ 30 s; project list rendering ≤ 2 s
