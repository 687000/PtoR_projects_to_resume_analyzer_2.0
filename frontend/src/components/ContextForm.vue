<template>
  <div class="context-form">
    <details class="accordion" :open="bgOpen">
      <summary @click.prevent="bgOpen = !bgOpen" class="accordion-header">
        <span>Background <span class="text-muted text-small">(not your work)</span></span>
        <span class="chevron">{{ bgOpen ? '▲' : '▼' }}</span>
      </summary>
      <div class="accordion-body">
        <div class="form-group">
          <label>Business / project background</label>
          <textarea v-model="ctx.background.business_background" placeholder="What is this project about? Business context..." />
        </div>
        <div class="form-group">
          <label>Team / client requirements</label>
          <textarea v-model="ctx.background.team_client_requirements" placeholder="What did the team or client need?" />
        </div>
        <div class="form-group">
          <label>PM product decisions</label>
          <textarea v-model="ctx.background.pm_product_decisions" placeholder="Key decisions from product management..." />
        </div>
      </div>
    </details>

    <details class="accordion" :open="contribOpen">
      <summary @click.prevent="contribOpen = !contribOpen" class="accordion-header">
        <span>Your Contributions</span>
        <span class="chevron">{{ contribOpen ? '▲' : '▼' }}</span>
      </summary>
      <div class="accordion-body">
        <div class="form-group">
          <label>T1 — Scope analysis, API/interface design</label>
          <textarea v-model="ctx.contributions.t1_responsibilities" placeholder="Architecture planning, interface design, scope analysis..." />
        </div>
        <div class="form-group">
          <label>T2 — Implementation, web development</label>
          <textarea v-model="ctx.contributions.t2_responsibilities" placeholder="What you actually built, coded, or shipped..." />
        </div>
        <div class="form-group">
          <label>Architecture details</label>
          <textarea v-model="ctx.contributions.architecture_details" placeholder="Architectural decisions you made or drove..." />
        </div>
        <div class="form-group">
          <label>Cross-platform / cross-functional coordination</label>
          <textarea v-model="ctx.contributions.cross_functional_coordination" placeholder="Coordination with mobile, backend, design, PM..." />
        </div>
        <div class="form-group">
          <label>Challenges, constraints, tradeoffs</label>
          <textarea v-model="ctx.contributions.challenges_constraints_tradeoffs" placeholder="Technical challenges you navigated..." />
        </div>
        <div class="form-group">
          <label>Outcomes and impact</label>
          <textarea v-model="ctx.contributions.outcomes_impact" placeholder="What improved as a result of your work?" />
        </div>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({ modelValue: { type: Object, required: true } })
const emit = defineEmits(['update:modelValue'])

const ctx = ref(props.modelValue)
const bgOpen = ref(false)
const contribOpen = ref(true)

watch(() => props.modelValue, (v) => { ctx.value = v }, { deep: true })
watch(ctx, (v) => emit('update:modelValue', v), { deep: true })
</script>

<style scoped>
.accordion { border: 1px solid var(--border); border-radius: var(--radius-sm); margin-bottom: 8px; }
.accordion-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  list-style: none;
  font-weight: 600; font-size: 13px;
  user-select: none;
}
.accordion-header::-webkit-details-marker { display: none; }
.accordion-body { padding: 0 12px 12px; }
.chevron { font-size: 10px; color: var(--text-muted); }
</style>
