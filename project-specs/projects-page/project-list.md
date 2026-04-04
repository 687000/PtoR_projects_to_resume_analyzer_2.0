# Project List Feature Design

**Feature:** Project Asset/Content Management
**Page:** Projects Page
**Last updated:** 2026-04-03

---

## MVP Implementation Status (Python CLI)

The current implementation is a Python CLI. The Vue 3 UI described below is the target design.

**Implemented commands:**
```bash
# Upload and analyze a project
python -m src.cli upload --file project.pdf
python -m src.cli upload --file project.txt
python -m src.cli upload --text "paste project description here"

# List all saved projects
python -m src.cli list
```

**Upload flow:**
1. Parse input (plain text or PDF → `src/parser.py`)
2. Prompt user for structured context form (background vs. contributions)
3. Run analysis via LLM — classification, tagging, output generation (`src/analyzer.py`)
4. Display results and confirm save
5. Save to `data/projects.json` (`src/store.py`)

**Project store:** `data/projects.json` — append-only JSON list.  
Each record includes: `id`, `created_at`, `title`, `category`, `tags`, `summary`, `ownership_description`, `technical_highlights`, `resume_bullets`, `interview_answer`, `self_intro`, `talking_points`, `context`, `raw_text`, `source_metadata`.

---

## 1. Overview

The Project List serves as a pure content management interface for project assets. It provides clear UI previews of all saved projects, enabling efficient CRUD operations and streamlined project management workflows.

**Key Goals:**
- Clear content previews for all project assets
- Intuitive CRUD operations (Create via uploader, Read/Update/Delete here)
- Easy management process with drag-and-drop reordering
- Quick access to project details and editing

---

## 2. Core Features

### Content Preview
- **Card-based Layout:** Each project displayed as a card with title, category, key highlights, and thumbnail
- **Quick Preview:** Hover/click to show summary, technical tags, and ownership highlights
- **Visual Indicators:** Status icons for analysis completion, edit history, and usage in resumes

### CRUD Operations
- **Create:** Link to project uploader for new projects
- **Read:** Browse and search project list with filters
- **Update:** Inline editing of metadata, drag-to-reorder, bulk tagging
- **Delete:** Single/bulk delete with confirmation and undo option

### Management Tools
- **Search & Filter:** Real-time search across titles, content, and tags
- **Sorting:** By date, category, usage frequency, or custom order
- **Bulk Actions:** Select multiple projects for batch operations (tag, export, delete)
- **Export:** Download project data in various formats (JSON, PDF summary)

---

## 3. UI Design

### Layout
```
[Search Bar + Filters]

[Project Grid/List View Toggle]

[Project Cards Grid]
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ [Thumbnail] Project Title   │ │ [Thumbnail] Project Title   │
│ Category | Tags            │ │ Category | Tags            │
│ Key highlights preview...   │ │ Key highlights preview...   │
│ [Preview] [Edit] [Delete]   │ │ [Preview] [Edit] [Delete]   │
└─────────────────────────────┘ └─────────────────────────────┘

[Bulk Actions Bar - when selected]
[Export] [Tag] [Delete] [Reorder]
```

### Key Interactions
- **Drag & Drop:** Reorder projects by dragging cards
- **Inline Edit:** Click metadata fields to edit directly
- **Quick Actions:** Context menus for common operations
- **Selection Mode:** Checkbox selection for bulk operations

---

## 4. User Flows

### Daily Management
1. View project grid with clear previews
2. Search/filter to find specific projects
3. Drag to reorder for priority/custom organization
4. Quick edit metadata inline
5. Bulk select for common operations

### Content Review
1. Hover cards for instant preview
2. Click to view full project details
3. Check usage indicators for resume integration
4. Export selected projects for external use

---

## 5. Technical Implementation

**Frontend:** Vue 3 grid component with drag-and-drop (vue-draggable)
**State:** Pinia store for project data with optimistic updates
**Storage:** Local SQLite with indexed search
**Performance:** Virtual scrolling for large collections (>100 projects)

---

## 6. Validation

- CRUD operations complete within 2 seconds
- Search results update in <100ms
- Drag-and-drop reordering persists immediately
- Bulk operations handle up to 50 projects efficiently
- Offline functionality for local data management

**SearchFilters.vue:**
- Search input and filter controls
- State management for active filters
- Clear/reset functionality

**ListControls.vue:**
- View toggle (list/grid)
- Bulk action controls
- Export functionality

### Performance Considerations

- **Virtualization:** Use virtual scrolling for >50 projects
- **Lazy Loading:** Load project details on demand
- **Indexing:** Client-side indexing for fast search
- **Caching:** Cache rendered cards to reduce re-renders

---

## 5. Data Structure

### Project List Item Display Fields

Based on Project Entity from PRD §8:

- **title** (primary display)
- **category** (filterable)
- **source_materials[]** (count or preview)
- **date / timeline** (sortable)
- **key highlights** (from generated summary)
- **tags** (technical themes from analysis)
- **role_versions** (available variants)

### Search and Filter Options

- **Text Search:** Across title, summary, and highlights
- **Category Filter:** Dropdown of project categories
- **Tag Filter:** Multi-select technical tags
- **Date Filter:** Date range picker
- **Favorites:** Toggle for starred projects

---

## 6. Validation and Testing

### User Acceptance Criteria

- [ ] All saved projects display in list format
- [ ] Search returns relevant results within 100ms
- [ ] Filters apply correctly and combine logically
- [ ] Navigation to detail view preserves context
- [ ] Bulk operations work on selected projects

### Edge Cases

- **Empty List:** Show onboarding message with link to upload
- **No Search Results:** Clear "no results" message with reset option
- **Large Lists:** Maintain performance with 100+ projects
- **Deleted Projects:** Handle gracefully without breaking list
- **Concurrent Edits:** Sync changes across open views

### Accessibility Testing

- Keyboard navigation through list items
- Screen reader support for project cards
- High contrast mode compatibility
- Focus management in search/filter controls

---

## 7. Future Enhancements

- **Advanced Search:** Full-text search with highlighting
- **Project Templates:** Quick creation from common patterns
- **Collaboration:** Share project lists with team members
- **Analytics:** Usage statistics and project insights
- **Integration:** Sync with external project management tools