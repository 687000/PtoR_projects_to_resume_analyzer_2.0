# Project-to-Resume Analyzer

Convert your project experience into interview-ready resume content, and match it against job descriptions to generate tailored resume bullets.

- **Projects page** — upload project materials, get structured output (summary, resume bullets, STAR answer, talking points), saved to a local library
- **Resume page** — paste a job description, match it against your saved projects, edit and copy tailored bullets per role


## Requirements

- **Python 3.12+** and **Node.js 16+**
- System dependency for image OCR: `brew install tesseract`

---

## Setup

**1. Install dependencies (first time only):**
```
bash ./install.sh
```

**2. Copy the env file and fill in any optional tokens:**
```
bash cp .env.example .env
```

| Variable | Required | Purpose |
|---|---|---|
| `NOTION_TOKEN` | Only for Notion links | Notion integration token — see [notion.so/my-integrations](https://www.notion.so/my-integrations) |

---

## Running the app

```
bash ./run.sh
```

Opens at **http://localhost:5173**. Press `Ctrl+C` to stop both servers.

> `run.sh` starts the FastAPI backend on port 8000 and the Vue dev server on port 5173.

To start the backend only:
```bash
uvicorn src.api:app --reload --port 8000
```

---

## Usage

### Projects page

Upload project materials in any format, fill in a context form (background vs. your contributions), review the generated output, and save to your project library.

**Supported input types:**
- Plain text paste
- File upload: `.pdf`, `.txt`, `.md`, `.html`, `.htm`, `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp`
- URL (fetches and parses the page)
- Notion page URL (requires `NOTION_TOKEN` in `.env`)

**Output per project:**

| Field | Description |
|---|---|
| `summary` | Structured from your T1/T2 contributions and outcomes |
| `ownership_description` | Separates your work from business context and PM decisions |
| `technical_highlights` | Keyword-dense sentences extracted from your input |
| `resume_bullets` | Action-verb sentences from your contributions |
| `interview_answer` | STAR format (Situation / Task / Action / Result) |
| `self_intro` | One-liner for quick introductions |
| `talking_points` | Key themes for interview discussion |

---

### Resume page

Upload a job description (text, file, or URL), see matched projects ranked by fit score, edit the tailored bullets, and copy the resume section to clipboard.

**Fit scoring** (per project):

| Dimension | Weight |
|---|---|
| Tech stack overlap | 40% |
| Domain relevance | 25% |
| Collaboration signals | 20% |
| Seniority alignment | 15% |

If the new JD is highly similar to one you already saved (≥ 70% requirement overlap), you'll be prompted to update the existing target instead of creating a duplicate.

---

## Data storage

All data is stored locally:

| File | Contents |
|---|---|
| `data/projects.json` | Saved project analyses |
| `data/jd_targets.json` | Saved job targets with match results |

Nothing is sent to external services unless you use a Notion link (calls the Notion API) or a URL (fetches the page).

---

## Run tests

```bash
python3 -m pytest tests/ -v
```

---

## Changelog

### 2026-04-04
- Resume page: JD upload, project matching with fit scores, tailored bullet editor, copy to clipboard
- `src/jd_analyzer.py` — JD requirement extraction and project scoring
- `src/jd_store.py` — local storage for JD targets (`data/jd_targets.json`)
- New API routes: `GET/POST/PATCH/DELETE /api/jd-targets`, `POST /api/jd/analyze`

### 2026-04-03
- Vue 3 frontend with project grid, upload panel, detail modal, and CRUD
- FastAPI REST backend (`src/api.py`) exposing `/api/projects` and `/api/analyze`
- Added image OCR support (`.jpg`, `.png`, and other image formats via Tesseract)
- Added HTML file parsing (`.html`, `.htm`)
- Added URL/website scraping
- Added Notion page support via Notion API
- Replaced LLM-based analysis with rule-based keyword extraction (no API key required)
