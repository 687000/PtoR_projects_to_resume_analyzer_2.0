<template>
  <Teleport to="body">
    <div class="overlay" @click.self="store.closeModal()">
      <div class="modal">

        <!-- Header -->
        <div class="modal-header">
          <div class="header-main">
            <h2>{{ t.role_title }}</h2>
            <div class="meta">
              <span v-if="t.company" class="company">{{ t.company }}</span>
              <span class="date-info">Saved {{ formatDate(t.created_at) }}</span>
            </div>
          </div>
          <div class="header-actions">
            <button
              class="btn-secondary rematch-btn"
              :disabled="store.modal.rematching"
              @click="openRematchPanel"
            >
              <span v-if="store.modal.rematching" class="spinner dark" />
              <span v-else>Re-match</span>
            </button>
            <button class="btn-ghost close-btn" @click="store.closeModal()">✕</button>
          </div>
        </div>

        <!-- Requirements panel -->
        <div class="req-panel">
          <span class="req-label">Requirements</span>
          <div class="req-chips">
            <span v-for="kw in allRequirements" :key="kw" class="req-chip">{{ kw }}</span>
            <span v-if="!allRequirements.length" class="req-none">No requirements extracted</span>
          </div>
        </div>

        <!-- Original JD text (collapsible) -->
        <div class="jd-source-panel">
          <button class="jd-source-toggle" @click="showJDSource = !showJDSource">
            <span class="jd-source-label">Original JD</span>
            <span class="jd-source-chevron" :class="{ open: showJDSource }">▾</span>
          </button>
          <div v-if="showJDSource" class="jd-source-body">
            <pre class="jd-source-text">{{ t.raw_jd_text || 'No source text saved.' }}</pre>
          </div>
        </div>

        <!-- Matched project sections -->
        <div class="modal-scroll">
          <div v-if="!matchedProjects.length" class="no-projects">
            No projects matched this JD. Add more projects on the Projects page to improve results.
          </div>

          <div
            v-for="(mp, mpIdx) in matchedProjects"
            :key="mp.project_id"
            class="project-section"
          >
            <div class="project-header">
              <span class="project-title">{{ mp.project_title }}</span>
              <span class="fit-badge" :class="fitClass(mp.fit_score)">{{ mp.fit_score }}%</span>
            </div>

            <div v-if="mp.addressed_requirements?.length" class="addressed">
              <span v-for="r in mp.addressed_requirements" :key="r" class="tag">{{ r }}</span>
            </div>

            <ul class="bullet-list">
              <li
                v-for="(b, bIdx) in mp.tailored_bullets"
                :key="bIdx"
                class="bullet-item"
                :class="{ excluded: !b.included }"
                @click="toggleBullet(mpIdx, bIdx)"
              >
                <span class="toggle-icon">{{ b.included ? '☑' : '☐' }}</span>
                <span
                  v-if="editingKey !== `${mpIdx}-${bIdx}`"
                  class="bullet-text"
                  @click.stop="startEdit(mpIdx, bIdx, b.text)"
                >{{ b.text }}</span>
                <textarea
                  v-else
                  class="bullet-edit"
                  v-model="editText"
                  rows="2"
                  @click.stop
                  @blur="commitEdit(mpIdx, bIdx)"
                  @keydown.enter.prevent="commitEdit(mpIdx, bIdx)"
                  @keydown.escape="editingKey = null"
                />
              </li>
            </ul>

            <button class="add-bullet-btn" @click="addBullet(mpIdx)">+ Add bullet</button>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <div class="footer-left">
            <template v-if="store.modal.deleteConfirm">
              <span class="confirm-text">Delete this job target?</span>
              <button class="btn-danger" @click="store.deleteTarget(t.id)">Yes, delete</button>
              <button class="btn-secondary" @click="store.modal.deleteConfirm = false">Cancel</button>
            </template>
            <button v-else class="btn-ghost danger-ghost" @click="store.modal.deleteConfirm = true">Delete</button>
          </div>
          <div class="footer-right">
            <button class="btn-secondary" @click="openCopyPopup">Copy Resume Section</button>
            <button class="btn-primary" :disabled="store.modal.saving" @click="store.saveBullets()">
              <span v-if="store.modal.saving" class="spinner" />
              {{ store.modal.saving ? 'Saving…' : 'Save Changes' }}
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- Rematch project selection panel -->
    <div v-if="showRematchPanel" class="rematch-overlay" @click.self="showRematchPanel = false">
      <div class="rematch-panel">
        <div class="rematch-panel-header">
          <div class="rematch-panel-title-group">
            <span class="rematch-panel-title">Select Projects to Re-match</span>
            <span class="rematch-panel-subtitle">Matching runs against the original uploaded JD text</span>
          </div>
          <button class="btn-ghost close-btn" @click="showRematchPanel = false">✕</button>
        </div>
        <div class="rematch-select-bar">
          <span class="rematch-sel-count">{{ selectedProjectIds.length }} of {{ projectStore.projects.length }} selected</span>
          <button class="select-all-btn" @click="toggleAllProjects">
            {{ selectedProjectIds.length === projectStore.projects.length ? 'Deselect all' : 'Select all' }}
          </button>
        </div>
        <div class="rematch-panel-body">
          <div
            v-for="proj in projectStore.projects"
            :key="proj.id"
            class="rematch-proj-row"
            :class="{ selected: isProjectSelected(proj.id) }"
            @click="toggleProjectSelection(proj.id)"
          >
            <input
              type="checkbox"
              :checked="isProjectSelected(proj.id)"
              @click.stop
              @change="toggleProjectSelection(proj.id)"
            />
            <div class="rematch-proj-info">
              <span class="rematch-proj-name">{{ proj.title }}</span>
              <span class="rematch-proj-cat">{{ proj.category }}</span>
            </div>
          </div>
        </div>
        <div class="rematch-panel-footer">
          <button class="btn-secondary" @click="showRematchPanel = false">Cancel</button>
          <button
            class="btn-primary"
            :disabled="!selectedProjectIds.length || store.modal.rematching"
            @click="runRematch"
          >
            <span v-if="store.modal.rematching" class="spinner" />
            {{ store.modal.rematching ? 'Matching…' : `Re-match with ${selectedProjectIds.length} project${selectedProjectIds.length !== 1 ? 's' : ''}` }}
          </button>
        </div>
      </div>
    </div>

    <!-- Copy popup -->
    <div v-if="showCopyPopup" class="copy-overlay" @click.self="showCopyPopup = false">
      <div class="copy-popup">
        <div class="copy-popup-header">
          <span class="copy-popup-title">Resume Section</span>
          <button class="btn-ghost close-btn" @click="showCopyPopup = false">✕</button>
        </div>
        <div class="copy-popup-options">
          <label class="option-label">
            <input type="checkbox" v-model="showProjectTitle" @change="regenerateCopyText" />
            Show project titles
          </label>
        </div>
        <textarea class="copy-popup-textarea" v-model="copyPopupText" rows="14" />
        <div class="copy-popup-footer">
          <button class="btn-secondary" @click="showCopyPopup = false">Close</button>
          <button class="btn-primary" @click="copyFromPopup">
            {{ copied ? 'Copied!' : 'Copy to Clipboard' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useProjectStore } from '../stores/projects'

const store = useResumeStore()
const projectStore = useProjectStore()
const t = computed(() => store.modal.target)
const matchedProjects = computed(() => t.value?.matched_projects || [])

const editingKey = ref(null)
const editText = ref('')
const copied = ref(false)
const showCopyPopup = ref(false)
const copyPopupText = ref('')
const showProjectTitle = ref(true)
const showRematchPanel = ref(false)
const selectedProjectIds = ref([])
const showJDSource = ref(false)

const allRequirements = computed(() => {
  const r = t.value?.extracted_requirements
  if (!r) return []
  return [
    ...(r.tech_stack || []),
    ...(r.domain || []),
    ...(r.collaboration || []),
    ...(r.seniority || []),
  ].slice(0, 20)
})

function fitClass(score) {
  if (score >= 80) return 'high'
  if (score >= 60) return 'mid'
  return 'low'
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

function toggleBullet(mpIdx, bIdx) {
  if (editingKey.value === `${mpIdx}-${bIdx}`) return
  const b = matchedProjects.value[mpIdx].tailored_bullets[bIdx]
  b.included = !b.included
}

function startEdit(mpIdx, bIdx, text) {
  editingKey.value = `${mpIdx}-${bIdx}`
  editText.value = text
}

function commitEdit(mpIdx, bIdx) {
  if (editText.value.trim()) {
    matchedProjects.value[mpIdx].tailored_bullets[bIdx].text = editText.value.trim()
    matchedProjects.value[mpIdx].tailored_bullets[bIdx].source = 'user'
  }
  editingKey.value = null
}

function addBullet(mpIdx) {
  const bullets = matchedProjects.value[mpIdx].tailored_bullets
  bullets.push({
    text: 'New bullet — click to edit',
    included: true,
    source: 'user',
    order: bullets.length,
  })
  // Start editing the new bullet immediately
  const newIdx = bullets.length - 1
  startEdit(mpIdx, newIdx, bullets[newIdx].text)
}

function buildResumeText() {
  const lines = []
  for (const mp of matchedProjects.value) {
    const included = mp.tailored_bullets.filter(b => b.included)
    if (!included.length) continue
    if (showProjectTitle.value) lines.push(mp.project_title)
    included.forEach(b => lines.push(showProjectTitle.value ? `  • ${b.text}` : `• ${b.text}`))
    lines.push('')
  }
  return lines.join('\n').trim()
}

function openCopyPopup() {
  copyPopupText.value = buildResumeText()
  showCopyPopup.value = true
}

function regenerateCopyText() {
  copyPopupText.value = buildResumeText()
}

function openRematchPanel() {
  // Pre-select projects that were previously matched to this JD
  const previouslyMatched = matchedProjects.value.map(mp => mp.project_id)
  selectedProjectIds.value = previouslyMatched.length
    ? previouslyMatched
    : projectStore.projects.map(p => p.id)
  showRematchPanel.value = true
}

function isProjectSelected(id) {
  return selectedProjectIds.value.includes(id)
}

function toggleProjectSelection(id) {
  const idx = selectedProjectIds.value.indexOf(id)
  if (idx === -1) selectedProjectIds.value.push(id)
  else selectedProjectIds.value.splice(idx, 1)
}

function toggleAllProjects() {
  if (selectedProjectIds.value.length === projectStore.projects.length) {
    selectedProjectIds.value = []
  } else {
    selectedProjectIds.value = projectStore.projects.map(p => p.id)
  }
}

async function runRematch() {
  await store.rematch(t.value.id, selectedProjectIds.value)
  showRematchPanel.value = false
}

async function copyFromPopup() {
  await navigator.clipboard.writeText(copyPopupText.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0;
  background: rgba(30, 20, 60, 0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--surface);
  border-radius: 12px;
  width: 800px;
  height: 84vh;
  display: flex; flex-direction: column;
  box-shadow: 0 24px 48px rgba(40,20,100,0.22);
  overflow: hidden;
  flex-shrink: 0;
}

/* Header */
.modal-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 16px; padding: 18px 20px 14px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.header-main { flex: 1; min-width: 0; }
h2 { font-size: 15px; font-weight: 700; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.company { font-size: 12px; color: var(--text-muted); }
.date-info { font-size: 11px; color: var(--text-muted); }
.header-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.rematch-btn { font-size: 12px; padding: 5px 12px; min-width: 80px; }
.close-btn { font-size: 15px; padding: 2px 7px; }

/* Requirements panel */
.req-panel {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
  background: #faf9fe;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.req-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--text-muted);
  white-space: nowrap; padding-top: 2px;
}
.req-chips { display: flex; flex-wrap: wrap; gap: 4px; flex: 1; }
.req-chip {
  font-size: 11px; font-weight: 500;
  background: var(--tag-bg); color: var(--tag-text);
  padding: 2px 8px; border-radius: 100px;
}
.req-none { font-size: 12px; color: var(--text-muted); font-style: italic; }

/* Original JD collapsible panel */
.jd-source-panel {
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.jd-source-toggle {
  width: 100%;
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 20px;
  background: none; border: none; cursor: pointer;
  text-align: left;
}
.jd-source-toggle:hover { background: #f5f3fc; }
.jd-source-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--text-muted);
}
.jd-source-chevron {
  font-size: 13px; color: var(--text-muted);
  transition: transform 0.15s;
  display: inline-block;
}
.jd-source-chevron.open { transform: rotate(180deg); }
.jd-source-body {
  padding: 0 20px 12px;
  background: #faf9fe;
}
.jd-source-text {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 11px; line-height: 1.65;
  color: var(--text-muted);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 12px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 260px;
  overflow-y: auto;
  margin: 0;
}

/* Scrollable body */
.modal-scroll {
  flex: 1; overflow-y: auto; padding: 20px;
  display: flex; flex-direction: column; gap: 24px;
}

.no-projects {
  font-size: 13px; color: var(--text-muted);
  text-align: center; padding: 32px 0;
}

/* Project section */
.project-section {
  display: flex; flex-direction: column; gap: 10px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}
.project-section:last-child { border-bottom: none; padding-bottom: 0; }

.project-header { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.project-title { font-size: 13px; font-weight: 700; }

.fit-badge {
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 100px;
}
.fit-badge.high { background: #dcfce7; color: #166534; }
.fit-badge.mid  { background: #fef9c3; color: #854d0e; }
.fit-badge.low  { background: #f1f5f9; color: #475569; }

.addressed { display: flex; flex-wrap: wrap; gap: 4px; }

/* Bullet list */
.bullet-list { display: flex; flex-direction: column; gap: 4px; list-style: none; padding: 0; }
.bullet-item {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 5px 8px; border-radius: 6px;
  cursor: pointer; transition: background 0.1s, opacity 0.15s;
}
.bullet-item:hover { background: var(--tag-bg); }
.bullet-item.excluded { opacity: 0.4; }

.toggle-icon {
  font-size: 15px; line-height: 1.6;
  color: var(--primary); flex-shrink: 0; min-width: 18px;
  user-select: none;
}

.bullet-text {
  font-size: 13px; line-height: 1.65; color: var(--text);
  cursor: text; flex: 1;
  border-radius: 3px; padding: 1px 3px;
}
.bullet-text:hover { text-decoration: underline; text-underline-offset: 2px; }

.bullet-edit {
  flex: 1; font-size: 13px; line-height: 1.65;
  resize: none; padding: 4px 6px;
}

.add-bullet-btn {
  background: none; border: 1px dashed var(--border);
  border-radius: 6px; padding: 5px 12px;
  font-size: 12px; color: var(--text-muted);
  cursor: pointer; text-align: left; width: fit-content;
}
.add-bullet-btn:hover { border-color: var(--primary); color: var(--primary); background: var(--tag-bg); }

/* Footer */
.modal-footer {
  display: flex; justify-content: space-between; align-items: center;
  gap: 12px; padding: 12px 20px;
  border-top: 1px solid var(--border);
  background: #faf9fe;
  flex-shrink: 0; flex-wrap: wrap;
}
.footer-left { display: flex; align-items: center; gap: 8px; }
.footer-right { display: flex; align-items: center; gap: 8px; }
.confirm-text { font-size: 12px; color: var(--text); }
.danger-ghost { color: var(--danger); }
.danger-ghost:hover { background: #fdf2f4; }

.spinner.dark {
  border-color: rgba(0,0,0,0.15);
  border-top-color: var(--text-muted);
}

/* Rematch project selection panel */
.rematch-overlay {
  position: fixed; inset: 0;
  background: rgba(30, 20, 60, 0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1100;
}

.rematch-panel {
  background: var(--surface);
  border-radius: 10px;
  width: 520px;
  max-width: 92vw;
  max-height: 80vh;
  display: flex; flex-direction: column;
  box-shadow: 0 16px 40px rgba(40, 20, 100, 0.22);
  overflow: hidden;
}

.rematch-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px 10px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.rematch-panel-title-group { display: flex; flex-direction: column; gap: 2px; }
.rematch-panel-title { font-size: 14px; font-weight: 700; }
.rematch-panel-subtitle { font-size: 11px; color: var(--text-muted); }

.rematch-select-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 18px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  background: #faf9fe;
}
.rematch-sel-count { font-size: 12px; color: var(--text-muted); }

.rematch-panel-body {
  flex: 1; overflow-y: auto;
  padding: 8px 0;
}

.rematch-proj-row {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 18px; cursor: pointer;
  transition: background 0.1s;
}
.rematch-proj-row:hover { background: var(--tag-bg); }
.rematch-proj-row.selected { background: #f0eeff; }
.rematch-proj-row input[type="checkbox"] { flex-shrink: 0; accent-color: var(--primary); cursor: pointer; }

.rematch-proj-info { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
.rematch-proj-name { font-size: 13px; font-weight: 500; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rematch-proj-cat { font-size: 11px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.rematch-panel-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 18px;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}

/* Copy popup */
.copy-overlay {
  position: fixed; inset: 0;
  background: rgba(30, 20, 60, 0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1100;
}

.copy-popup {
  background: var(--surface);
  border-radius: 10px;
  width: 560px;
  max-width: 92vw;
  display: flex; flex-direction: column; gap: 0;
  box-shadow: 0 16px 40px rgba(40, 20, 100, 0.22);
  overflow: hidden;
}

.copy-popup-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px 10px;
  border-bottom: 1px solid var(--border);
}
.copy-popup-title { font-size: 14px; font-weight: 700; }

.copy-popup-options {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 18px 0;
}
.option-label {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: var(--text-muted); cursor: pointer;
  user-select: none;
}
.option-label input[type="checkbox"] { cursor: pointer; accent-color: var(--primary); }

.copy-popup-textarea {
  margin: 8px 18px 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px; line-height: 1.7;
  resize: vertical;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 12px;
  color: var(--text);
  background: var(--bg);
  min-height: 200px;
}

.copy-popup-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 18px;
}
</style>
