# Project Item Feature Design

**Feature:** Project Detail View and Resume Bullet Editing
**Page:** Projects Page — Detail Modal
**Last updated:** 2026-04-04

---

## 1. Overview

The Project Item is a fixed-size modal that opens when the user clicks any project card. It provides a full read view of all generated output fields, a context re-edit mode, and inline editing of resume bullets.

---

## 2. User Flow

### View mode

1. Click a project card → modal opens on the **Summary** tab
2. Switch tabs to browse all output sections
3. Click **"Edit Context"** to enter edit mode
4. Click **"Delete"** (with confirmation) to remove the project

### Edit context mode

1. Context form opens pre-filled with current values
2. Edit any field
3. Click **"Save with Re-analysis"** → all output fields regenerate from the new context
4. Or click **"Cancel"** to return to view mode

### Resume bullet editing

Bullets are editable directly inside the **Resume Bullets** tab without entering a separate edit mode:

1. Click any bullet text to edit it inline
2. Click **✕** next to a bullet to remove it
3. Click **"+ Add bullet"** to append a new empty bullet
4. Changes are saved on blur (PATCH request, no full re-analysis)

---

## 3. Tab Structure

| Tab | Content |
|---|---|
| **Source & Context** | Raw extracted text + all 9 context form fields as provided |
| **Summary** | Summary, ownership description, self-introduction |
| **Highlights** | Technical highlights list |
| **Resume Bullets** | Editable bullet list — see §4 |
| **Interview** | STAR interview answer, talking points |

---

## 4. Resume Bullets Tab — Editing Detail

The Resume Bullets tab supports direct inline editing. No separate "edit mode" is required.

### Interactions

| Action | How |
|---|---|
| Edit a bullet | Click the bullet text → inline textarea activates |
| Confirm edit | Click outside (blur) or press Enter |
| Cancel edit | Press Escape — reverts to previous text |
| Delete a bullet | Click **✕** on the right of the row |
| Add a bullet | Click **"+ Add bullet"** at the bottom of the list |

### Save behavior

Bullet edits are saved immediately on blur via `PATCH /api/projects/{id}` with `reanalyze: false`. A brief **"Saved"** indicator appears after each successful save.

### Visual design

```
Resume Bullets
──────────────────────────────────────────
  • Built modular Vue 3 component system...    ✕
  • Defined API contracts across web and...    ✕
  • Coordinated delivery across 3 teams...     ✕
──────────────────────────────────────────
  + Add bullet
```

- **✕** = delete button, visible on hover
- Clicking bullet text activates an inline `<textarea>`

---

## 5. Technical Implementation

**Component:** `ProjectModal.vue`

**State (Pinia `projectStore.modal`):**
```
open, project, editing, editContext, reanalyzing, deleteConfirm
```

**Bullet editing — local state inside `ProjectModal.vue`:**
```
editingBulletIdx: number | null   — index of the bullet being edited
editBulletText: string            — current draft text
```

**API call for bullet edits:**
- `PATCH /api/projects/{id}` with `{ context: <unchanged>, resume_bullets: [...], reanalyze: false }`

---

## 6. Validation

- [ ] All tabs display correct data from the saved project record
- [ ] Source & Context tab shows raw extracted text and all context fields
- [ ] Inline bullet edit activates on click, confirms on blur/Enter, cancels on Escape
- [ ] Delete bullet removes it and saves immediately
- [ ] Add bullet appends an empty row and activates it for editing
- [ ] "Edit Context" → re-analysis regenerates all output including bullets
- [ ] Delete project requires confirmation and closes the modal

---

## 7. Future Enhancements

- Drag-and-drop bullet reordering
- Edit history per bullet — undo back to AI-generated original
- Role-aligned bullet variants (Vue developer vs. middle office framing)
- Copy all included bullets to clipboard
