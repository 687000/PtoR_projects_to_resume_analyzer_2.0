# API Endpoints

**Module:** `src/api.py`

This document defines the REST API endpoint surface for project and job description workflows.

## Project Endpoints

| Method   | Path                 | Purpose                                    |
| -------- | -------------------- | ------------------------------------------ |
| `GET`    | `/api/projects`      | list all projects                          |
| `GET`    | `/api/projects/{id}` | get a single project                       |
| `POST`   | `/api/analyze`       | analyze text or URL without saving         |
| `POST`   | `/api/analyze/file`  | analyze uploaded file without saving       |
| `POST`   | `/api/projects`      | save a project record                      |
| `PATCH`  | `/api/projects/{id}` | update a project and optionally re-analyze |
| `DELETE` | `/api/projects/{id}` | delete a project                           |

## JD Endpoints

| Method   | Path                   | Purpose                     |
| -------- | ---------------------- | --------------------------- |
| `GET`    | `/api/jd-targets`      | list all JD targets         |
| `GET`    | `/api/jd-targets/{id}` | get a single JD target      |
| `POST`   | `/api/jd-targets`      | save a JD target            |
| `POST`   | `/api/jd/analyze`      | analyze a JD without saving |
| `POST`   | `/api/jd/match`        | match JD against projects   |
| `POST`   | `/api/jd/{jd_id}/projects/{project_id}/generate-bullets` | generate tailored bullets for specific project |
| `PATCH`  | `/api/jd-targets/{id}` | update a JD target          |
| `DELETE` | `/api/jd-targets/{id}` | delete a JD target          |

## Tailored Bullets Endpoint

**Endpoint:** `POST /api/jd/{jd_id}/projects/{project_id}/generate-bullets`

**Purpose:** Generate JD-specific tailored resume bullets for a matched project using LLM.

**Request Body:**
```json
{
  "count": 2  // optional, defaults to 2, max 3
}
```

**Response:**
```json
{
  "tailored_bullets": [
    {
      "bullet": "string",
      "addresses": ["tech_stack", "domain"],
      "source_references": ["resume_bullets[0]", "technical_highlights[2]"],
      "reasoning": "string"
    }
  ],
  "generation_notes": "string"
}
```

**Requirements:**
- `ANTHROPIC_API_KEY` environment variable must be set
- JD target and project must exist
- Project must be matched against the JD

## Notes

The API layer is the service boundary between frontend/CLI clients and the backend logic. It routes parsing, analysis, storage, and matching requests to the appropriate modules.