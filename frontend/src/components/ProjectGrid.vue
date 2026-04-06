<template>
  <div>
    <!-- Search & filters -->
    <div class="filters mb-16">
      <input v-model="search" placeholder="Search projects…" style="max-width:280px;" />
      <select v-model="filterCategory" style="max-width:160px;">
        <option value="">All categories</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
    </div>

    <div v-if="store.loading" class="flex-center" style="padding:40px; justify-content:center;">
      <span class="spinner" /> Loading…
    </div>

    <div v-else-if="!filtered.length" class="empty-state">
      <h3>No projects yet</h3>
      <p>Upload a project above to get started.</p>
    </div>

    <div v-else class="grid-2">
      <ProjectCard v-for="p in filtered" :key="p.id" :project="p" />
    </div>

    <ProjectModal />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProjectStore } from '../stores/projects'
import ProjectCard from './ProjectCard.vue'
import ProjectModal from './ProjectModal.vue'

const store = useProjectStore()
const search = ref('')
const filterCategory = ref('')
const categories = ['web_app', 'mobile', 'backend', 'data', 'devops', 'platform', 'other']

onMounted(() => store.fetchProjects())

const filtered = computed(() => {
  let list = store.list
  if (filterCategory.value) {
    list = list.filter(p => p.category === filterCategory.value)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(p =>
      (p.title || '').toLowerCase().includes(q) ||
      (p.analysis?.summary || '').toLowerCase().includes(q) ||
      (p.tags || []).some(t => t.toLowerCase().includes(q))
    )
  }
  return list
})
</script>

<style scoped>
.filters { display: flex; gap: 10px; flex-wrap: wrap; }
</style>
