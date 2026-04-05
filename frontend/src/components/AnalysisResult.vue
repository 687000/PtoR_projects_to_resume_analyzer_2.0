<template>
  <div class="result">

    <!-- Source provenance -->
    <div class="source-bar">
      <span class="source-label">Source:</span>
      <span class="source-type">{{ sourceLabel }}</span>
      <button class="source-toggle" @click="showSource = !showSource">
        {{ showSource ? 'Hide extracted text ▴' : 'Preview extracted text ▾' }}
      </button>
    </div>

    <div v-if="showSource" class="source-preview">
      <pre>{{ result.raw_text }}</pre>
    </div>

    <!-- Title + tags -->
    <div class="result-title-row">
      <div>
        <h3>{{ result.title }}</h3>
        <div class="meta">
          <span class="category-badge" :class="result.category">{{ result.category }}</span>
          <span v-for="tag in result.tags" :key="tag" class="tag">{{ tag.replace(/_/g, ' ') }}</span>
        </div>
      </div>
    </div>

    <!-- Output tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >{{ tab.label }}</button>
    </div>

    <div class="tab-body">
      <div v-if="activeTab === 'summary'" class="section">
        <div class="field">
          <label>Summary</label>
          <textarea v-model="result.summary" rows="3" />
        </div>
        <div class="field">
          <label>Ownership</label>
          <textarea v-model="result.ownership_description" rows="4" />
        </div>
        <div class="field">
          <label>Self-Introduction</label>
          <textarea v-model="result.self_intro" rows="2" />
        </div>
      </div>

      <div v-if="activeTab === 'highlights'" class="section">
        <div class="field">
          <label>Technical Highlights</label>
          <ListEditor v-model="result.technical_highlights" />
        </div>
      </div>

      <div v-if="activeTab === 'bullets'" class="section">
        <div v-if="result.summary_bullet" class="field">
          <label>Primary Bullet</label>
          <textarea v-model="result.summary_bullet" rows="2" />
        </div>
        <div class="field">
          <label>Supporting Bullets</label>
          <ListEditor v-model="result.resume_bullets" />
        </div>
      </div>

      <div v-if="activeTab === 'interview'" class="section">
        <div class="field">
          <label>Interview Answer (STAR)</label>
          <textarea v-model="result.interview_answer" rows="8" />
        </div>
        <div class="field">
          <label>Talking Points</label>
          <ListEditor v-model="result.talking_points" />
        </div>
      </div>
    </div>

    <!-- Sticky save bar -->
    <div class="save-bar">
      <span class="save-hint">Review and edit any field above, then save.</span>
      <div class="save-actions">
        <button class="btn-secondary" @click="emit('discard')">Discard</button>
        <button class="btn-save" :disabled="saving" @click="emit('save')">
          <span v-if="saving" class="spinner" />
          {{ saving ? 'Saving…' : '✓ Save to Projects' }}
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ListEditor from './ListEditor.vue'

const props = defineProps({
  result: { type: Object, required: true },
  saving: { type: Boolean, default: false },
})
const emit = defineEmits(['save', 'discard'])

const showSource = ref(false)
const activeTab = ref('summary')

const tabs = [
  { key: 'summary', label: 'Summary' },
  { key: 'highlights', label: 'Highlights' },
  { key: 'bullets', label: 'Resume Bullets' },
  { key: 'interview', label: 'Interview' },
]

const sourceLabel = computed(() => {
  const meta = props.result.source_metadata || {}
  if (meta.filename) return `📄 ${meta.filename}`
  if (meta.url) return `🔗 ${meta.url}`
  return '📝 Plain text'
})
</script>

<style scoped>
.result {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Source preview bar */
.source-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: #f8fafc;
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  flex-wrap: wrap;
}
.source-label { color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; font-size: 10px; }
.source-type { color: var(--text); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 300px; }
.source-toggle {
  background: none;
  border: none;
  font-size: 11px;
  color: var(--primary);
  padding: 0;
  margin-left: auto;
  white-space: nowrap;
}
.source-toggle:hover { text-decoration: underline; }

.source-preview {
  background: #f1f5f9;
  border-bottom: 1px solid var(--border);
  padding: 12px 14px;
  max-height: 200px;
  overflow-y: auto;
}
.source-preview pre {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 11px;
  line-height: 1.6;
  color: var(--text-muted);
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

/* Title row */
.result-title-row {
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--border);
}
h3 { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
.meta { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }

.category-badge {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; padding: 2px 8px; border-radius: 100px;
  background: #dbeafe; color: #1e40af;
}
.category-badge.backend { background: #dcfce7; color: #166534; }
.category-badge.mobile  { background: #f3e8ff; color: #6b21a8; }
.category-badge.data    { background: #fef9c3; color: #854d0e; }
.category-badge.devops  { background: #fee2e2; color: #991b1b; }
.category-badge.platform{ background: #e0e7ff; color: #3730a3; }
.category-badge.other   { background: #f1f5f9; color: #475569; }

/* Tabs */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  padding: 0 16px;
  overflow-x: auto;
}
.tab {
  background: none; border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0; padding: 9px 14px;
  font-size: 13px; color: var(--text-muted);
  margin-bottom: -1px; white-space: nowrap;
}
.tab.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.tab:hover:not(.active) { color: var(--text); }

.tab-body { padding: 16px; flex: 1; }
.section { display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 4px; }

/* Sticky save bar */
.save-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: #f0f7ff;
  border-top: 2px solid var(--primary);
  position: sticky;
  bottom: 0;
}
.save-hint { font-size: 12px; color: var(--text-muted); }
.save-actions { display: flex; gap: 8px; flex-shrink: 0; }

.btn-save {
  background: var(--primary);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-save:hover:not(:disabled) { background: var(--primary-hover); }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
