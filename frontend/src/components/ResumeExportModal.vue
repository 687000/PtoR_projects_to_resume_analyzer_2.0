<template>
  <div v-if="exportModal.open" class="modal-overlay" @click.self="store.closeExport">
    <div class="modal export-modal">
      <div class="modal-header">
        <div>
          <div style="font-weight:700; font-size:15px;">Resume Section</div>
          <div class="text-muted text-small">{{ jd.title }} · {{ jd.company || 'Unknown company' }}</div>
        </div>
        <div style="display:flex; gap:8px; align-items:center;">
          <button class="btn-secondary" style="font-size:12px; padding:4px 10px;" @click="showTitles = !showTitles">
            {{ showTitles ? 'Hide Titles' : 'Show Titles' }}
          </button>
          <button class="btn-ghost" @click="store.closeExport" style="font-size:18px; padding:4px 8px;">✕</button>
        </div>
      </div>

      <div class="modal-body">
        <div v-if="!selectedSections.length" class="empty-state" style="padding:30px;">
          <h3>No bullets selected</h3>
          <p>Check bullets in the resume detail view to include them here.</p>
        </div>

        <div v-else>
          <!-- Rewrite result notice -->
          <div v-if="rewriteDone" class="rewrite-notice mb-12">
            AI rewrite applied. Review bullets below and copy when ready.
          </div>

          <div v-for="section in selectedSections" :key="section.project_id" class="export-section mb-12">
            <div v-if="showTitles" class="export-title">{{ section.project_title }}</div>
            <ul class="export-bullets">
              <li v-for="(b, i) in section.bullets" :key="i" class="export-bullet-row">
                <span class="bullet-dot">•</span>
                <span class="bullet-text">{{ b }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button
          class="btn-secondary"
          :disabled="!selectedSections.length || rewriting"
          @click="rewriteWithAI"
        >
          <span v-if="rewriting"><span class="spinner" style="width:11px;height:11px;margin-right:6px;" /></span>
          {{ rewriting ? 'Rewriting…' : 'Rewrite with AI' }}
        </button>
        <button
          class="btn-primary"
          style="margin-left:auto;"
          :disabled="!selectedSections.length"
          @click="copyToClipboard"
        >
          Copy to Clipboard
        </button>
        <button class="btn-secondary" @click="store.closeExport">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useToast } from '../composables/toast'

const store = useResumeStore()
const toast = useToast()
const exportModal = store.exportModal
const jd = computed(() => exportModal.jd || {})
const showTitles = ref(true)
const rewriting = ref(false)
const rewriteDone = ref(false)

// Local overrides: projectId -> [bullet texts] (set after AI rewrite)
const rewrittenBullets = ref({})

// Reset local state when modal opens with a new JD
watch(() => exportModal.open, (open) => {
  if (open) {
    rewrittenBullets.value = {}
    rewriteDone.value = false
  }
})

const selectedSections = computed(() => {
  const projects = jd.value.match_results?.projects || []
  return projects
    .map(mp => {
      const bullets = rewrittenBullets.value[mp.project_id]
        ?? (mp.tailored_bullets || []).filter(b => b.included).map(b => b.bullet)
      return { project_id: mp.project_id, project_title: mp.project_title, bullets }
    })
    .filter(s => s.bullets.length > 0)
})

async function rewriteWithAI() {
  const allBullets = []
  const bulletMap = [] // { project_id, project_title, count }

  for (const section of selectedSections.value) {
    bulletMap.push({ project_id: section.project_id, project_title: section.project_title, count: section.bullets.length })
    allBullets.push(...section.bullets)
  }

  if (!allBullets.length) return
  rewriting.value = true
  rewriteDone.value = false

  try {
    const result = await store.rewriteBullets(jd.value.id, allBullets)
    const rewritten = (result.rewritten_bullets || []).map(r => r.rewritten || r.original)

    let idx = 0
    const newMap = {}
    for (const { project_id, count } of bulletMap) {
      newMap[project_id] = rewritten.slice(idx, idx + count)
      idx += count
    }
    rewrittenBullets.value = newMap
    rewriteDone.value = true
  } catch (e) {
    toast.error(e.message)
  } finally {
    rewriting.value = false
  }
}

function copyToClipboard() {
  const lines = []
  for (const section of selectedSections.value) {
    if (showTitles.value) lines.push(section.project_title)
    for (const b of section.bullets) {
      lines.push(`• ${b}`)
    }
    lines.push('')
  }
  navigator.clipboard.writeText(lines.join('\n').trimEnd()).then(
    () => toast.success('Copied to clipboard!'),
    () => toast.error('Failed to copy'),
  )
}
</script>

<style scoped>
.export-modal { max-width: 700px; }
.export-section { border-bottom: 1px solid var(--border); padding-bottom: 12px; }
.export-section:last-child { border-bottom: none; }
.export-title { font-weight: 700; font-size: 14px; margin-bottom: 6px; color: var(--text); }
.export-bullets { list-style: none; padding: 0; margin: 0; }
.export-bullet-row { display: flex; gap: 8px; padding: 4px 0; align-items: flex-start; }
.bullet-dot { color: var(--accent); flex-shrink: 0; margin-top: 1px; }
.bullet-text { font-size: 13px; line-height: 1.6; color: var(--text); }
.rewrite-notice {
  background: rgba(67,97,238,0.08);
  border: 1px solid rgba(67,97,238,0.2);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  font-size: 12px;
  color: var(--accent);
}
</style>
