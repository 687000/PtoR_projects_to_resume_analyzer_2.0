<template>
  <div v-if="modal.open" class="modal-overlay" @click.self="store.closeModal">
    <div class="modal">
      <div class="modal-header">
        <div>
          <div style="font-weight:700; font-size:15px;">{{ project.title || 'Untitled Project' }}</div>
          <div style="margin-top:4px; display:flex; gap:6px; flex-wrap:wrap;">
            <span class="badge badge-blue">{{ project.category || 'other' }}</span>
            <span v-for="t in project.tags" :key="t" class="chip">{{ t }}</span>
          </div>
        </div>
        <button class="btn-ghost" @click="store.closeModal" style="font-size:18px; padding:4px 8px;">✕</button>
      </div>

      <div class="modal-body">
        <div v-if="!editing">
          <div class="tabs">
            <div v-for="t in tabs" :key="t.id" class="tab" :class="{ active: activeTab === t.id }" @click="activeTab = t.id">
              {{ t.label }}
            </div>
          </div>

          <!-- Source & Context -->
          <div v-if="activeTab === 'source'">
            <div class="section-title">Extracted source text</div>
            <pre class="source-text">{{ project.source?.raw_text || 'No source text.' }}</pre>
            <hr />
            <div class="section-title">Background</div>
            <div v-for="(v, k) in project.context?.background" :key="k" class="ctx-field">
              <span class="ctx-label">{{ labelMap[k] || k }}</span>
              <span class="ctx-val">{{ v || '—' }}</span>
            </div>
            <div class="section-title mt-16">Contributions</div>
            <div v-for="(v, k) in project.context?.contributions" :key="k" class="ctx-field">
              <span class="ctx-label">{{ labelMap[k] || k }}</span>
              <span class="ctx-val">{{ v || '—' }}</span>
            </div>
          </div>

          <!-- Summary -->
          <div v-if="activeTab === 'summary'">
            <div class="section-title">Summary</div>
            <p>{{ analysis.summary || '—' }}</p>
            <hr />
            <div class="section-title">Ownership</div>
            <p>{{ analysis.ownership_description || '—' }}</p>
            <hr />
            <div class="section-title">Self-introduction</div>
            <p>{{ analysis.self_introduction || '—' }}</p>
          </div>

          <!-- Highlights -->
          <div v-if="activeTab === 'highlights'">
            <div class="section-title">Technical Highlights</div>
            <ul class="bullet-list">
              <li v-for="(h, i) in analysis.technical_highlights" :key="i">
                <span class="bullet-dot">→</span> {{ h }}
              </li>
            </ul>
            <div v-if="analysis.technical_learning_arc" class="mt-16">
              <div class="section-title">Technical Learning Arc</div>
              <div class="arc-grid">
                <div v-for="key in ['primary_challenge','approach_and_why','key_learning_insight','transfer_value']" :key="key">
                  <div class="arc-label">{{ arcLabels[key] }}</div>
                  <p class="text-small">{{ analysis.technical_learning_arc[key] || '—' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Resume Bullets -->
          <div v-if="activeTab === 'bullets'">
            <div class="section-title">Summary Bullet</div>
            <div class="summary-bullet mb-16">{{ analysis.summary_bullet || '—' }}</div>
            <div class="section-title">Resume Bullets</div>
            <ListEditor v-model="editableBullets" @update:modelValue="onBulletsChange" />
          </div>

          <!-- Interview -->
          <div v-if="activeTab === 'interview'">
            <div v-if="analysis.interview_answer_star" class="mb-16">
              <div class="section-title">STAR Interview Answer</div>
              <div v-for="key in ['situation','task','action','result']" :key="key" class="star-item">
                <span class="star-key">{{ key[0].toUpperCase() }}</span>
                <p>{{ analysis.interview_answer_star[key] || '—' }}</p>
              </div>
            </div>
            <div class="section-title mt-16">Talking Points</div>
            <ul class="bullet-list">
              <li v-for="(tp, i) in analysis.talking_points" :key="i">
                <span class="bullet-dot">•</span> {{ tp }}
              </li>
            </ul>
            <div v-if="analysis.anticipated_interview_questions?.length" class="mt-16">
              <div class="section-title">Anticipated Interview Questions</div>
              <div v-for="(q, i) in analysis.anticipated_interview_questions" :key="i" class="card mb-8">
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

        <!-- Edit Context mode -->
        <div v-else>
          <ContextForm v-model="editContext" />
        </div>
      </div>

      <div class="modal-footer">
        <template v-if="!editing">
          <button class="btn-danger" style="margin-right:auto;" @click="confirmDelete">Delete</button>
          <button class="btn-secondary" @click="startEdit">Edit Context</button>
          <button class="btn-secondary" @click="store.closeModal">Close</button>
        </template>
        <template v-else>
          <button class="btn-secondary" @click="cancelEdit">Cancel</button>
          <button class="btn-primary" :disabled="reanalyzing" @click="saveEdit">
            <span v-if="reanalyzing"><span class="spinner" style="width:12px;height:12px;margin-right:6px;" /></span>
            {{ reanalyzing ? 'Re-analyzing…' : 'Save with Re-analysis' }}
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useProjectStore } from '../stores/projects'
import { useToast } from '../composables/toast'
import { projectsApi } from '../api/client'
import ListEditor from './ListEditor.vue'
import ContextForm from './ContextForm.vue'

const store = useProjectStore()
const toast = useToast()
const modal = store.modal
const project = computed(() => modal.project || {})
const analysis = computed(() => project.value.analysis || {})

const tabs = [
  { id: 'source', label: 'Source & Context' },
  { id: 'summary', label: 'Summary' },
  { id: 'highlights', label: 'Highlights' },
  { id: 'bullets', label: 'Resume Bullets' },
  { id: 'interview', label: 'Interview' },
]
const activeTab = ref('summary')
const editing = ref(false)
const reanalyzing = ref(false)
const editContext = ref({})
const editableBullets = ref([])

watch(project, (p) => {
  editableBullets.value = [...(p.analysis?.resume_bullets || [])]
  editContext.value = JSON.parse(JSON.stringify(p.context || {}))
}, { immediate: true })

const labelMap = {
  business_background: 'Business background',
  team_client_requirements: 'Team / client requirements',
  pm_product_decisions: 'PM product decisions',
  t1_responsibilities: 'T1 responsibilities',
  t2_responsibilities: 'T2 responsibilities',
  architecture_details: 'Architecture details',
  cross_functional_coordination: 'Cross-functional coordination',
  challenges_constraints_tradeoffs: 'Challenges & tradeoffs',
  outcomes_impact: 'Outcomes & impact',
}
const arcLabels = {
  primary_challenge: 'Primary Challenge',
  approach_and_why: 'Approach & Why',
  key_learning_insight: 'Key Insight',
  transfer_value: 'Transfer Value',
}

async function onBulletsChange(bullets) {
  try {
    const updated = await store.updateBullets(project.value.id, bullets)
    modal.project = updated
    toast.success('Saved')
  } catch (e) {
    toast.error(e.message)
  }
}

function startEdit() {
  editing.value = true
  editContext.value = JSON.parse(JSON.stringify(project.value.context || {}))
}

function cancelEdit() {
  editing.value = false
}

async function saveEdit() {
  reanalyzing.value = true
  try {
    const updated = await projectsApi.update(project.value.id, {
      context: editContext.value,
      reanalyze: true,
    })
    const idx = store.list.findIndex(p => p.id === project.value.id)
    if (idx !== -1) store.list[idx] = updated
    modal.project = updated
    editing.value = false
    toast.success('Re-analyzed and saved')
  } catch (e) {
    toast.error(e.message)
  } finally {
    reanalyzing.value = false
  }
}

async function confirmDelete() {
  if (!confirm(`Delete "${project.value.title}"?`)) return
  try {
    await store.deleteProject(project.value.id)
    store.closeModal()
    toast.success('Deleted')
  } catch (e) {
    toast.error(e.message)
  }
}
</script>

<style scoped>
.source-text {
  font-size: 12px; white-space: pre-wrap; color: var(--text-muted);
  background: var(--surface2); padding: 12px; border-radius: var(--radius-sm);
  max-height: 200px; overflow-y: auto;
}
.ctx-field { display: flex; gap: 12px; margin-bottom: 8px; }
.ctx-label { font-size: 12px; color: var(--text-muted); width: 160px; flex-shrink: 0; }
.ctx-val { font-size: 13px; }
.summary-bullet {
  background: var(--surface2); border-radius: var(--radius-sm);
  padding: 10px 12px; font-style: italic; color: var(--text);
}
.star-item { display: flex; gap: 12px; margin-bottom: 10px; align-items: flex-start; }
.star-key {
  background: var(--accent); color: #fff;
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.arc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.arc-label { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
</style>
