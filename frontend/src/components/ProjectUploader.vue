<template>
  <div class="uploader" :class="{ 'has-result': !!store.upload.result }">

    <!-- Header — changes label based on step -->
    <div class="uploader-header">
      <template v-if="store.upload.result">
        <div class="step-indicator">
          <span class="step done">1 Upload</span>
          <span class="arrow">→</span>
          <span class="step active">2 Review &amp; Save</span>
        </div>
        <button class="btn-ghost back-btn" @click="store.upload.result = null">← Back to edit</button>
      </template>
      <template v-else>
        <button class="toggle-btn" @click="store.upload.open = !store.upload.open">
          <span class="plus" :class="{ rotate: store.upload.open }">+</span>
          Add New Project
        </button>
      </template>
    </div>

    <div v-if="store.upload.open || store.upload.result" class="uploader-body">

      <!-- Step 1: input + context -->
      <template v-if="!store.upload.result">
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab"
            :class="{ active: store.upload.activeTab === tab.key }"
            @click="store.upload.activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <div class="input-area">
          <template v-if="store.upload.activeTab === 'text'">
            <label>Project description</label>
            <textarea
              v-model="store.upload.source"
              rows="5"
              placeholder="Paste or type your project description, notes, or spec…"
            />
          </template>

          <template v-else-if="store.upload.activeTab === 'file'">
            <div
              class="drop-zone"
              :class="{ dragover }"
              @dragover.prevent="dragover = true"
              @dragleave="dragover = false"
              @drop.prevent="onDrop"
              @click="fileInput.click()"
            >
              <template v-if="store.upload.files.length">
                <div v-for="f in store.upload.files" :key="f.name" class="file-pill">📄 {{ f.name }}</div>
              </template>
              <span v-else>Drop files here or <u>click to browse</u><br /><small>PDF, TXT, MD, HTML, PNG, JPG — multiple files allowed</small></span>
            </div>
            <input ref="fileInput" type="file" multiple accept=".pdf,.txt,.md,.html,.htm,.jpg,.jpeg,.png,.bmp,.tiff,.webp" style="display:none" @change="onFileChange" />
          </template>

          <template v-else>
            <label>{{ store.upload.activeTab === 'notion' ? 'Notion page URL' : 'URL' }}</label>
            <input
              type="url"
              v-model="store.upload.source"
              :placeholder="store.upload.activeTab === 'notion'
                ? 'https://www.notion.so/Your-Page-abc123…'
                : 'https://example.com/project-page'"
            />
            <p v-if="store.upload.activeTab === 'notion'" class="hint">Requires NOTION_TOKEN in server .env and page shared with your integration.</p>
          </template>
        </div>

        <ContextForm v-model="store.upload.context" />

        <div class="form-footer">
          <p v-if="store.upload.analyzeError" class="error">{{ store.upload.analyzeError }}</p>
          <div class="form-actions">
            <button class="btn-secondary" @click="store.resetUpload()">Cancel</button>
            <button class="btn-primary" :disabled="store.upload.analyzing" @click="store.analyze()">
              <span v-if="store.upload.analyzing" class="spinner" />
              {{ store.upload.analyzing ? 'Analyzing…' : 'Analyze Project' }}
            </button>
          </div>
        </div>
      </template>

      <!-- Step 2: review result -->
      <template v-else>
        <AnalysisResult
          :result="store.upload.result"
          :saving="store.loading"
          @save="store.saveAnalysis()"
          @discard="store.resetUpload()"
        />
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useProjectStore } from '../stores/projects'
import ContextForm from './ContextForm.vue'
import AnalysisResult from './AnalysisResult.vue'

const store = useProjectStore()
const fileInput = ref(null)
const dragover = ref(false)

const tabs = [
  { key: 'text', label: 'Text' },
  { key: 'file', label: 'File' },
  { key: 'url', label: 'URL' },
  { key: 'notion', label: 'Notion' },
]

function onFileChange(e) {
  store.upload.files = Array.from(e.target.files)
}
function onDrop(e) {
  dragover.value = false
  store.upload.files = Array.from(e.dataTransfer.files)
}
</script>

<style scoped>
.uploader {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 20px;
  transition: border-color 0.2s;
}
.uploader.has-result {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
}

.uploader-header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 46px;
}

/* Step indicator shown in review step */
.step-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
}
.step { color: var(--text-muted); }
.step.done { color: #16a34a; }
.step.active { color: var(--primary); font-weight: 700; }
.arrow { color: var(--text-muted); font-size: 12px; }

.back-btn { font-size: 12px; color: var(--text-muted); }
.back-btn:hover { color: var(--text); }

/* Add new project toggle */
.toggle-btn {
  background: none;
  border: none;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0;
}
.toggle-btn:hover { color: var(--primary-hover); }

.plus {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: var(--primary);
  color: #fff;
  border-radius: 50%;
  font-size: 16px;
  line-height: 1;
  transition: transform 0.2s;
}
.plus.rotate { transform: rotate(45deg); }

.uploader-body {
  border-top: 1px solid var(--border);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0;
}
.tab {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  padding: 6px 12px;
  color: var(--text-muted);
  margin-bottom: -1px;
}
.tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.tab:hover:not(.active) { color: var(--text); }

.input-area { display: flex; flex-direction: column; gap: 6px; }

.drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 28px 20px;
  text-align: center;
  color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  line-height: 1.8;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: var(--primary);
  background: var(--tag-bg);
}
.drop-zone small { font-size: 11px; }
.file-pill { font-size: 13px; color: var(--text); line-height: 1.8; }

.hint { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

.form-footer { display: flex; flex-direction: column; gap: 8px; }
.form-actions { display: flex; justify-content: flex-end; gap: 8px; }
.error { color: var(--danger); font-size: 12px; }
</style>
