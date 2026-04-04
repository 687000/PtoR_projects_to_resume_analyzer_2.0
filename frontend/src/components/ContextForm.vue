<template>
  <div class="context-form">
    <section>
      <button type="button" class="section-toggle" @click="bgOpen = !bgOpen">
        <span>Background <em>(not your work)</em></span>
        <span class="chevron" :class="{ open: bgOpen }">▸</span>
      </button>
      <div v-show="bgOpen" class="section-body">
        <div class="field">
          <label>Business / project background</label>
          <textarea v-model="local.business_background" rows="2" placeholder="What is this project about? Who is the client or team?" />
        </div>
        <div class="field">
          <label>Team / client requirements</label>
          <textarea v-model="local.team_client_requirements" rows="2" placeholder="What did the team or client ask for?" />
        </div>
        <div class="field">
          <label>PM product decisions</label>
          <textarea v-model="local.pm_decisions" rows="2" placeholder="Key product decisions made by PMs (not you)" />
        </div>
      </div>
    </section>

    <section>
      <button type="button" class="section-toggle" @click="contribOpen = !contribOpen">
        <span>Your Contributions</span>
        <span class="chevron" :class="{ open: contribOpen }">▸</span>
      </button>
      <div v-show="contribOpen" class="section-body">
        <div class="field">
          <label>T1 — scope analysis, API/interface design</label>
          <textarea v-model="local.t1_responsibilities" rows="2" placeholder="Technical analysis, platform assessment, interface definitions you drove" />
        </div>
        <div class="field">
          <label>T2 — implementation, web development</label>
          <textarea v-model="local.t2_responsibilities" rows="2" placeholder="Hands-on coding, feature delivery, detailed design" />
        </div>
        <div class="field">
          <label>Architecture details</label>
          <textarea v-model="local.architecture_details" rows="2" placeholder="Models, controllers, stores, views, APIs you defined" />
        </div>
        <div class="field">
          <label>Cross-platform / cross-functional coordination</label>
          <textarea v-model="local.coordination" rows="2" placeholder="Web / mobile / server coordination, stakeholder communication" />
        </div>
        <div class="field">
          <label>Challenges, constraints, tradeoffs</label>
          <textarea v-model="local.challenges" rows="2" placeholder="What was hard? What tradeoffs did you navigate?" />
        </div>
        <div class="field">
          <label>Outcomes and impact</label>
          <textarea v-model="local.outcomes" rows="2" placeholder="What shipped? Metrics, user impact, delivery results" />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({ modelValue: { type: Object, required: true } })
const emit = defineEmits(['update:modelValue'])

const bgOpen = defineModel('bgOpen', { default: false })
const contribOpen = defineModel('contribOpen', { default: true })

const local = reactive({ ...props.modelValue })

watch(local, val => emit('update:modelValue', { ...val }))
watch(() => props.modelValue, val => Object.assign(local, val), { deep: true })
</script>

<style scoped>
.context-form { display: flex; flex-direction: column; gap: 4px; }

.section-toggle {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  text-align: left;
}
.section-toggle em { font-style: normal; color: var(--text-muted); font-weight: 400; }
.section-toggle:hover { background: #e8eef5; }

.chevron { transition: transform 0.2s; display: inline-block; }
.chevron.open { transform: rotate(90deg); }

.section-body { display: flex; flex-direction: column; gap: 10px; padding: 12px 4px 8px; }
.field { display: flex; flex-direction: column; gap: 4px; }
</style>
