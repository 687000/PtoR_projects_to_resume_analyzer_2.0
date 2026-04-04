<template>
  <div class="list-editor">
    <div v-for="(item, i) in items" :key="i" class="list-row">
      <textarea v-model="items[i]" rows="2" @input="emit('update:modelValue', [...items])" />
      <button type="button" class="btn-ghost remove" @click="remove(i)" title="Remove">✕</button>
    </div>
    <button type="button" class="btn-secondary add" @click="add">+ Add</button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])

const items = ref([...props.modelValue])

watch(() => props.modelValue, v => { items.value = [...v] })

function add() {
  items.value.push('')
  emit('update:modelValue', [...items.value])
}
function remove(i) {
  items.value.splice(i, 1)
  emit('update:modelValue', [...items.value])
}
</script>

<style scoped>
.list-editor { display: flex; flex-direction: column; gap: 6px; }
.list-row { display: flex; gap: 6px; align-items: flex-start; }
.list-row textarea { flex: 1; }
.remove { padding: 6px 8px; color: var(--text-muted); }
.remove:hover { color: var(--danger); }
.add { align-self: flex-start; font-size: 12px; padding: 4px 10px; }
</style>
