<template>
  <div class="page">
    <div class="page-header">
      <h1>Projects</h1>
      <p class="text-muted">Build your project library. Each project becomes a reusable asset for resume generation.</p>
    </div>
    <ProjectUploader />
    <ProjectGrid />
  </div>
</template>

<script setup>
import ProjectUploader from './ProjectUploader.vue'
import ProjectGrid from './ProjectGrid.vue'
</script>
