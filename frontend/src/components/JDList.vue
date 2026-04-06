<template>
  <div>
    <div v-if="store.loading" class="flex-center" style="padding:40px; justify-content:center;">
      <span class="spinner" /> Loading…
    </div>

    <div v-else-if="!store.list.length" class="empty-state">
      <h3>No job targets yet</h3>
      <p>Upload a job description above to generate tailored resume content.</p>
    </div>

    <div v-else class="grid-2">
      <div
        v-for="jd in store.list"
        :key="jd.id"
        class="card jd-card"
      >
        <div class="flex-between mb-8">
          <div>
            <div style="font-weight:700; font-size:14px;">{{ jd.title || 'Untitled Role' }}</div>
            <div class="text-muted text-small">{{ jd.company || 'Unknown company' }} · {{ formatDate(jd.created_at) }}</div>
          </div>
          <span class="score-badge" :class="scoreClass(bestScore(jd))">
            {{ bestScore(jd) > 0 ? bestScore(jd) + '%' : '—' }}
          </span>
        </div>

        <div class="tags mb-8">
          <span v-for="t in topTech(jd)" :key="t" class="chip">{{ t }}</span>
        </div>

        <div class="text-small text-muted mb-12">
          {{ matchCount(jd) }} project{{ matchCount(jd) !== 1 ? 's' : '' }} matched
          <span v-if="jd.seniority_fit" class="ml-8">
            · Seniority: <span :class="fitClass(jd.seniority_fit)">{{ jd.seniority_fit }}</span>
          </span>
        </div>

        <div class="flex-center gap-8">
          <button class="btn-primary" style="font-size:12px; padding:4px 12px;" @click="store.openDetail(jd)">View Resume</button>
          <button class="btn-secondary" style="font-size:12px; padding:4px 10px;" :disabled="rematching === jd.id" @click="rematch(jd)">
            <span v-if="rematching === jd.id"><span class="spinner" style="width:10px;height:10px;margin-right:4px;" /></span>
            Re-match
          </button>
          <button class="btn-danger" style="font-size:12px; padding:4px 10px;" @click="del(jd)">Delete</button>
        </div>
      </div>
    </div>

    <JDDetailModal />
    <ResumeExportModal />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useToast } from '../composables/toast'
import JDDetailModal from './JDDetailModal.vue'
import ResumeExportModal from './ResumeExportModal.vue'

const store = useResumeStore()
const toast = useToast()
const rematching = ref(null)

onMounted(() => store.fetchJdTargets())

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function bestScore(jd) {
  const projects = jd.match_results?.projects || []
  if (!projects.length) return 0
  return Math.max(...projects.map(p => p.fit_score || 0))
}

function matchCount(jd) {
  return (jd.match_results?.projects || []).length
}

function topTech(jd) {
  return (jd.extracted_requirements?.tech_stack || []).slice(0, 4)
}

function scoreClass(score) {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-mid'
  return 'score-low'
}

function fitClass(fit) {
  if (fit === 'meets') return 'text-accent'
  if (fit === 'partial') return ''
  return 'text-muted'
}

async function rematch(jd) {
  rematching.value = jd.id
  try {
    await store.rematch(jd.id)
    toast.success('Re-matched!')
  } catch (e) {
    toast.error(e.message)
  } finally {
    rematching.value = null
  }
}

async function del(jd) {
  if (!confirm(`Delete "${jd.title}"?`)) return
  try {
    await store.deleteJd(jd.id)
    toast.success('Deleted')
  } catch (e) {
    toast.error(e.message)
  }
}
</script>

<style scoped>
.jd-card { cursor: default; }
.tags { display: flex; flex-wrap: wrap; gap: 4px; }
.ml-8 { margin-left: 8px; }
</style>
