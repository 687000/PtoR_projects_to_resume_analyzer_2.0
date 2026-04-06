# Resume List Feature Design

**Feature:** Job Target / Resume Content Management
**Page:** Resume Page

---

## 1. Overview

The Resume List is a management interface for all saved job targets. Each item in the list represents one JD the user has matched against their projects. From here the user can browse saved targets, view tailored resume output for each, re-run matching after adding new projects, and delete stale targets.

**Key Goals:**
- Give a clear at-a-glance view of all active job targets
- Surface match quality and last-used status per target
- Provide quick access to tailored resume content for each target

---

## 2. Core Features

### Content Preview

- **Card-based layout:** Each JD target displayed as a card showing role title, company (if detected), top matched projects, and overall best fit score
- **Status indicators:** Whether the target has been exported, when it was last updated, and whether new projects have been added since the last match run

### CRUD Operations

- **Create:** Via JD Uploader (see jd-uploader.md)
- **Read:** Browse, search, and filter the JD list
- **Update:** Re-run matching on an existing target; edit extracted requirements manually
- **Delete:** Single delete with confirmation

### Management Tools

- **Search:** Real-time search across role title, company name, and extracted tech keywords
- **Filter:** By date added, fit score range, or export status
- **Sort:** By date added (default), best fit score, or role title alphabetically

---

## 3. UI Design

### Layout

```
[Search Bar + Filters]  [Sort: Date Added ▾]

[JD Cards Grid]
┌─────────────────────────────┐  ┌─────────────────────────────┐
│ Senior Frontend Engineer    │  │ Full-Stack Developer         │
│ Acme Corp · Added 2026-03-28│  │ Beta Inc · Added 2026-04-01 │
│ Best match: 92% (Project A) │  │ Best match: 74% (Project C) │
│ 3 projects matched          │  │ 2 projects matched          │
│ [View Resume] [Re-match]    │  │ [View Resume] [Re-match]    │
│ [Delete]                    │  │ [Delete]            ★ New   │
└─────────────────────────────┘  └─────────────────────────────┘
```

**Card fields:**
- Role title (extracted or user-labeled)
- Company name (extracted, or "Unknown")
- Date added
- Best overall fit score
- Number of projects matched
- "New projects available" badge — shown when projects have been added since the last match run
- Actions: **View Resume**, **Re-match**, **Delete**

### Empty State

When no JDs have been saved yet:

```
[Empty state illustration]
No job targets yet.
Upload a job description to generate tailored resume content.
[+ Add Job Target]
```

### Detail View

Clicking **View Resume** opens the full tailored resume output for that JD target — see custom-resume-item.md for the detail view spec.

---

## 4. User Flows

### Browse and Select

1. User opens Resume Page
2. Scrolls / searches the JD list
3. Clicks "View Resume" on a target → detail view opens

### Re-match After Adding Projects

1. User adds new projects on the Projects Page
2. Returns to Resume Page
3. Cards with "New projects available" badge are surfaced at top
4. User clicks "Re-match" on a card
5. Matching re-runs; card updates with new scores and bullets

### Delete a Stale Target

1. User clicks "Delete" on a card
2. Confirmation: "Remove [role title] from your job targets? This will delete all tailored resume content for this job."
3. On confirm: card removed, data deleted

---

## 5. Technical Implementation

**Frontend:** Vue 3 grid component, same layout system as Projects Page  
**State:** Pinia store (`resumeStore`) — mirrors `projectStore` pattern  
**Storage:** `data/jd_targets.json` — append-only JSON list, same format as `projects.json`  
**Search:** Client-side filtering across `role_title`, `company`, `extracted_keywords[]`

### JD Target List Item Display Fields

From the Job Description Entity (PRD §8):

| Field | Display Purpose |
|---|---|
| `role_title` | Primary card heading |
| `company` | Subheading |
| `created_at` | "Added [date]" |
| `best_fit_score` | Score badge |
| `matched_project_count` | "N projects matched" |
| `has_new_projects` | "New" badge |
| `last_exported_at` | "Last exported [date]" if applicable |

### Performance Targets

- List render: < 2 seconds
- Search filter: < 100ms
- Re-match trigger: initiates async job, shows spinner on card

---

## 6. Validation and Testing

### User Acceptance Criteria

- [ ] All saved JD targets display as cards
- [ ] Search and filter reduce the visible list correctly
- [ ] "New projects available" badge appears when new projects exist since last match
- [ ] "Re-match" re-runs the pipeline and updates card data
- [ ] "View Resume" opens the correct detail view
- [ ] Delete removes the target and its associated tailored content

### Edge Cases

- **Empty list:** Show onboarding empty state with link to JD uploader
- **JD with no extracted company name:** Display "Unknown company" gracefully
- **Re-match with no new projects:** Confirm before re-running ("No new projects have been added. Re-run anyway?")
- **Deleted project referenced in a JD target:** Show "[project deleted]" placeholder in match results rather than crashing

---

## 7. Future Enhancements

- Bulk export: generate a combined resume PDF from multiple top-ranked targets
- Target comparison: side-by-side view of two JD targets against the same project pool
- Application tracking: mark targets as Applied / Interview / Offer / Rejected
- Analytics: which projects appear most frequently in top matches
