# JD Uploader Feature Design

**Feature:** Job Description Upload and Matching
**Page:** Resume Page
**Last updated:** 2026-04-03

---

## 1. Overview

The JD Uploader is the primary entry point on the Resume Page. It accepts a job description in any supported format, extracts role requirements, checks for duplicates against existing saved JDs, and triggers the matching pipeline to rank saved projects by relevance.

**Key Goals:**
- Accept JDs in all common formats without friction
- Surface a deduplication prompt before running matching, to avoid redundant job targets
- Produce a ranked, tailored output that can be immediately used to build a resume

---

## 2. User Flow

### Primary Flow: Upload and Match

1. **Access Upload Area**
   - User navigates to Resume Page
   - Upload area is displayed at the top, collapsed by default (same pattern as Projects Page)

2. **Select Input Type**
   - Plain text paste
   - File upload (PDF)
   - Screenshot / image (OCR)
   - URL to job posting

3. **Provide JD Material**
   - For text: direct paste into textarea
   - For file: drag-and-drop or file picker
   - For image: drag-and-drop or file picker; OCR runs on submit
   - For URL: URL input field; page content is fetched and extracted on submit

4. **Deduplication Check**
   - Before running matching, system compares the incoming JD against all existing saved JDs
   - Similarity is computed on extracted requirement keywords and role signals
   - If a high-similarity match is found (threshold: ≥ 70% overlap), system shows a prompt:
     - "This looks similar to **[existing JD title]** saved on [date]. Update that target instead, or save as a new one?"
     - Options: **Update existing** | **Save as new** | **Cancel**
   - If no duplicate is found, proceed silently

5. **Matching Execution**
   - System extracts key requirements from the JD (see §4 for extraction logic)
   - Runs matching against all saved projects
   - Scores each project per requirement dimension
   - Ranks projects by overall fit

6. **Review Match Results**
   - Results displayed inline below the upload area, or as a full-page view
   - User sees ranked project list with fit scores and tailored bullets
   - User can promote/demote projects, pin bullets for export

7. **Save JD Target**
   - User clicks "Save to Resume Targets"
   - JD entity saved with match results attached
   - Appears in JD list below

### Alternative Flow: Re-run Matching

- User opens an existing saved JD target
- Clicks "Re-match" after adding new projects
- Matching runs again; new results replace old ones (with confirmation)

---

## 3. UI Design

### Layout

```
[Resume Page Header]

[JD Upload Area - Collapsed]
+ Add New Job Target

[JD Upload Area - Expanded]
Input Type: [Text] [File] [Image] [URL]

[Input area for selected type]

[Submit Button: Extract & Match]

[Deduplication Prompt - if triggered]
"Similar to: [JD title] (saved [date])"
[Update Existing] [Save as New] [Cancel]

[Match Results]
Ranked Projects:
┌──────────────────────────────────────────────────────────┐
│ #1  Project Title              Fit Score: 92%            │
│     Matched requirements: Vue, cross-team coordination   │
│     Tailored bullets:                                    │
│     • [editable bullet]                                  │
│     • [editable bullet]                                  │
└──────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────┐
│ #2  Project Title              Fit Score: 74%            │
│     ...                                                  │
└──────────────────────────────────────────────────────────┘

[Save to Resume Targets]
```

### Visual Design Principles

- Same collapsible panel pattern as the Projects Page uploader
- Fit score displayed as a percentage badge (color: green ≥ 80%, yellow 60–79%, grey < 60%)
- Deduplication prompt is non-blocking — it is an inline banner, not a modal, so the user can still scroll the input
- Tailored bullets are editable inline before save

---

## 4. Technical Implementation

### JD Requirement Extraction

Extracted fields per JD:
- **Tech stack signals** — frameworks, languages, tools mentioned explicitly
- **Collaboration signals** — team size indicators, cross-functional mentions, leadership keywords
- **Domain signals** — industry, product type, business context
- **Seniority signals** — years of experience, scope of ownership, title-level cues
- **Raw requirement list** — bullet-extracted list of stated qualifications

### Matching Logic

Per saved project, scoring runs across dimensions:

| Dimension | Weight |
|---|---|
| Tech stack overlap | 40% |
| Domain relevance | 25% |
| Collaboration pattern match | 20% |
| Seniority signal alignment | 15% |

Overall fit score = weighted sum. Projects sorted descending by score.

### Tailored Bullet Generation

For each matched project:
- Select the most relevant resume bullets from the project's `resume_bullets[]`
- Reorder and filter based on which JD requirements they address
- Prepend the strongest signal keywords where naturally fitting
- Output: 2–4 bullets per project, ranked by relevance to this specific JD

### Deduplication

- On JD submit, extract requirement keyword set
- Compare against keyword sets of all existing saved JDs (Jaccard similarity)
- Threshold: ≥ 70% overlap triggers the deduplication prompt
- Comparison is fast (in-memory set operations, no network call)

### Key Components

**JDUploadHandler.vue:**
- Input type tab selection
- File/text/URL input handling
- Triggers extraction and matching pipeline

**DuplicatePrompt.vue:**
- Inline banner shown when a similar JD is detected
- Exposes: update vs. new vs. cancel actions

**MatchResultsList.vue:**
- Ranked project cards with fit scores
- Inline bullet editing per project
- Pin/unpin bullets for export

### Performance Targets

- JD extraction: < 1 second (local, rule-based)
- Matching against 20 projects: ≤ 15 seconds
- Deduplication check: < 200ms

---

## 5. Validation and Testing

### User Acceptance Criteria

- [ ] User can upload a JD in all supported input types
- [ ] Deduplication prompt fires correctly for similar JDs and is suppressible
- [ ] Matching runs and returns a ranked list with fit scores
- [ ] Tailored bullets are shown per project and are editable inline
- [ ] Saving a JD target creates a record visible in the JD list

### Edge Cases

- **No saved projects yet:** Show message "Add projects first before matching against a JD" with a link to the Projects Page
- **JD with no extractable requirements:** Graceful degradation — show raw text, allow manual save without scores
- **All projects score below 30%:** Show a low-confidence warning but still display results
- **Duplicate accepted as "Update":** Overwrite existing JD entity; match results and tailored bullets refresh

---

## 6. Future Enhancements

- LLM-powered extraction for nuanced requirement parsing
- Role-aligned bullet rewriting (Vue developer vs. middle office framing)
- Side-by-side view: JD requirements vs. project contributions
- Export matched resume section directly to PDF or clipboard
