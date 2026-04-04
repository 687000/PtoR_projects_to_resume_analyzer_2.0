<template>
  <div id="app">
    <header>
      <div class="header-inner">
        <div class="logo">
          <span class="logo-mark">P→R</span>
          <span class="logo-text">Project-to-Resume</span>
        </div>

        <nav class="nav-tabs">
          <button
            class="nav-tab"
            :class="{ active: page === 'projects' }"
            @click="page = 'projects'"
          >Projects</button>
          <button
            class="nav-tab"
            :class="{ active: page === 'resume' }"
            @click="page = 'resume'"
          >Resume</button>
        </nav>

        <span v-if="projectStore.error || resumeStore.error" class="global-error">
          {{ projectStore.error || resumeStore.error }}
        </span>
      </div>
    </header>

    <main>
      <template v-if="page === 'projects'">
        <ProjectUploader />
        <ProjectGrid />
        <ProjectModal v-if="projectStore.modal.open" />
      </template>

      <template v-else>
        <JDUploader />
        <JDList />
        <JDDetailModal v-if="resumeStore.modal.open" />
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProjectStore } from './stores/projects'
import { useResumeStore } from './stores/resume'
import ProjectUploader from './components/ProjectUploader.vue'
import ProjectGrid from './components/ProjectGrid.vue'
import ProjectModal from './components/ProjectModal.vue'
import JDUploader from './components/JDUploader.vue'
import JDList from './components/JDList.vue'
import JDDetailModal from './components/JDDetailModal.vue'

const page = ref('projects')
const projectStore = useProjectStore()
const resumeStore = useResumeStore()

onMounted(() => {
  projectStore.fetchAll()
  resumeStore.fetchAll()
})
</script>

<style scoped>
#app { min-height: 100vh; display: flex; flex-direction: column; }

header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  height: 52px;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo { display: flex; align-items: center; gap: 10px; }
.logo-mark {
  background: var(--primary);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
  letter-spacing: 0.02em;
}
.logo-text { font-size: 15px; font-weight: 600; color: var(--text); }

.nav-tabs {
  display: flex;
  gap: 2px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 3px;
}
.nav-tab {
  background: none;
  border: none;
  border-radius: 6px;
  padding: 4px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  transition: background 0.15s, color 0.15s;
}
.nav-tab.active {
  background: var(--surface);
  color: var(--primary);
  font-weight: 700;
  box-shadow: var(--shadow);
}
.nav-tab:hover:not(.active) { color: var(--text); }

.global-error {
  font-size: 12px;
  color: var(--danger);
  margin-left: auto;
}

main {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 24px auto;
  padding: 0 24px;
}
</style>
