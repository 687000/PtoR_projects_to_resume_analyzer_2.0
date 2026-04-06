<template>
  <div v-if="detail.open" class="modal-overlay" @click.self="store.closeDetail">
    <div class="modal" style="max-width:860px;">
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
          <div class="flex-between mb-10">
            <div>
              <span style="font-weight:700;">#{{ idx + 1 }} {{ mp.project_title }}</span>
              <div class="tags mt-6">
                <span v-for="r in mp.addressed_requirements?.slice(0,4)" :key="r" class="chip">{{ r }}</span>
              </div>
            </div>
            <div class="flex-center gap-8">
              <span class="score-badge" :class="scoreClass(mp.fit_score)">{{ mp.fit_score }}%</span>
            </div>
          </div>

          <div class="text-small text-muted mb-10" v-if="mp.fit_reason">{{ mp.fit_reason }}</div>

          <!-- Bullets list -->
          <div v-for="(b, bi) in mp.tailored_bullets" :key="bi" class="bullet-row">
            <input class="bullet-checkbox" type="checkbox" :checked="b.included" @change="toggleBullet(mp, bi, $event.target.checked)" />
            <div class="bullet-content">
              <template v-if="editingBullet?.mp === idx && editingBullet?.bi === bi">
                <textarea
                  v-model="editBulletText"
                  rows="2"
                  class="bullet-edit-input"
                  @blur="saveBulletEdit(mp, bi)"
                  @keydown.escape="editingBullet = null"
                />
              </template>
              <template v-else>
                <span
                  class="bullet-text"
                  :class="{ 'bullet-unchecked': !b.included }"
                  @click="startBulletEdit(idx, bi, b.bullet)"
                >{{ b.bullet }}</span>
                <span v-if="b.source === 'generated'" class="badge badge-blue" style="font-size:9px; margin-left:6px;">AI</span>
              </template>
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
.req-panel { background: var(--surface2); border-radius: var(--radius-sm); padding: 12px; }
.tags { display: flex; flex-wrap: wrap; gap: 4px; }
.matched-section { padding: 14px; }
.bullet-row {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 6px 0; border-bottom: 1px solid var(--border);
  .bullet-checkbox {
    flex: 0 0 50px;
  }
}
.bullet-row:last-of-type { border-bottom: none; }
.bullet-content { flex: 1; }
.bullet-text { cursor: text; line-height: 1.5; }
.bullet-text:hover { color: var(--accent); }
.bullet-unchecked { opacity: 0.4; }
.bullet-edit-input { width: 100%; font-size: 13px; padding: 4px; }
</style>
