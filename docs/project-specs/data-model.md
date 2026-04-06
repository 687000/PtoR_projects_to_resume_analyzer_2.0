# Data Model

This document defines the persistent record shapes used by the system.

## Project Record

A project record is the main persistent object in the system.

```json
{
  "id": "uuid",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601",
  "title": "string",
  "category": "web_app | mobile | backend | data | devops | platform | other",
  "tags": ["string"],
  "source": {
    "source_type": "text | file | url | notion",
    "raw_text": "string",
    "source_reference": "string"
  },
  "context": {
    "background": {
      "business_background": "string",
      "team_client_requirements": "string",
      "pm_product_decisions": "string"
    },
    "contributions": {
      "t1_responsibilities": "string",
      "t2_responsibilities": "string",
      "architecture_details": "string",
      "cross_functional_coordination": "string",
      "challenges_constraints_tradeoffs": "string",
      "outcomes_impact": "string"
    }
  },
  "analysis": {
    "summary": "string",
    "summary_bullet": "string",
    "ownership_description": "string",
    "self_introduction": "string",
    "resume_bullets": ["string"],
    "technical_highlights": ["string"],
    "talking_points": ["string"],
    "interview_answer_star": {
      "situation": "string",
      "task": "string",
      "action": "string",
      "result": "string"
    },
    "technical_learning_arc": {
      "primary_challenge": "string",
      "approach_and_why": "string",
      "key_learning_insight": "string",
      "transfer_value": "string"
    },
    "anticipated_interview_questions": [
      {
        "question": "string",
        "intent": "string",
        "suggested_answer_frames": ["string"]
      }
    ],
    "role_emphasis_prep": {
      "primary_themes": ["string"],
      "cross_functional_elements": ["string"],
      "technical_depth_areas": ["string"]
    }
  },
  "role_versions": {}
}
```

## Input Parsing Layer

This layer converts supported raw inputs into the normalized `source` structure used by project and JD records.

### Normalized Output Contract

```json
{
  "source_type": "text | file | url | notion",
  "raw_text": "string",
  "source_reference": "string",
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

| Input Type                                        | Parsing Method                          | Multi-file |
| ------------------------------------------------- | --------------------------------------- | ---------- |
| Plain text                                        | pass-through                            | —          |
| PDF                                               | `pdfplumber`                            | yes        |
| `.txt` / `.md`                                    | `Path.read_text()`                      | yes        |
| `.html` / `.htm`                                  | `BeautifulSoup` with content extraction | yes        |
| Images (`.jpg`, `.png`, `.bmp`, `.tiff`, `.webp`) | OCR via Tesseract + Pillow              | yes        |
| URL                                               | `requests` + `BeautifulSoup`            | —          |
| Notion page URL                                   | Notion API block traversal              | —          |

When multiple files are uploaded, each is parsed individually and their `raw_text` values are joined with `\n\n---\n\n` separators. The merged `source_reference` is a comma-separated list of filenames, and `metadata.filenames` holds the array.

### Responsibility

This layer is responsible only for ingestion, normalization, and provenance capture. It does not classify content, score fit, generate analysis, or persist final records.

## Data Model Sections

| Section         | Purpose                                             |
| --------------- | --------------------------------------------------- |
| `source`        | preserves the original parsed material              |
| `context`       | captures user-provided interpretation and ownership |
| `analysis`      | stores generated structured outputs                 |
| `role_versions` | stores alternate role-specific reframings           |

## JD Target Record

A JD target record stores extracted requirements and match results.

```json
{
  "id": "uuid",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601",
  "title": "string",
  "company": "string",
  "source": {
    "source_type": "text | file | url",
    "raw_text": "string",
    "source_reference": "string"
  },
  "extracted_requirements": {
    "tech_stack": ["string"],
    "collaboration_signals": ["string"],
    "domain_context": ["string"],
    "seniority_signals": ["string"],
    "role_category": "string"
  },
  "match_results": {
    "projects": [
      {
        "project_id": "uuid",
        "fit_score": 0,
        "score_breakdown": {
          "tech_stack_overlap": 0,
          "domain_relevance": 0,
          "collaboration_signals": 0,
          "seniority_alignment": 0
        },
        "tailored_bullets": [
          {
            "bullet": "string",
            "addresses": ["tech_stack", "domain", "collaboration", "seniority"],
            "source_references": ["resume_bullets[0]", "technical_highlights[2]"],
            "reasoning": "string"
          }
        ],
        "addressed_requirements": ["string"]
      }
    ]
  },
  "similar_to": "uuid",
  "is_duplicate_of": "uuid"
}
```
