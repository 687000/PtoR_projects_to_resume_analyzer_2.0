import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectsApi } from '../api/client'

export const useProjectStore = defineStore('projects', () => {
  const list = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Upload panel state
  const upload = ref({
    open: false,
    activeTab: 'text',
    text: '',
    url: '',
    notionUrl: '',
    files: [],
    context: defaultContext(),
    analyzing: false,
    analyzeError: null,
    result: null,      // { source, title, category, tags, analysis }
    sourcePreview: '',
  })

  // Modal state
  const modal = ref({
    open: false,
    project: null,
  })

  function defaultContext() {
    return {
      background: {
        business_background: '',
        team_client_requirements: '',
        pm_product_decisions: '',
      },
      contributions: {
        t1_responsibilities: '',
        t2_responsibilities: '',
        architecture_details: '',
        cross_functional_coordination: '',
        challenges_constraints_tradeoffs: '',
        outcomes_impact: '',
      },
    }
  }

  async function fetchProjects() {
    loading.value = true
    error.value = null
    try {
      list.value = await projectsApi.list()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function analyzeProject() {
    const u = upload.value
    u.analyzing = true
    u.analyzeError = null
    u.result = null
    try {
      let res
      if (u.activeTab === 'files' && u.files.length > 0) {
        res = await projectsApi.analyzeFile(u.files, u.context)
      } else if (u.activeTab === 'url') {
        res = await projectsApi.analyzeText('', u.url, '', u.context)
      } else if (u.activeTab === 'notion') {
        res = await projectsApi.analyzeText('', '', u.notionUrl, u.context)
      } else {
        res = await projectsApi.analyzeText(u.text, '', '', u.context)
      }
      u.result = res
      u.sourcePreview = res.source?.raw_text || ''
    } catch (e) {
      u.analyzeError = e.message
    } finally {
      u.analyzing = false
    }
  }

  async function saveProject() {
    const u = upload.value
    if (!u.result) return
    const saved = await projectsApi.save(u.result.source, u.context, u.result)
    list.value.unshift(saved)
    resetUpload()
    return saved
  }

  function resetUpload() {
    const u = upload.value
    u.open = false
    u.activeTab = 'text'
    u.text = ''
    u.url = ''
    u.notionUrl = ''
    u.files = []
    u.context = defaultContext()
    u.analyzing = false
    u.analyzeError = null
    u.result = null
    u.sourcePreview = ''
  }

  async function updateBullets(projectId, bullets) {
    const updated = await projectsApi.update(projectId, {
      resume_bullets: bullets,
      reanalyze: false,
    })
    const idx = list.value.findIndex(p => p.id === projectId)
    if (idx !== -1) list.value[idx] = updated
    return updated
  }

  async function deleteProject(projectId) {
    await projectsApi.delete(projectId)
    list.value = list.value.filter(p => p.id !== projectId)
  }

  function openModal(project) {
    modal.value.open = true
    modal.value.project = project
  }

  function closeModal() {
    modal.value.open = false
    modal.value.project = null
  }

  return {
    list, loading, error, upload, modal,
    fetchProjects, analyzeProject, saveProject, resetUpload,
    updateBullets, deleteProject, openModal, closeModal,
    defaultContext,
  }
})
