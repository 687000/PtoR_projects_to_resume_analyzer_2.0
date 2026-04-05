<template>
  <Teleport to="body">
    <div class="overlay" @click.self="store.closeModal()">
      <div class="modal">

        <!-- Header -->
        <div class="modal-header">
          <div class="header-main">
            <h2>{{ p.title }}</h2>
            <div class="meta">
              <span class="category-badge" :class="p.category">{{ p.category }}</span>
              <span v-for="tag in p.tags" :key="tag" class="tag">{{ tag.replace(/_/g, ' ') }}</span>
            </div>
          </div>
          <button class="btn-ghost close-btn" @click="store.closeModal()">✕</button>
        </div>

        <!-- Edit mode -->
        <template v-if="store.modal.editing">
          <div class="modal-scroll">
            <p class="edit-hint">Edit context below and re-analyze to regenerate all output fields.</p>
            <div class="edit-form-wrap">
              <ContextForm v-model="store.modal.editContext" />
            </div>
          </div>
          <div class="modal-footer">
            <p v-if="store.error" class="error">{{ store.error }}</p>
            <div class="footer-actions">
              <button class="btn-secondary" @click="store.modal.editing = false">Cancel</button>
              <button class="btn-primary" :disabled="store.modal.reanalyzing" @click="store.reanalyze()">
                <span v-if="store.modal.reanalyzing" class="spinner" />
                {{ store.modal.reanalyzing ? 'Re-analyzing…' : 'Save with Re-analysis' }}
              </button>
            </div>
          </div>
        </template>

        <!-- View mode -->
        <template v-else>
          <div class="tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="tab"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >{{ tab.label }}</button>
          </div>

          <div class="modal-scroll">

            <!-- Source & Context tab -->
            <div v-if="activeTab === 'source'" class="section">
              <div class="source-meta">
                <span class="meta-pill">{{ sourceTypeLabel }}</span>
                <span v-if="sourceName" class="meta-path">{{ sourceName }}</span>
                <span class="meta-chars">{{ p.raw_text?.length?.toLocaleString() }} chars extracted</span>
              </div>

              <div class="field">
                <label>Extracted Text</label>
                <pre class="raw-text">{{ p.raw_text }}</pre>
              </div>

              <div class="divider" />

              <div class="field"><label>Context used for analysis</label></div>
              <div class="context-grid">
                <template v-for="(field, key) in contextFields" :key="key">
                  <div v-if="p.context?.[key]" class="context-item">
                    <span class="context-key">{{ field }}</span>
                    <p class="context-val">{{ p.context[key] }}</p>
                  </div>
                </template>
                <p v-if="!hasAnyContext" class="empty-note">No context was provided during upload.</p>
              </div>
            </div>

            <!-- Summary tab -->
            <div v-if="activeTab === 'summary'" class="section">
              <div class="field"><label>Summary</label><p>{{ p.summary }}</p></div>
              <div class="field"><label>Ownership</label><p class="pre">{{ p.ownership_description }}</p></div>
              <div class="field"><label>Self-Introduction</label><p>{{ p.self_intro }}</p></div>
            </div>

            <!-- Highlights tab -->
            <div v-if="activeTab === 'highlights'" class="section">
              <div class="field">
                <label>Technical Highlights</label>
                <ul><li v-for="(h, i) in p.technical_highlights" :key="i">{{ h }}</li></ul>
              </div>
            </div>

            <!-- Bullets tab -->
            <div v-if="activeTab === 'bullets'" class="section">
              <div v-if="p.summary_bullet" class="field">
                <label>Primary Bullet</label>
                <p class="summary-bullet">{{ p.summary_bullet }}</p>
              </div>
              <div class="field">
                <div class="bullets-header">
                  <label>Supporting Bullets</label>
                  <span v-if="bulletSaved" class="saved-indicator">Saved</span>
                </div>
                <div class="bullets-list">
                  <div v-for="(b, i) in localBullets" :key="i" class="bullet-row">
                    <span class="bullet-dot">•</span>
                    <textarea
                      v-if="editingBulletIdx === i"
                      ref="bulletInputRef"
                      class="bullet-textarea"
                      v-model="editBulletText"
                      rows="2"
                      @blur="confirmBullet(i)"
                      @keydown.enter.prevent="confirmBullet(i)"
                      @keydown.esc="cancelBullet(i)"
                    />
                    <span v-else class="bullet-text" @click="startEditBullet(i)">{{ b }}</span>
                    <button class="bullet-delete" @mousedown.prevent @click="deleteBullet(i)">✕</button>
                  </div>
                </div>
                <button class="btn-add-bullet" @click="addBullet">+ Add bullet</button>
              </div>
            </div>

            <!-- Interview tab -->
            <div v-if="activeTab === 'interview'" class="section">
              <div class="field"><label>Interview Answer (STAR)</label><p class="pre">{{ p.interview_answer }}</p></div>
              <div class="field">
                <label>Talking Points</label>
                <ul><li v-for="(t, i) in p.talking_points" :key="i">{{ t }}</li></ul>
              </div>
            </div>

            <!-- JD Targets tab -->
            <div v-if="activeTab === 'jd-targets'" class="section">
              <p v-if="!matchedJDs.length" class="empty-note">
                No JD targets have matched this project yet. Upload a job description on the Resume page.
              </p>
              <div v-else class="jd-target-list">
                <div v-for="jd in matchedJDs" :key="jd.id" class="jd-target-row">
                  <div class="jd-target-info">
                    <span class="jd-role">{{ jd.role_title }}</span>
                    <span v-if="jd.company" class="jd-company">{{ jd.company }}</span>
                  </div>
                  <div class="jd-target-actions">
                    <span class="jd-fit-badge" :class="fitClass(jd.fit_score)">{{ jd.fit_score }}%</span>
                    <button
                      class="btn-ghost jd-rematch-btn"
                      :disabled="rematchingJdId === jd.id"
                      @click.stop="rematchJD(jd)"
                      title="Re-match this JD against this project only"
                    >
                      <span v-if="rematchingJdId === jd.id" class="spinner-sm" />
                      <span v-else>Re-match</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <div class="modal-footer">
            <div class="footer-left">
              <span class="date-info">Saved {{ formatDate(p.created_at) }}</span>
              <span v-if="p.updated_at" class="date-info">&nbsp;· Updated {{ formatDate(p.updated_at) }}</span>
            </div>
            <div class="footer-actions">
              <template v-if="store.modal.deleteConfirm">
                <span class="confirm-text">Delete this project?</span>
                <button class="btn-danger" @click="store.deleteProject(p.id)">Yes, delete</button>
                <button class="btn-secondary" @click="store.modal.deleteConfirm = false">Cancel</button>
              </template>
              <template v-else>
                <button class="btn-ghost danger-ghost" @click="store.modal.deleteConfirm = true">Delete</button>
                <button class="btn-primary" @click="store.modal.editing = true">Edit Context</button>
              </template>
            </div>
          </div>
        </template>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useProjectStore } from '../stores/projects'
import { useResumeStore } from '../stores/resume'
import ContextForm from './ContextForm.vue'

const store = useProjectStore()
const resumeStore = useResumeStore()
const p = computed(() => store.modal.project)

const matchedJDs = computed(() => {
  if (!p.value?.id) return []
  return (resumeStore.jdTargetsByProject[p.value.id] || [])
    .slice()
    .sort((a, b) => (b.fit_score || 0) - (a.fit_score || 0))
})

function fitClass(score) {
  if (score >= 80) return 'high'
  if (score >= 60) return 'mid'
  return 'low'
}

const rematchingJdId = ref(null)

async function rematchJD(jd) {
  rematchingJdId.value = jd.id
  try {
    await resumeStore.rematch(jd.id, [p.value.id])
  } finally {
    rematchingJdId.value = null
  }
}

// --- Bullet editing ---
const localBullets = ref([])
const editingBulletIdx = ref(null)
const editBulletText = ref('')
const originalBulletText = ref('')
const bulletSaved = ref(false)
const bulletInputRef = ref(null)

watch(() => p.value?.id, () => {
  localBullets.value = [...(p.value?.resume_bullets || [])]
  editingBulletIdx.value = null
}, { immediate: true })

function startEditBullet(i) {
  editingBulletIdx.value = i
  editBulletText.value = localBullets.value[i]
  originalBulletText.value = localBullets.value[i]
  nextTick(() => bulletInputRef.value?.focus())
}

async function confirmBullet(i) {
  if (editingBulletIdx.value !== i) return
  editingBulletIdx.value = null
  const text = editBulletText.value.trim()
  const newBullets = [...localBullets.value]
  if (text === '') {
    newBullets.splice(i, 1)
  } else {
    newBullets[i] = text
  }
  localBullets.value = newBullets
  await doSaveBullets(newBullets)
}

function cancelBullet(i) {
  if (originalBulletText.value === '') {
    localBullets.value = localBullets.value.filter((_, idx) => idx !== i)
  }
  editingBulletIdx.value = null
}

async function deleteBullet(i) {
  if (editingBulletIdx.value === i) editingBulletIdx.value = null
  const newBullets = localBullets.value.filter((_, idx) => idx !== i)
  localBullets.value = newBullets
  await doSaveBullets(newBullets)
}

async function addBullet() {
  localBullets.value = [...localBullets.value, '']
  editingBulletIdx.value = localBullets.value.length - 1
  editBulletText.value = ''
  originalBulletText.value = ''
  await nextTick()
  bulletInputRef.value?.focus()
}

async function doSaveBullets(bullets) {
  await store.saveBullets(bullets)
  bulletSaved.value = true
  setTimeout(() => { bulletSaved.value = false }, 1500)
}

const tabs = [
  { key: 'source',      label: 'Source & Context' },
  { key: 'summary',     label: 'Summary' },
  { key: 'highlights',  label: 'Highlights' },
  { key: 'bullets',     label: 'Resume Bullets' },
  { key: 'interview',   label: 'Interview' },
  { key: 'jd-targets',  label: `JD Targets${matchedJDs.value.length ? ` (${matchedJDs.value.length})` : ''}` },
]
const activeTab = ref('summary')

const contextFields = {
  business_background:      'Business background',
  team_client_requirements: 'Team / client requirements',
  pm_decisions:             'PM product decisions',
  t1_responsibilities:      'T1 — scope & design',
  t2_responsibilities:      'T2 — implementation',
  architecture_details:     'Architecture details',
  coordination:             'Cross-platform coordination',
  challenges:               'Challenges & tradeoffs',
  outcomes:                 'Outcomes & impact',
}

const hasAnyContext = computed(() =>
  p.value?.context && Object.values(p.value.context).some(v => v?.trim())
)

const sourceTypeLabel = computed(() => {
  const meta = p.value?.source_metadata || {}
  if (meta.filename) return meta.filename.split('.').pop().toUpperCase()
  if (meta.url?.includes('notion')) return 'Notion'
  if (meta.url) return 'URL'
  return 'Text'
})

const sourceName = computed(() => {
  const meta = p.value?.source_metadata || {}
  return meta.filename || meta.url || null
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(30, 20, 60, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Fixed size — does not resize with content */
.modal {
  background: var(--surface);
  border-radius: 12px;
  width: 760px;
  height: 82vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 48px rgba(40,20,100,0.22);
  overflow: hidden;
  flex-shrink: 0;
}

/* Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.header-main { flex: 1; min-width: 0; }
h2 { font-size: 15px; font-weight: 700; margin-bottom: 7px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta { display: flex; flex-wrap: wrap; gap: 5px; }

.close-btn { font-size: 15px; padding: 2px 7px; flex-shrink: 0; }

/* Tabs */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  padding: 0 20px;
  overflow-x: auto;
  flex-shrink: 0;
  background: #faf9fe;
}
.tab {
  background: none; border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0; padding: 9px 13px;
  font-size: 12px; font-weight: 500;
  color: var(--text-muted);
  margin-bottom: -1px; white-space: nowrap;
}
.tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 700; }
.tab:hover:not(.active) { color: var(--text); }

/* Scrollable body — fixed height fills remaining space */
.modal-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* Content sections */
.section { display: flex; flex-direction: column; gap: 18px; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field p { font-size: 13px; line-height: 1.75; color: var(--text); }
.field p.pre { white-space: pre-line; }
.field ul { padding-left: 18px; display: flex; flex-direction: column; gap: 6px; }
.field li { font-size: 13px; line-height: 1.65; }

/* Source & Context tab */
.source-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.meta-pill {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
  background: var(--tag-bg); color: var(--tag-text);
  padding: 3px 9px; border-radius: 100px;
}
.meta-path {
  font-size: 12px; color: var(--text-muted);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 360px;
}
.meta-chars { font-size: 11px; color: var(--text-muted); margin-left: auto; }

.raw-text {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 11px;
  line-height: 1.65;
  color: var(--text-muted);
  background: #f6f4fc;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px 14px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 220px;
  overflow-y: auto;
}

.divider {
  height: 1px;
  background: var(--border);
  margin: 4px 0;
}

.context-grid { display: flex; flex-direction: column; gap: 12px; }
.context-item { display: flex; flex-direction: column; gap: 3px; }
.context-key {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--text-muted);
}
.context-val { font-size: 13px; line-height: 1.65; color: var(--text); }
.empty-note { font-size: 12px; color: var(--text-muted); font-style: italic; }

/* Edit mode form */
.edit-hint { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
.edit-form-wrap { /* ContextForm fills this */ }

/* Category badges */
.category-badge {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; padding: 2px 8px; border-radius: 100px;
  background: #ede9fe; color: #5340b0;
}
.category-badge.backend  { background: #d1fae5; color: #065f46; }
.category-badge.mobile   { background: #f3e8ff; color: #6b21a8; }
.category-badge.data     { background: #fef9c3; color: #854d0e; }
.category-badge.devops   { background: #fee2e2; color: #991b1b; }
.category-badge.platform { background: #e0e7ff; color: #3730a3; }
.category-badge.other    { background: #f1f5f9; color: #475569; }

/* Footer */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
  background: #faf9fe;
  flex-wrap: wrap;
}
.footer-left { display: flex; gap: 2px; }
.date-info { font-size: 11px; color: var(--text-muted); }
.footer-actions { display: flex; align-items: center; gap: 8px; }
.confirm-text { font-size: 12px; color: var(--text); }
.error { font-size: 12px; color: var(--danger); flex: 1; }

.danger-ghost { color: var(--danger); }
.danger-ghost:hover { background: #fdf2f4; }

.summary-bullet {
  font-size: 13px;
  line-height: 1.75;
  color: var(--text);
  background: #f0f7ff;
  border-left: 3px solid var(--primary);
  padding: 8px 12px;
  border-radius: 0 6px 6px 0;
}

/* Bullet inline editing */
.bullets-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.saved-indicator {
  font-size: 11px;
  color: #16a34a;
  font-weight: 600;
}
.bullets-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
}
.bullet-row {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  padding: 3px 4px;
  border-radius: 5px;
}
.bullet-row:hover { background: #f5f3fc; }
.bullet-row:hover .bullet-delete { opacity: 1; }
.bullet-dot {
  font-size: 13px;
  color: var(--text-muted);
  padding-top: 1px;
  flex-shrink: 0;
}
.bullet-text {
  flex: 1;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text);
  cursor: text;
  word-break: break-word;
}
.bullet-textarea {
  flex: 1;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text);
  border: 1px solid var(--primary);
  border-radius: 4px;
  padding: 2px 6px;
  resize: none;
  outline: none;
  background: #faf9fe;
  font-family: inherit;
}
.bullet-delete {
  background: none;
  border: none;
  font-size: 11px;
  color: var(--text-muted);
  padding: 2px 4px;
  cursor: pointer;
  opacity: 0;
  flex-shrink: 0;
  line-height: 1.65;
  border-radius: 3px;
}
.bullet-delete:hover { color: var(--danger); background: #fdf2f4; }
.btn-add-bullet {
  margin-top: 8px;
  background: none;
  border: none;
  font-size: 12px;
  color: var(--primary);
  cursor: pointer;
  padding: 4px 0;
  font-weight: 500;
}
.btn-add-bullet:hover { text-decoration: underline; }

/* JD Targets tab */
.jd-target-list { display: flex; flex-direction: column; gap: 6px; }
.jd-target-row {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 10px 14px;
  border: 1px solid var(--border); border-radius: 8px;
  background: var(--surface);
}
.jd-target-info { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
.jd-role { font-size: 13px; font-weight: 600; color: var(--text); }
.jd-company { font-size: 11px; color: var(--text-muted); }

.jd-target-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

.jd-fit-badge {
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 100px; flex-shrink: 0;
}
.jd-fit-badge.high { background: #dcfce7; color: #166534; }
.jd-fit-badge.mid  { background: #fef9c3; color: #854d0e; }
.jd-fit-badge.low  { background: #f1f5f9; color: #475569; }

.jd-rematch-btn { font-size: 11px; padding: 3px 9px; min-width: 64px; }

.spinner-sm {
  display: inline-block;
  width: 10px; height: 10px;
  border: 2px solid rgba(0,0,0,0.12);
  border-top-color: var(--text-muted);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
