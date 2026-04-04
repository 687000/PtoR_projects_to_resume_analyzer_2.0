<template>
  <div class="card" @click="store.openModal(project)">
    <div class="card-header">
      <span class="category-badge" :class="project.category">{{ project.category }}</span>
      <span class="date">{{ formatDate(project.created_at) }}</span>
    </div>

    <h3 class="title">{{ project.title }}</h3>

    <p class="summary">{{ truncate(project.summary, 120) }}</p>

    <div class="tags">
      <span v-for="tag in project.tags?.slice(0, 4)" :key="tag" class="tag">{{ tag.replace(/_/g, ' ') }}</span>
    </div>

    <div class="card-actions" @click.stop>
      <button class="btn-ghost" title="View" @click="store.openModal(project)">View</button>
      <button class="btn-ghost danger" title="Delete" @click="confirmDelete">Delete</button>
    </div>

    <div v-if="showConfirm" class="delete-confirm" @click.stop>
      <span>Delete "{{ truncate(project.title, 30) }}"?</span>
      <button class="btn-danger" @click="doDelete">Yes, delete</button>
      <button class="btn-secondary" @click="showConfirm = false">Cancel</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useProjectStore } from '../stores/projects'

const props = defineProps({ project: { type: Object, required: true } })
const store = useProjectStore()
const showConfirm = ref(false)

function confirmDelete() { showConfirm.value = true }
function doDelete() { store.deleteProject(props.project.id) }

function truncate(str, n) {
  if (!str) return ''
  return str.length > n ? str.slice(0, n) + '…' : str
}
function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
  box-shadow: var(--shadow);
}
.card:hover { box-shadow: var(--shadow-md); border-color: #c7d7ed; }

.card-header { display: flex; justify-content: space-between; align-items: center; }

.category-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 8px;
  border-radius: 100px;
  background: #dbeafe;
  color: #1e40af;
}
.category-badge.backend { background: #dcfce7; color: #166534; }
.category-badge.mobile { background: #f3e8ff; color: #6b21a8; }
.category-badge.data { background: #fef9c3; color: #854d0e; }
.category-badge.devops { background: #fee2e2; color: #991b1b; }
.category-badge.platform { background: #e0e7ff; color: #3730a3; }
.category-badge.other { background: #f1f5f9; color: #475569; }

.date { font-size: 11px; color: var(--text-muted); }

.title { font-size: 14px; font-weight: 600; line-height: 1.4; }

.summary { font-size: 12px; color: var(--text-muted); line-height: 1.5; }

.tags { display: flex; flex-wrap: wrap; gap: 4px; }

.card-actions {
  display: flex;
  gap: 4px;
  margin-top: auto;
  padding-top: 4px;
  border-top: 1px solid var(--border);
}
.btn-ghost { font-size: 12px; padding: 4px 10px; }
.btn-ghost.danger:hover { color: var(--danger); }

.delete-confirm {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 10px;
  background: #fff5f5;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 12px;
}
.delete-confirm span { flex: 1; color: var(--text); }
.delete-confirm button { padding: 4px 10px; font-size: 12px; }
</style>
