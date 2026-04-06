<template>
  <div class="analysis-result">
    <div class="flex-between mb-16">
      <div>
        <input v-model="localTitle" class="title-input" placeholder="Project title" />
        <div style="margin-top:6px; display:flex; gap:6px; flex-wrap:wrap;">
          <span class="badge badge-blue">{{ result.category || 'other' }}</span>
          <span v-for="t in result.tags" :key="t" class="chip">{{ t }}</span>
        </div>
      </div>
      <div class="flex-center gap-8">
        <button class="btn-secondary" @click="showSource = !showSource">
          {{ showSource ? 'Hide' : 'Preview' }} source
        </button>
        <slot name="actions" />
      </div>
    </div>

    <div v-if="showSource" class="source-preview mb-16">
      <div class="section-title">Extracted source text</div>
      <pre class="source-text">{{ result.source?.raw_text || '' }}</pre>
    </div>

    <div class="tabs">
      <div v-for="t in tabs" :key="t.id" class="tab" :class="{ active: activeTab === t.id }" @click="activeTab = t.id">
        {{ t.label }}
      </div>
    </div>

    <!-- Summary tab -->
    <div v-if="activeTab === 'summary'">
      <div class="form-group">
        <label>Summary</label>
        <textarea v-model="analysis.summary" rows="3" />
      </div>
      <div class="form-group">
        <label>Ownership description</label>
        <textarea v-model="analysis.ownership_description" rows="2" />
      </div>
      <div class="form-group">
        <label>Self-introduction</label>
        <textarea v-model="analysis.self_introduction" rows="2" />
      </div>
    </div>

    <!-- Highlights tab -->
    <div v-if="activeTab === 'highlights'">
      <div class="section-title">Technical Highlights</div>
      <ListEditor v-model="analysis.technical_highlights" />
    </div>

    <!-- Resume Bullets tab -->
    <div v-if="activeTab === 'bullets'">
      <div class="section-title">Summary Bullet</div>
      <textarea v-model="analysis.summary_bullet" rows="2" class="mb-16" />
      <div class="section-title">Resume Bullets</div>
      <ListEditor v-model="analysis.resume_bullets" />
    </div>

    <!-- Interview tab -->
    <div v-if="activeTab === 'interview'">
      <div class="section-title">STAR Interview Answer</div>
      <div v-if="analysis.interview_answer_star" class="star-grid">
        <div v-for="key in ['situation','task','action','result']" :key="key" class="form-group">
          <label>{{ key.charAt(0).toUpperCase() + key.slice(1) }}</label>
          <textarea v-model="analysis.interview_answer_star[key]" rows="2" />
        </div>
      </div>
      <div class="section-title mt-16">Talking Points</div>
      <ListEditor v-model="analysis.talking_points" />
      <div v-if="analysis.anticipated_interview_questions?.length" class="mt-16">
        <div class="section-title">Anticipated Interview Questions</div>
        <div v-for="(q, i) in analysis.anticipated_interview_questions" :key="i" class="iq-card card mb-8">
          <div style="font-weight:600; margin-bottom:4px;">{{ q.question }}</div>
          <div class="text-muted text-small mb-8">{{ q.intent }}</div>
          <ul class="bullet-list">
            <li v-for="(f, j) in q.suggested_answer_frames" :key="j">
              <span class="bullet-dot">→</span> {{ f }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import ListEditor from './ListEditor.vue'

const props = defineProps({
  result: { type: Object, required: true },
})
const emit = defineEmits(['update:result'])

const tabs = [
  { id: 'summary', label: 'Summary' },
  { id: 'highlights', label: 'Highlights' },
  { id: 'bullets', label: 'Resume Bullets' },
  { id: 'interview', label: 'Interview' },
]
const activeTab = ref('summary')
const showSource = ref(false)
const localTitle = ref(props.result.title || '')
const analysis = reactive({ ...props.result.analysis })

watch([localTitle, analysis], () => {
  emit('update:result', { ...props.result, title: localTitle.value, analysis: { ...analysis } })
}, { deep: true })

watch(() => props.result, (r) => {
  localTitle.value = r.title || ''
  Object.assign(analysis, r.analysis)
}, { deep: true })
</script>

<style scoped>
.title-input {
  font-size: 16px; font-weight: 700; background: transparent;
  border: none; border-bottom: 1px solid var(--border);
  border-radius: 0; padding: 4px 2px; width: 100%; max-width: 400px;
}
.title-input:focus { border-bottom-color: var(--accent); outline: none; }
.source-preview { background: var(--surface2); border-radius: var(--radius-sm); padding: 12px; }
.source-text { font-size: 12px; white-space: pre-wrap; color: var(--text-muted); max-height: 200px; overflow-y: auto; }
.star-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.iq-card { margin-bottom: 8px; }
@media (max-width: 600px) { .star-grid { grid-template-columns: 1fr; } }
</style>
