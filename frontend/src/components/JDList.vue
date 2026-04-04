<template>
  <div class="jd-list-section">
    <div class="toolbar">
      <input
        type="text"
        class="search-input"
        v-model="query"
        placeholder="Search job targets…"
      />
      <span class="count">{{ filtered.length }} target{{ filtered.length !== 1 ? 's' : '' }}</span>
    </div>

    <div v-if="store.loading && !store.targets.length" class="empty">Loading…</div>

    <div v-else-if="!store.targets.length" class="empty">
      <p>No job targets yet.</p>
      <button class="btn-primary" @click="store.upload.open = true">Add your first job target</button>
    </div>

    <div v-else-if="!filtered.length" class="empty">
      <p>No targets match your search.</p>
      <button class="btn-secondary" @click="query = ''">Clear</button>
    </div>

    <div v-else class="grid">
      <div
        v-for="t in filtered"
        :key="t.id"
        class="card"
        @click="store.openModal(t)"
      >
        <div class="card-header">
          <span class="date">{{ formatDate(t.created_at) }}</span>
          <span v-if="t.updated_at" class="updated-badge">updated</span>
        </div>

        <div class="card-title">
          <span class="role">{{ t.role_title }}</span>
          <span v-if="t.company" class="company">{{ t.company }}</span>
        </div>

        <div class="match-summary">
          <span v-if="bestScore(t)" class="fit-badge" :class="fitClass(bestScore(t))">
            Best match: {{ bestScore(t) }}%
          </span>
          <span class="match-count">{{ t.matched_projects?.length || 0 }} project{{ (t.matched_projects?.length || 0) !== 1 ? 's' : '' }} matched</span>
        </div>

        <div class="req-chips">
          <span v-for="kw in topRequirements(t)" :key="kw" class="req-chip">{{ kw }}</span>
        </div>

        <div class="card-actions" @click.stop>
          <button class="btn-ghost" @click="store.openModal(t)">View Resume</button>
          <button
            class="btn-ghost"
            :disabled="rematching === t.id"
            @click="doRematch(t.id)"
          >
            <span v-if="rematching === t.id" class="spinner dark" />
            <span v-else>Re-match</span>
          </button>
          <button class="btn-ghost danger" @click.stop="confirmId = t.id">Delete</button>
        </div>

        <div v-if="confirmId === t.id" class="delete-confirm" @click.stop>
          <span>Delete "{{ t.role_title }}"?</span>
          <button class="btn-danger" @click="doDelete(t.id)">Yes, delete</button>
          <button class="btn-secondary" @click="confirmId = null">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useResumeStore } from '../stores/resume'

const store = useResumeStore()
const query = ref('')
const confirmId = ref(null)
const rematching = ref(null)

const filtered = computed(() => {
  const q = query.value.toLowerCase()
  if (!q) return store.sortedTargets
  return store.sortedTargets.filter(t => {
    const hay = `${t.role_title} ${t.company || ''} ${
      (t.extracted_requirements?.tech_stack || []).join(' ')
    }`.toLowerCase()
    return hay.includes(q)
  })
})

function bestScore(target) {
  const projects = target.matched_projects || []
  if (!projects.length) return null
  return Math.max(...projects.map(p => p.fit_score))
}

function fitClass(score) {
  if (score >= 80) return 'high'
  if (score >= 60) return 'mid'
  return 'low'
}

function topRequirements(target) {
  const r = target.extracted_requirements || {}
  return [...(r.tech_stack || []), ...(r.domain || [])].slice(0, 5)
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

async function doRematch(id) {
  rematching.value = id
  await store.rematch(id)
  rematching.value = null
}

function doDelete(id) {
  store.deleteTarget(id)
  confirmId.value = null
}
</script>

<style scoped>
.jd-list-section { display: flex; flex-direction: column; gap: 14px; }

.toolbar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.search-input { flex: 1; min-width: 200px; max-width: 320px; }
.count { font-size: 12px; color: var(--text-muted); margin-left: auto; }

.empty {
  text-align: center; color: var(--text-muted);
  padding: 48px 24px;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  display: flex; flex-direction: column; gap: 10px;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
  box-shadow: var(--shadow);
}
.card:hover { box-shadow: var(--shadow-md); border-color: #c7d7ed; }

.card-header { display: flex; align-items: center; gap: 8px; }
.date { font-size: 11px; color: var(--text-muted); }
.updated-badge {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.04em;
  background: #e0e7ff; color: #3730a3;
  padding: 1px 6px; border-radius: 100px;
}

.card-title { display: flex; flex-direction: column; gap: 2px; }
.role { font-size: 14px; font-weight: 600; line-height: 1.3; }
.company { font-size: 12px; color: var(--text-muted); }

.match-summary { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.fit-badge {
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 100px;
}
.fit-badge.high { background: #dcfce7; color: #166534; }
.fit-badge.mid  { background: #fef9c3; color: #854d0e; }
.fit-badge.low  { background: #f1f5f9; color: #475569; }
.match-count { font-size: 12px; color: var(--text-muted); }

.req-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.req-chip {
  font-size: 11px; font-weight: 500;
  background: var(--tag-bg); color: var(--tag-text);
  padding: 2px 8px; border-radius: 100px;
}

.card-actions {
  display: flex; gap: 4px; margin-top: auto;
  padding-top: 4px; border-top: 1px solid var(--border);
}
.btn-ghost { font-size: 12px; padding: 4px 10px; }
.btn-ghost.danger:hover { color: var(--danger); }

.delete-confirm {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 10px; background: #fff5f5;
  border: 1px solid #fecaca; border-radius: 6px; font-size: 12px;
}
.delete-confirm span { flex: 1; color: var(--text); }
.delete-confirm button { padding: 4px 10px; font-size: 12px; }

.spinner.dark {
  border-color: rgba(0,0,0,0.15);
  border-top-color: var(--text-muted);
}
</style>
