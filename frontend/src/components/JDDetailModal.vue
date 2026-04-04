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
              @click="store.rematch(t.id)"
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
              >
                <button
                  class="toggle-btn"
                  :title="b.included ? 'Exclude from export' : 'Include in export'"
                  @click="toggleBullet(mpIdx, bIdx)"
                >{{ b.included ? '☑' : '☐' }}</button>
                <span
                  v-if="editingKey !== `${mpIdx}-${bIdx}`"
                  class="bullet-text"
                  @click="startEdit(mpIdx, bIdx, b.text)"
                >{{ b.text }}</span>
                <textarea
                  v-else
                  class="bullet-edit"
                  v-model="editText"
                  rows="2"
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
            <button class="btn-secondary" @click="copyResume">
              {{ copied ? 'Copied!' : 'Copy Resume Section' }}
            </button>
            <button class="btn-primary" :disabled="store.modal.saving" @click="store.saveBullets()">
              <span v-if="store.modal.saving" class="spinner" />
              {{ store.modal.saving ? 'Saving…' : 'Save Changes' }}
            </button>
          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useResumeStore } from '../stores/resume'

const store = useResumeStore()
const t = computed(() => store.modal.target)
const matchedProjects = computed(() => t.value?.matched_projects || [])

const editingKey = ref(null)
const editText = ref('')
const copied = ref(false)

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

function copyResume() {
  const lines = []
  for (const mp of matchedProjects.value) {
    const included = mp.tailored_bullets.filter(b => b.included)
    if (!included.length) continue
    lines.push(mp.project_title)
    included.forEach(b => lines.push(`  • ${b.text}`))
    lines.push('')
  }
  navigator.clipboard.writeText(lines.join('\n').trim())
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
.bullet-list { display: flex; flex-direction: column; gap: 6px; list-style: none; padding: 0; }
.bullet-item {
  display: flex; align-items: flex-start; gap: 8px;
  transition: opacity 0.15s;
}
.bullet-item.excluded { opacity: 0.4; }

.toggle-btn {
  background: none; border: none; padding: 0;
  font-size: 15px; line-height: 1.6;
  color: var(--primary); cursor: pointer; flex-shrink: 0;
  min-width: 18px;
}
.toggle-btn:hover { opacity: 0.7; }

.bullet-text {
  font-size: 13px; line-height: 1.65; color: var(--text);
  cursor: text; flex: 1;
  border-radius: 3px; padding: 1px 3px;
  transition: background 0.1s;
}
.bullet-text:hover { background: var(--tag-bg); }

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
</style>
