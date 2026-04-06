# PtoR — Project-to-Resume Analyzer

Convert project materials and job descriptions into interview-ready resume content.

## Setup

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
bash install.sh
```

## Run

**Production (serves frontend + API on port 8000):**
```bash
bash run.sh
```

**Development (hot-reload frontend on port 5173 + backend on port 8000):**
```bash
bash run.sh --dev
```

Open http://localhost:8000 (production) or http://localhost:5173 (dev).

## CLI

```bash
python -m src.cli upload text     # paste project text
python -m src.cli upload file path/to/file.pdf
python -m src.cli upload url https://...
python -m src.cli list
python -m src.cli get <id>
python -m src.cli update <id>
python -m src.cli delete <id>
python -m src.cli match           # paste JD and match against saved projects
```

## Requirements

- Python 3.11+
- Node.js 18+
- Tesseract (optional, for image OCR): `brew install tesseract`
- `ANTHROPIC_API_KEY` in `.env`

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design and layer boundaries.

## Status

| Feature | Status |
|---|---|
| Project upload (text / file / URL / Notion) | ✅ |
| Project analysis (LLM + fallback) | ✅ |
| Project store (CRUD) | ✅ |
| JD upload (text / file / URL) | ✅ |
| JD analysis + requirement extraction | ✅ |
| Project matching + scoring (LLM + fallback) | ✅ |
| Tailored bullet generation | ✅ |
| Vue 3 frontend (Projects + Resume pages) | ✅ |
| REST API | ✅ |
| CLI | ✅ |
