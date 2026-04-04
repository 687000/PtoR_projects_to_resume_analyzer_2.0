<template>
  <div class="grid-section">
    <div class="toolbar">
      <input
        type="text"
        class="search-input"
        v-model="store.search.query"
        placeholder="Search projects…"
      />
      <select v-model="store.search.category" class="filter-select">
        <option value="">All categories</option>
        <option v-for="cat in store.allCategories" :key="cat" :value="cat">{{ cat }}</option>
      </select>
      <select v-model="store.search.tag" class="filter-select">
        <option value="">All tags</option>
        <option v-for="tag in store.allTags" :key="tag" :value="tag">{{ tag.replace(/_/g, ' ') }}</option>
      </select>
      <span class="count">{{ store.filteredProjects.length }} project{{ store.filteredProjects.length !== 1 ? 's' : '' }}</span>
    </div>

    <div v-if="store.loading && !store.projects.length" class="loading">Loading…</div>

    <div v-else-if="!store.projects.length" class="empty">
      <p>No projects yet.</p>
      <button class="btn-primary" @click="store.upload.open = true">Add your first project</button>
    </div>

    <div v-else-if="!store.filteredProjects.length" class="empty">
      <p>No projects match your search.</p>
      <button class="btn-secondary" @click="clearFilters">Clear filters</button>
    </div>

    <div v-else class="grid">
      <div
        v-for="p in store.filteredProjects"
        :key="p.id"
        class="draggable-card"
        :class="{
          dragging: draggedProjectId === p.id,
          'drag-over': draggedOverProjectId === p.id,
        }"
        draggable="true"
        @dragstart="onDragStart($event, p)"
        @dragover="onDragOver($event, p)"
        @drop="onDrop($event, p)"
        @dragleave="onDragLeave($event, p)"
        @dragend="onDragEnd"
      >
        <ProjectCard :project="p" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useProjectStore } from '../stores/projects'
import ProjectCard from './ProjectCard.vue'

const store = useProjectStore()
const draggedProjectId = ref(null)
const draggedOverProjectId = ref(null)

function clearFilters() {
  store.search.query = ''
  store.search.category = ''
  store.search.tag = ''
}

function onDragStart(event, project) {
  draggedProjectId.value = project.id
  event.dataTransfer.effectAllowed = 'move'
}

function onDragOver(event, project) {
  event.preventDefault()
  if (draggedProjectId.value === project.id) return
  draggedOverProjectId.value = project.id
  event.dataTransfer.dropEffect = 'move'
}

function onDrop(event, project) {
  event.preventDefault()
  if (!draggedProjectId.value || draggedProjectId.value === project.id) {
    draggedProjectId.value = null
    draggedOverProjectId.value = null
    return
  }

  store.reorderProjects(draggedProjectId.value, project.id)
  draggedProjectId.value = null
  draggedOverProjectId.value = null
}

function onDragLeave(event, project) {
  if (draggedOverProjectId.value === project.id) {
    draggedOverProjectId.value = null
  }
}

function onDragEnd() {
  draggedProjectId.value = null
  draggedOverProjectId.value = null
}
</script>

<style scoped>
.grid-section { display: flex; flex-direction: column; gap: 14px; }

.toolbar {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}

.filter-select {
  font-family: inherit;
  font-size: 13px;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 7px 10px;
  outline: none;
  cursor: pointer;
}
.filter-select:focus { border-color: var(--primary); }

.count { font-size: 12px; color: var(--text-muted); margin-left: auto; }

.loading, .empty {
  text-align: center;
  color: var(--text-muted);
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.draggable-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.draggable-card.drag-over {
  transform: scale(1.01);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.18);
}

.draggable-card.dragging {
  opacity: 0.6;
}
</style>
