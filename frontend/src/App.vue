<template>
  <div>
    <nav class="nav">
      <div class="nav-logo">PtoR</div>
      <div
        class="nav-link"
        :class="{ active: page === 'projects' }"
        @click="page = 'projects'"
      >Projects</div>
      <div
        class="nav-link"
        :class="{ active: page === 'resume' }"
        @click="page = 'resume'"
      >Resume</div>
    </nav>

    <ProjectsPage v-if="page === 'projects'" />
    <ResumePage v-else />

    <ToastContainer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ProjectsPage from './components/ProjectsPage.vue'
import ResumePage from './components/ResumePage.vue'
import ToastContainer from './components/ToastContainer.vue'

const page = ref('projects')
</script>
