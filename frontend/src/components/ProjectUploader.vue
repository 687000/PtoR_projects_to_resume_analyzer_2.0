<template>
  <div class="collapsible-panel">
    <div class="collapsible-header" @click="toggle">
      <span style="font-weight:600;">{{ upload.open ? '− Add New Project' : '+ Add New Project' }}</span>
      <span v-if="upload.open && upload.result" class="badge badge-green">Step 2 — Review</span>
    </div>

    <div v-if="upload.open" class="collapsible-body">
      <!-- Step 1: Input -->
      <template v-if="!upload.result">
        <div class="tabs mb-8">
          <div v-for="t in inputTabs" :key="t" class="tab" :class="{ active: upload.activeTab === t }" @click="upload.activeTab = t">
            {{ t.charAt(0).toUpperCase() + t.slice(1) }}
          </div>
        </div>

        <div v-if="upload.activeTab === 'text'" class="form-group">
          <label>Project description or materials</label>
          <textarea v-model="upload.text" rows="6" placeholder="Paste project notes, descriptions, documentation..." />
        </div>

        <div v-else-if="upload.activeTab === 'files'" class="form-group">
          <label>Upload files (.pdf, .txt, .md, .html, .jpg, .png, etc.) — multiple allowed</label>
          <div class="drop-zone" @dragover.prevent @drop.prevent="onDrop" @click="fileInput.click()">
            <div v-if="upload.files.length" class="file-list">
              <div v-for="(f, i) in upload.files" :key="i" class="file-item">
                <span class="file-name">{{ f.name }}</span>
                <span class="text-muted text-small"> ({{ (f.size / 1024).toFixed(0) }} KB)</span>
                <button class="remove-file" @click.stop="removeFile(i)">×</button>
              </div>
            </div>
            <div v-else class="text-muted">Drop files here or click to select</div>
          </div>
          <input ref="fileInput" type="file" multiple style="display:none" accept=".pdf,.txt,.md,.html,.htm,.jpg,.jpeg,.png,.bmp,.tiff,.webp" @change="onFileChange" />
        </div>

        <div v-else-if="upload.activeTab === 'url'" class="form-group">
          <label>URL</label>
          <input v-model="upload.url" placeholder="https://..." />
        </div>

        <div v-else-if="upload.activeTab === 'notion'" class="form-group">
          <label>Notion page URL</label>
          <input v-model="upload.notionUrl" placeholder="https://notion.so/..." />
        </div>

        <div class="mt-16">
          <ContextForm v-model="upload.context" />
        </div>

        <div v-if="upload.analyzeError" class="error-msg mt-8">{{ upload.analyzeError }}</div>

        <div class="flex-center gap-8 mt-16">
          <button class="btn-primary" :disabled="upload.analyzing || !hasInput" @click="analyze">
            <span v-if="upload.analyzing"><span class="spinner" style="width:12px;height:12px;margin-right:6px;" /></span>
            {{ upload.analyzing ? 'Analyzing…' : 'Analyze Project' }}
          </button>
          <button class="btn-secondary" @click="store.resetUpload">Cancel</button>
        </div>
      </template>

      <!-- Step 2: Review -->
      <template v-else>
        <AnalysisResult v-model:result="upload.result" />

        <div class="flex-center gap-8 mt-16">
          <button class="btn-primary" :disabled="saving" @click="save">
            <span v-if="saving"><span class="spinner" style="width:12px;height:12px;margin-right:6px;" /></span>
            {{ saving ? 'Saving…' : '✓ Save to Projects' }}
          </button>
          <button class="btn-secondary" @click="upload.result = null">← Back</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useProjectStore } from '../stores/projects'
import { useToast } from '../composables/toast'
import ContextForm from './ContextForm.vue'
import AnalysisResult from './AnalysisResult.vue'

const store = useProjectStore()
const toast = useToast()
const upload = store.upload
const fileInput = ref(null)
const saving = ref(false)

const inputTabs = ['text', 'files', 'url', 'notion']

const hasInput = computed(() => {
  const u = upload
  if (u.activeTab === 'text') return u.text.trim().length > 0
  if (u.activeTab === 'files') return u.files.length > 0
  if (u.activeTab === 'url') return u.url.trim().length > 0
  if (u.activeTab === 'notion') return u.notionUrl.trim().length > 0
  return false
})

function toggle() {
  upload.open = !upload.open
}

function onDrop(e) {
  const dropped = Array.from(e.dataTransfer.files)
  if (dropped.length) upload.files = [...upload.files, ...dropped]
}

function onFileChange(e) {
  const selected = Array.from(e.target.files)
  if (selected.length) upload.files = [...upload.files, ...selected]
  e.target.value = ''
}

function removeFile(index) {
  upload.files = upload.files.filter((_, i) => i !== index)
}

async function analyze() {
  await store.analyzeProject()
}

async function save() {
  saving.value = true
  try {
    await store.saveProject()
    toast.success('Project saved!')
  } catch (e) {
    toast.error(e.message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius-sm);
  padding: 16px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s;
}
.drop-zone:hover { border-color: var(--accent); }
.file-list { text-align: left; }
.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  font-size: 13px;
}
.file-name { font-weight: 600; }
.remove-file {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0 4px;
}
.remove-file:hover { color: var(--red); }
.error-msg { color: var(--red); font-size: 12px; }
</style>
