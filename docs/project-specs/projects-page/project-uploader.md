# Project Uploader Feature Design

**Feature:** Project Upload and Analysis
**Page:** Projects Page

---

## 1. Overview

The Project Uploader is the primary entry point for adding new projects. It accepts project materials in multiple formats, collects structured context from the user, runs analysis, and shows an editable preview before saving to the project library.

The uploader is a collapsible panel at the top of the Projects Page. It operates as a two-step flow: input → review & save.

---

## 2. User Flow

### Step 1 — Input and context

1. Click **"+ Add New Project"** to expand the panel
2. Select input type tab: **Text** | **File** | **URL** | **Notion**
3. Provide the source material
4. Fill in the context form (Background / Contributions sections)
5. Click **"Analyze Project"**

### Step 2 — Review and save

1. Tabbed output preview appears (Summary | Highlights | Resume Bullets | Interview)
2. All fields are editable inline before saving
3. Click **"✓ Save to Projects"** — project is prepended to the grid

**Back** returns to Step 1 with all inputs preserved.

---

## 3. Input Types

| Tab | Accepted formats | Notes |
|---|---|---|
| Text | Plain text paste | Direct textarea |
| File | `.pdf`, `.txt`, `.md`, `.html`, `.htm`, `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp` | Drag-and-drop or file picker; multiple files allowed; max 10 MB per file |
| URL | `http://` / `https://` | Fetches and parses page content |
| Notion | Notion page URL | Requires `NOTION_TOKEN` env var |

---

## 4. Context Form

Two accordion sections, each with labeled textareas:

**Background (not your work)**
- Business / project background
- Team / client requirements
- PM product decisions

**Your Contributions**
- T1 responsibilities — scope analysis, API/interface design
- T2 responsibilities — implementation, web development
- Architecture details
- Cross-platform / cross-functional coordination
- Challenges, constraints, tradeoffs
- Outcomes and impact

All fields are optional. More context produces better output.

---

## 5. Analysis Result Preview

Shown in Step 2. Same tabbed layout as the project detail view:

| Tab | Editable content |
|---|---|
| Summary | Summary, ownership description, self-introduction |
| Highlights | Technical highlights list (add / remove items) |
| Resume Bullets | Resume bullet list (add / remove / edit items) |
| Interview | STAR interview answer, talking points list |

A "Preview extracted text" toggle shows the raw extracted text from the source.

---

## 6. Technical Implementation

**Components:**
- `ProjectUploader.vue` — collapsible panel, tab selection, file handling, two-step state
- `ContextForm.vue` — 9-field form in two accordion sections
- `AnalysisResult.vue` — tabbed output preview with inline editing
- `ListEditor.vue` — reusable add/remove/edit list for bullet and highlight arrays

**API calls:**
- `POST /api/analyze` — text / URL / Notion input
- `POST /api/analyze/file` — file upload (multipart)
- `POST /api/projects` — save confirmed analysis

**State (Pinia `projectStore.upload`):**
```
open, activeTab, source, files, context,
analyzing, result, analyzeError
```

---

## 7. Validation

- [ ] All input types parse and return extracted text
- [ ] Context form pre-populates from URL/file metadata where possible
- [ ] Analysis result is editable in all tabs before save
- [ ] Save creates a new project and prepends it to the grid
- [ ] File size > 10 MB shows a clear error
- [ ] Empty input shows a validation error before submitting
