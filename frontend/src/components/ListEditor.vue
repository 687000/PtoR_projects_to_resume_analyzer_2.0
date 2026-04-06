<template>
  <ul class="list-editor">
    <li v-for="(item, i) in items" :key="i" class="list-editor-row">
      <span class="bullet-dot">•</span>
      <template v-if="editIdx === i">
        <textarea
          v-model="editText"
          class="list-editor-input"
          rows="2"
          @blur="confirmEdit(i)"
          @keydown.enter.exact.prevent="confirmEdit(i)"
          @keydown.escape="cancelEdit"
          ref="textareaRef"
        />
      </template>
      <template v-else>
        <span class="list-editor-text" @click="startEdit(i, item)">{{ item }}</span>
      </template>
      <button class="btn-ghost list-editor-del" @click="remove(i)" title="Remove">✕</button>
    </li>
  </ul>
  <button class="btn-ghost" style="font-size:12px; margin-top:6px;" @click="addEmpty">+ Add item</button>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])

const items = ref([...props.modelValue])
const editIdx = ref(null)
const editText = ref('')
const textareaRef = ref(null)

function startEdit(i, text) {
  editIdx.value = i
  editText.value = text
  nextTick(() => textareaRef.value?.focus())
}

function confirmEdit(i) {
  if (editIdx.value !== i) return
  items.value[i] = editText.value.trim() || items.value[i]
  editIdx.value = null
  emit('update:modelValue', [...items.value])
}

function cancelEdit() {
  editIdx.value = null
}

function remove(i) {
  items.value.splice(i, 1)
  emit('update:modelValue', [...items.value])
}

function addEmpty() {
  items.value.push('')
  nextTick(() => startEdit(items.value.length - 1, ''))
}
</script>

<style scoped>
.list-editor { list-style: none; }
.list-editor-row {
  display: flex; align-items: flex-start; gap: 6px;
  padding: 5px 0;
  border-bottom: 1px solid var(--border);
}
.list-editor-row:last-child { border-bottom: none; }
.bullet-dot { color: var(--accent); flex-shrink: 0; padding-top: 2px; }
.list-editor-text {
  flex: 1; cursor: text; line-height: 1.5;
  color: var(--text);
  padding: 1px 4px;
  border-radius: var(--radius-sm);
}
.list-editor-text:hover { background: var(--surface2); }
.list-editor-input {
  flex: 1; min-height: 48px; font-size: 13px; padding: 4px 6px;
}
.list-editor-del { padding: 2px 6px; color: var(--text-muted); flex-shrink: 0; }
.list-editor-del:hover { color: var(--red); }
</style>
