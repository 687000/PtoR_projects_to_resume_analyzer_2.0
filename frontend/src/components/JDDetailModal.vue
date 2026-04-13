<template>
  <div v-if="detail.open" class="modal-overlay" @click.self="store.closeDetail">
    <div class="modal" style="max-width:860px;" @mousedown="onModalMousedown">
      <div class="modal-header">
        <div>
          <div style="font-weight:700; font-size:15px;">{{ jd.title }}</div>
          <div class="text-muted text-small">{{ jd.company || 'Unknown company' }}</div>
          <div v-if="jd.seniority_fit" class="mt-8">
            <span class="badge" :class="fitBadge(jd.seniority_fit)">Seniority: {{ jd.seniority_fit }}</span>
            <span class="text-small text-muted" style="margin-left:8px;">{{ jd.seniority_fit_reason }}</span>
          </div>
        </div>
        <button class="btn-ghost" @click="store.closeDetail" style="font-size:18px;">✕</button>
      </div>

      <div class="modal-body">
        <!-- Requirements panel -->
        <div class="req-panel mb-16">
          <div class="section-title">Extracted Requirements</div>
          <div class="tags">
            <span v-for="t in allRequirements" :key="t" class="chip">{{ t }}</span>
          </div>
        </div>

        <!-- No matches -->
        <div v-if="!matchedProjects.length" class="empty-state" style="padding:30px;">
          <h3>No projects matched</h3>
          <p>Add more projects on the Projects page to improve results.</p>
        </div>

        <!-- Matched project sections -->
        <div v-for="(mp, idx) in matchedProjects" :key="mp.project_id" class="matched-section card mb-12">
          <!-- Header -->
          <div class="section-header">
            <div class="header-left">
              <div class="project-title-row">
                <span class="project-number">#{{ idx + 1 }}</span>
                <h3 class="project-title">{{ mp.project_title }}</h3>
              </div>
              <div class="tags mt-8">
                <span v-for="r in mp.addressed_requirements?.slice(0,4)" :key="r" class="chip">{{ r }}</span>
              </div>
            </div>
            <div class="header-right">
              <span class="score-badge" :class="scoreClass(mp.fit_score)">{{ mp.fit_score }}%</span>
            </div>
          </div>

          <!-- Fit reason -->
          <div class="fit-reason" v-if="mp.fit_reason">{{ mp.fit_reason }}</div>

          <!-- Bullets list -->
          <div class="bullets-section">
            <div v-for="(b, bi) in mp.tailored_bullets" :key="bi" class="bullet-row" @click="handleBulletRowClick(mp, bi, $event)">
              <input class="bullet-checkbox" type="checkbox" :checked="b.included" @click.stop @change="toggleBullet(mp, bi, $event.target.checked)" />
              <div class="bullet-content">
                <template v-if="editingBullet?.mp === idx && editingBullet?.bi === bi">
                  <textarea
                    :ref="el => textareaRef.value = el"
                    v-model="editBulletText"
                    rows="2"
                    class="bullet-edit-input"
                    @blur="saveBulletEdit(mp, bi)"
                    @keydown.escape="editingBullet = null"
                    @click.stop=""
                  />
                </template>
                <template v-else>
                  <span
                    class="bullet-text"
                    :class="{ 'bullet-unchecked': !b.included }"
                    @click.stop="startBulletEdit(idx, bi, b.bullet)"
                  >{{ b.bullet }}</span>
                  <span v-if="b.source === 'generated'" class="badge badge-blue" style="font-size:9px; margin-left:6px;">AI</span>
                </template>
              </div>
            </div>
          </div>

        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-primary" style="margin-right:auto;" @click="openExport">Copy Resume Section</button>
        <button class="btn-secondary" @click="store.closeDetail">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useToast } from '../composables/toast'

const store = useResumeStore()
const toast = useToast()
const detail = store.detail
const jd = computed(() => detail.jd || {})

const editingBullet = ref(null)
const editBulletText = ref('')
const textareaRef = ref(null)

const matchedProjects = computed(() => jd.value.match_results?.projects || [])

const allRequirements = computed(() => {
  const req = jd.value.extracted_requirements || {}
  return [...(req.tech_stack || []), ...(req.domain || []), ...(req.collaboration || [])].slice(0, 12)
})

function scoreClass(score) {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-mid'
  return 'score-low'
}

function fitBadge(fit) {
  if (fit === 'meets') return 'badge-green'
  if (fit === 'partial') return 'badge-yellow'
  return 'badge-gray'
}

function startBulletEdit(mpIdx, bi, text) {
  editingBullet.value = { mp: mpIdx, bi }
  editBulletText.value = text
  setTimeout(() => textareaRef.value?.focus(), 0)
}

function onModalMousedown(e) {
  if (!editingBullet.value) return
  const el = textareaRef.value
  if (el && !el.contains(e.target)) {
    el.blur()
  }
}

function handleBulletRowClick(mp, bi, e) {
  const clickedContent = e.target.closest('.bullet-content')
  if (!clickedContent) {
    const included = !mp.tailored_bullets[bi].included
    toggleBullet(mp, bi, included)
  }
}

async function saveBulletEdit(mp, bi) {
  if (!editingBullet.value) return
  const newText = editBulletText.value.trim()
  if (newText && newText !== mp.tailored_bullets[bi].bullet) {
    mp.tailored_bullets[bi] = { ...mp.tailored_bullets[bi], bullet: newText, source: 'user' }
    await persistMatchResults()
  }
  editingBullet.value = null
}

async function toggleBullet(mp, bi, included) {
  mp.tailored_bullets[bi] = { ...mp.tailored_bullets[bi], included }
  await persistMatchResults()
}

async function persistMatchResults() {
  try {
    await store.updateJdBullets(jd.value.id, jd.value.match_results)
  } catch (e) {
    toast.error(e.message)
  }
}

function openExport() {
  store.openExport(jd.value)
}
</script>

<style scoped>
/* Layout */
.req-panel { background: var(--surface2); border-radius: var(--radius-sm); padding: 12px; }
.matched-section { padding: 18px; }

/* Header section */
.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
  padding-bottom: 14px;
  border-bottom: 2px solid var(--border);
}

.header-left { flex: 1; }
.header-right { display: flex; align-items: center; gap: 12px; }

.project-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.project-number {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  min-width: 30px;
}

.project-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  line-height: 1.3;
  color: var(--text-primary);
}

/* Tags */
.tags { display: flex; flex-wrap: wrap; gap: 6px; }

/* Score badge */
.score-badge {
  font-size: 14px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  min-width: 50px;
  text-align: center;
  flex-shrink: 0;
}

.score-high { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.score-mid { background: rgba(234, 179, 8, 0.15); color: #eab308; }
.score-low { background: rgba(107, 114, 128, 0.15); color: #6b7280; }

/* Fit reason */
.fit-reason {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 14px;
  padding: 10px 12px;
  background: var(--surface2);
  border-radius: var(--radius-sm);
  line-height: 1.5;
}

/* Bullets section */
.bullets-section { margin-top: 4px; }

.bullet-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-radius: 4px;
  transition: background 0.15s ease;
}

.bullet-row:hover {
  background: var(--surface2);
}

.bullet-row:last-of-type { border-bottom: none; }

.bullet-checkbox {
  flex: 0 0 20px;
  width: 20px;
  height: 20px;
  margin-top: 2px;
  cursor: pointer;
  accent-color: var(--accent);
  transition: transform 0.15s ease;
}

.bullet-checkbox:hover {
  transform: scale(1.1);
}

.bullet-content {
  flex: 1;
  min-width: 0;
}

.bullet-text {
  cursor: text;
  line-height: 1.6;
  font-size: 14px;
  color: var(--text-primary);
  word-break: break-word;
  transition: color 0.15s ease;
}

.bullet-text:hover {
  color: var(--accent);
}

.bullet-unchecked {
  opacity: 0.5;
}

.bullet-unchecked:hover {
  color: var(--text-primary);
}

.bullet-edit-input {
  width: 100%;
  font-size: 14px;
  padding: 8px;
  line-height: 1.6;
  border: 2px solid var(--accent);
  border-radius: var(--radius-sm);
  font-family: inherit;
  resize: vertical;
}

.bullet-edit-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.1);
}
</style>
