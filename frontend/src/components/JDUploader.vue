<template>
  <div class="uploader" :class="{ 'has-result': !!store.upload.result }">

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
          Add New Job Target
        </button>
      </template>
    </div>

    <div v-if="store.upload.open || store.upload.result" class="uploader-body">

      <!-- Step 1: input -->
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
            <label>Job description</label>
            <textarea
              v-model="store.upload.source"
              rows="7"
              placeholder="Paste the job description here…"
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
              <span v-if="store.upload.file">📄 {{ store.upload.file.name }}</span>
              <span v-else>Drop a file here or <u>click to browse</u><br /><small>PDF, TXT, HTML, PNG, JPG</small></span>
            </div>
            <input ref="fileInput" type="file" accept=".pdf,.txt,.html,.htm,.jpg,.jpeg,.png" style="display:none" @change="onFileChange" />
          </template>

          <template v-else>
            <label>Job posting URL</label>
            <input
              type="url"
              v-model="store.upload.source"
              placeholder="https://jobs.example.com/senior-frontend-engineer"
            />
          </template>
        </div>

        <div class="form-footer">
          <p v-if="store.upload.analyzeError" class="error">{{ store.upload.analyzeError }}</p>
          <div class="form-actions">
            <button class="btn-secondary" @click="store.resetUpload()">Cancel</button>
            <button class="btn-primary" :disabled="store.upload.analyzing" @click="store.analyze()">
              <span v-if="store.upload.analyzing" class="spinner" />
              {{ store.upload.analyzing ? 'Analyzing…' : 'Extract & Match' }}
            </button>
          </div>
        </div>
      </template>

      <!-- Step 2: review match results -->
      <template v-else>
        <!-- Deduplication prompt -->
        <div v-if="store.upload.duplicate" class="dup-banner">
          <span class="dup-icon">⚠</span>
          <span class="dup-msg">
            Similar to <strong>{{ store.upload.duplicate.role_title }}</strong>
            saved {{ formatDate(store.upload.duplicate.created_at) }}.
          </span>
          <div class="dup-actions">
            <button class="btn-secondary" @click="rematchExisting">Update existing</button>
            <button class="btn-ghost" @click="store.upload.duplicate = null">Save as new</button>
          </div>
        </div>

        <!-- JD summary -->
        <div class="jd-summary">
          <div class="jd-title-row">
            <h3>{{ store.upload.result.role_title }}</h3>
            <span v-if="store.upload.result.company" class="company">{{ store.upload.result.company }}</span>
          </div>
          <div class="req-chips">
            <span
              v-for="kw in allRequirements"
              :key="kw"
              class="req-chip"
            >{{ kw }}</span>
          </div>
        </div>

        <!-- Matched projects -->
        <div v-if="store.upload.result.matched_projects?.length" class="match-list">
          <div
            v-for="mp in store.upload.result.matched_projects"
            :key="mp.project_id"
            class="match-card"
          >
            <div class="match-header">
              <span class="match-title">{{ mp.project_title }}</span>
              <span class="fit-badge" :class="fitClass(mp.fit_score)">{{ mp.fit_score }}%</span>
            </div>
            <div v-if="mp.addressed_requirements?.length" class="addressed">
              <span v-for="r in mp.addressed_requirements" :key="r" class="tag">{{ r }}</span>
            </div>
            <ul class="bullets">
              <li v-for="(b, i) in mp.tailored_bullets" :key="i">{{ b.text }}</li>
            </ul>
          </div>
        </div>
        <p v-else class="no-match">No saved projects yet — add projects first to see match results.</p>

        <div class="form-footer">
          <p v-if="store.upload.analyzeError" class="error">{{ store.upload.analyzeError }}</p>
          <div class="form-actions">
            <button class="btn-secondary" @click="store.resetUpload()">Discard</button>
            <button class="btn-primary" :disabled="store.loading" @click="store.saveAnalysis()">
              <span v-if="store.loading" class="spinner" />
              {{ store.loading ? 'Saving…' : 'Save to Resume Targets' }}
            </button>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useResumeStore } from '../stores/resume'

const store = useResumeStore()
const fileInput = ref(null)
const dragover = ref(false)

const tabs = [
  { key: 'text', label: 'Text' },
  { key: 'file', label: 'File' },
  { key: 'url',  label: 'URL' },
]

function onFileChange(e) { store.upload.file = e.target.files[0] || null }
function onDrop(e) {
  dragover.value = false
  store.upload.file = e.dataTransfer.files[0] || null
}

const allRequirements = computed(() => {
  const r = store.upload.result?.extracted_requirements
  if (!r) return []
  return [...(r.tech_stack || []), ...(r.domain || []), ...(r.collaboration || []), ...(r.seniority || [])].slice(0, 16)
})

function fitClass(score) {
  if (score >= 80) return 'high'
  if (score >= 60) return 'mid'
  return 'low'
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

async function rematchExisting() {
  const dup = store.upload.duplicate
  if (!dup) return
  await store.rematch(dup.id)
  store.resetUpload()
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
  box-shadow: 0 0 0 3px rgba(124,111,207,0.1);
}

.uploader-header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 46px;
}

.step-indicator {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 500;
}
.step { color: var(--text-muted); }
.step.done { color: #16a34a; }
.step.active { color: var(--primary); font-weight: 700; }
.arrow { color: var(--text-muted); font-size: 12px; }
.back-btn { font-size: 12px; color: var(--text-muted); }
.back-btn:hover { color: var(--text); }

.toggle-btn {
  background: none; border: none;
  font-size: 14px; font-weight: 600;
  color: var(--primary);
  display: flex; align-items: center; gap: 8px; padding: 0;
}
.toggle-btn:hover { color: var(--primary-hover); }

.plus {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px;
  background: var(--primary); color: #fff;
  border-radius: 50%; font-size: 16px; line-height: 1;
  transition: transform 0.2s;
}
.plus.rotate { transform: rotate(45deg); }

.uploader-body {
  border-top: 1px solid var(--border);
  padding: 16px;
  display: flex; flex-direction: column; gap: 14px;
}

.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); }
.tab {
  background: none; border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0; padding: 6px 12px;
  color: var(--text-muted); margin-bottom: -1px;
}
.tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.tab:hover:not(.active) { color: var(--text); }

.input-area { display: flex; flex-direction: column; gap: 6px; }

.drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 28px 20px;
  text-align: center; color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  line-height: 1.8;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: var(--primary); background: var(--tag-bg);
}
.drop-zone small { font-size: 11px; }

/* Deduplication banner */
.dup-banner {
  display: flex; align-items: center; gap: 10px;
  background: #fffbeb; border: 1px solid #fcd34d;
  border-radius: 6px; padding: 10px 14px;
  flex-wrap: wrap;
}
.dup-icon { color: #d97706; font-size: 15px; flex-shrink: 0; }
.dup-msg { font-size: 13px; color: var(--text); flex: 1; min-width: 180px; }
.dup-actions { display: flex; gap: 6px; flex-shrink: 0; }

/* JD summary */
.jd-summary {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.jd-title-row { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.jd-title-row h3 { font-size: 14px; font-weight: 700; }
.company { font-size: 12px; color: var(--text-muted); }

.req-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.req-chip {
  font-size: 11px; font-weight: 500;
  background: var(--tag-bg); color: var(--tag-text);
  padding: 2px 8px; border-radius: 100px;
}

/* Match cards */
.match-list { display: flex; flex-direction: column; gap: 10px; }
.match-card {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 14px;
  display: flex; flex-direction: column; gap: 8px;
  background: var(--surface);
}
.match-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.match-title { font-size: 13px; font-weight: 600; }
.fit-badge {
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 100px;
}
.fit-badge.high { background: #dcfce7; color: #166534; }
.fit-badge.mid  { background: #fef9c3; color: #854d0e; }
.fit-badge.low  { background: #f1f5f9; color: #475569; }

.addressed { display: flex; flex-wrap: wrap; gap: 4px; }

.bullets { padding-left: 16px; display: flex; flex-direction: column; gap: 4px; }
.bullets li { font-size: 12px; line-height: 1.6; color: var(--text); }

.no-match { font-size: 13px; color: var(--text-muted); text-align: center; padding: 16px 0; }

.form-footer { display: flex; flex-direction: column; gap: 8px; }
.form-actions { display: flex; justify-content: flex-end; gap: 8px; }
.error { color: var(--danger); font-size: 12px; }
</style>
