<template>
  <div class="page">
    <div class="page-header">
      <h1>Resume</h1>
      <p class="text-muted">Upload a job description to match your projects and generate tailored resume content.</p>
    </div>
    <JDUploader />
    <JDList />
  </div>
</template>

<script setup>
import JDUploader from './JDUploader.vue'
import JDList from './JDList.vue'
</script>
