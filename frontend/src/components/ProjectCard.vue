<template>
  <div class="card project-card" @click="store.openModal(project)">
    <div class="flex-between mb-8">
      <span class="badge badge-blue">{{ project.category || 'other' }}</span>
      <span class="text-muted text-small">{{ formatDate(project.created_at) }}</span>
    </div>

    <h3 class="card-title">{{ project.title || 'Untitled Project' }}</h3>

    <p class="card-summary text-muted">{{ summary }}</p>

    <div v-if="project.tags?.length" class="tags">
      <span v-for="t in project.tags.slice(0, 4)" :key="t" class="chip">{{ t }}</span>
    </div>

    <div class="card-actions" @click.stop>
      <button class="btn-secondary" style="font-size:12px; padding:4px 10px;" @click="store.openModal(project)">View</button>
      <button class="btn-danger" style="font-size:12px; padding:4px 10px;" @click="confirmDelete">Delete</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useProjectStore } from '../stores/projects'
import { useToast } from '../composables/toast'

const props = defineProps({ project: { type: Object, required: true } })
const store = useProjectStore()
const toast = useToast()

const summary = computed(() => {
  const a = props.project.analysis
  return (a?.summary || a?.summary_bullet || '').slice(0, 120) + (
    (a?.summary || a?.summary_bullet || '').length > 120 ? '…' : ''
  )
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function confirmDelete() {
  if (!confirm(`Delete "${props.project.title}"?`)) return
  try {
    await store.deleteProject(props.project.id)
    toast.success('Project deleted')
  } catch (e) {
    toast.error(e.message)
  }
}
</script>

<style scoped>
.project-card { cursor: pointer; transition: border-color 0.15s, box-shadow 0.15s, transform 0.1s; }
.project-card:hover {
  border-color: rgba(67,97,238,0.3);
  box-shadow: 0 4px 20px rgba(67,97,238,0.1);
  transform: translateY(-1px);
}
.card-title { font-size: 14px; font-weight: 700; margin-bottom: 6px; color: var(--text); }
.card-summary { font-size: 12px; margin-bottom: 10px; line-height: 1.6; color: var(--text-muted); }
.tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.card-actions { display: flex; gap: 6px; }
</style>
