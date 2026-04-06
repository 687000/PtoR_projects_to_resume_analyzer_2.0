<template>
  <div class="collapsible-panel">
    <div class="collapsible-header" @click="upload.open = !upload.open">
      <span style="font-weight:600;">{{ upload.open ? '− Add New Job Target' : '+ Add New Job Target' }}</span>
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
          <label>Paste job description</label>
          <textarea v-model="upload.text" rows="8" placeholder="Paste the full job description here…" />
        </div>
        <div v-else-if="upload.activeTab === 'files'" class="form-group">
          <label>Upload files (.pdf, .txt, .jpg, .png) — multiple allowed</label>
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
          <input ref="fileInput" type="file" multiple style="display:none" accept=".pdf,.txt,.jpg,.jpeg,.png" @change="onFileChange" />
        </div>
        <div v-else-if="upload.activeTab === 'url'" class="form-group">
          <label>Job posting URL</label>
          <input v-model="upload.url" placeholder="https://…" />
        </div>

        <div v-if="upload.analyzeError" class="error-msg mt-8">{{ upload.analyzeError }}</div>

        <div class="flex-center gap-8 mt-16">
          <button class="btn-primary" :disabled="upload.analyzing || !hasInput" @click="analyze">
            <span v-if="upload.analyzing"><span class="spinner" style="width:12px;height:12px;margin-right:6px;" /></span>
            {{ upload.analyzing ? 'Extracting…' : 'Extract & Match' }}
          </button>
          <button class="btn-secondary" @click="store.resetUpload">Cancel</button>
        </div>
      </template>

      <!-- Step 2: Review -->
      <template v-else>
        <!-- Deduplication prompt -->
        <div v-if="upload.result.duplicate_check?.is_duplicate" class="dup-banner mb-16">
          <span>⚠️ Similar to <strong>{{ upload.result.duplicate_check.similar_title }}</strong></span>
          <div class="flex-center gap-8 mt-8">
            <button class="btn-secondary" @click="saveAs('update')">Update existing</button>
            <button class="btn-primary" @click="saveAs('new')">Save as new</button>
            <button class="btn-ghost" @click="upload.result = null">Cancel</button>
          </div>
        </div>

        <!-- JD Summary -->
        <div class="jd-summary card mb-16">
          <div style="font-size:15px; font-weight:700; margin-bottom:4px;">{{ upload.result.jd.title }}</div>
          <div class="text-muted text-small">{{ upload.result.jd.company || 'Unknown company' }}</div>
          <div class="tags mt-8">
            <span v-for="t in techTags" :key="t" class="chip">{{ t }}</span>
          </div>
        </div>

        <div v-if="!upload.result.duplicate_check?.is_duplicate" class="flex-center gap-8">
          <button class="btn-primary" :disabled="upload.savingAndMatching" @click="saveAs('new')">
            <span v-if="upload.savingAndMatching"><span class="spinner" style="width:12px;height:12px;margin-right:6px;" /></span>
            {{ upload.savingAndMatching ? 'Matching & saving…' : 'Save to Resume Targets' }}
          </button>
          <button class="btn-secondary" @click="upload.result = null">← Back</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useToast } from '../composables/toast'

const store = useResumeStore()
const toast = useToast()
const upload = store.upload
const fileInput = ref(null)

const inputTabs = ['text', 'files', 'url']

const hasInput = computed(() => {
  const u = upload
  if (u.activeTab === 'text') return u.text.trim().length > 0
  if (u.activeTab === 'files') return u.files.length > 0
  if (u.activeTab === 'url') return u.url.trim().length > 0
  return false
})

const techTags = computed(() => {
  const req = upload.result?.jd?.extracted_requirements || {}
  return [...(req.tech_stack || []), ...(req.domain || [])].slice(0, 8)
})

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
  await store.analyzeJd()
}

async function saveAs(mode) {
  try {
    const saved = await store.saveJd()
    if (saved) toast.success('Job target saved with matches!')
  } catch (e) {
    toast.error(e.message)
  }
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed var(--border); border-radius: var(--radius-sm);
  padding: 16px 20px; text-align: center; cursor: pointer; transition: border-color 0.15s;
}
.drop-zone:hover { border-color: var(--accent); }
.file-list { text-align: left; }
.file-item { display: flex; align-items: center; gap: 6px; padding: 4px 0; font-size: 13px; }
.file-name { font-weight: 600; }
.remove-file {
  margin-left: auto; background: none; border: none;
  color: var(--text-muted); cursor: pointer; font-size: 16px; line-height: 1; padding: 0 4px;
}
.remove-file:hover { color: var(--red); }
.error-msg { color: var(--red); font-size: 12px; }
.dup-banner {
  background: rgba(250,204,21,0.08);
  border: 1px solid rgba(250,204,21,0.3);
  border-radius: var(--radius-sm); padding: 12px;
}
.tags { display: flex; flex-wrap: wrap; gap: 4px; }
</style>
