<template>
  <div class="toast-container">
    <div
      v-for="t in toasts"
      :key="t.id"
      class="toast"
      :class="`toast-${t.type}`"
    >{{ t.message }}</div>
  </div>
</template>

<script setup>
import { useToast } from '../composables/toast'
const { toasts } = useToast()
</script>
