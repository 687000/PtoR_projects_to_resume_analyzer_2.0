import { defineStore } from 'pinia'
import * as api from '../api/client'

const emptyContext = () => ({
  business_background: '',
  team_client_requirements: '',
  pm_decisions: '',
  t1_responsibilities: '',
  t2_responsibilities: '',
  architecture_details: '',
  coordination: '',
  challenges: '',
  outcomes: '',
})

export const useProjectStore = defineStore('projects', {
  state: () => ({
    projects: [],
    loading: false,
    error: null,

    upload: {
      open: false,
      activeTab: 'text',
      source: '',
      files: [],
      context: emptyContext(),
      analyzing: false,
      result: null,
      analyzeError: null,
    },

    modal: {
      open: false,
      project: null,
      editing: false,
      editContext: emptyContext(),
      reanalyzing: false,
      deleteConfirm: false,
    },

    search: {
      query: '',
      category: '',
      tag: '',
    },
  }),

  getters: {
    filteredProjects(state) {
      const q = state.search.query.toLowerCase()
      const cat = state.search.category
      const tag = state.search.tag
      return state.projects.filter(p => {
        if (cat && p.category !== cat) return false
        if (tag && !p.tags?.includes(tag)) return false
        if (q) {
          const haystack = `${p.title} ${p.summary} ${p.tags?.join(' ')}`.toLowerCase()
          if (!haystack.includes(q)) return false
        }
        return true
      })
    },
    allCategories(state) {
      return [...new Set(state.projects.map(p => p.category).filter(Boolean))]
    },
    allTags(state) {
      return [...new Set(state.projects.flatMap(p => p.tags || []))]
    },
  },

  actions: {
    async fetchAll() {
      this.loading = true
      this.error = null
      try {
        this.projects = await api.getProjects()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    async analyze() {
      this.upload.analyzing = true
      this.upload.analyzeError = null
      this.upload.result = null
      try {
        const ctx = this.upload.context
        if (this.upload.activeTab === 'file') {
          if (!this.upload.files.length) throw new Error('No file selected')
          this.upload.result = await api.analyzeFile(this.upload.files, ctx)
        } else {
          if (!this.upload.source.trim()) throw new Error('Input is empty')
          this.upload.result = await api.analyzeSource(this.upload.source.trim(), ctx)
        }
      } catch (e) {
        this.upload.analyzeError = e.message
      } finally {
        this.upload.analyzing = false
      }
    },

    async saveAnalysis() {
      const r = this.upload.result
      if (!r) return
      this.loading = true
      try {
        const { raw_text, source_metadata, ...analysis } = r
        const saved = await api.saveProject(analysis, raw_text, source_metadata || {})
        this.projects.unshift(saved)
        this.resetUpload()
      } catch (e) {
        this.upload.analyzeError = e.message
      } finally {
        this.loading = false
      }
    },

    resetUpload() {
      this.upload.open = false
      this.upload.activeTab = 'text'
      this.upload.source = ''
      this.upload.files = []
      this.upload.context = emptyContext()
      this.upload.result = null
      this.upload.analyzeError = null
      this.upload.analyzing = false
    },

    openModal(project) {
      this.modal.project = { ...project }
      this.modal.editing = false
      this.modal.editContext = { ...(project.context || emptyContext()) }
      this.modal.deleteConfirm = false
      this.modal.open = true
    },

    closeModal() {
      this.modal.open = false
      this.modal.project = null
      this.modal.editing = false
      this.modal.deleteConfirm = false
      this.modal.reanalyzing = false
    },

    async reanalyze() {
      if (!this.modal.project) return
      this.modal.reanalyzing = true
      try {
        const updated = await api.patchProject(
          this.modal.project.id,
          this.modal.editContext,
          true,
        )
        this.modal.project = { ...updated }
        this.modal.editing = false
        const idx = this.projects.findIndex(p => p.id === updated.id)
        if (idx !== -1) this.projects[idx] = updated
      } catch (e) {
        this.error = e.message
      } finally {
        this.modal.reanalyzing = false
      }
    },

    async saveBullets(bullets) {
      if (!this.modal.project) return
      const updated = await api.patchProject(
        this.modal.project.id,
        this.modal.project.context || {},
        false,
        bullets,
      )
      this.modal.project = { ...updated }
      const idx = this.projects.findIndex(p => p.id === updated.id)
      if (idx !== -1) this.projects[idx] = updated
    },

    reorderProjects(sourceId, targetId) {
      const sourceIndex = this.projects.findIndex(p => p.id === sourceId)
      const targetIndex = this.projects.findIndex(p => p.id === targetId)
      if (sourceIndex === -1 || targetIndex === -1 || sourceIndex === targetIndex) return

      const [moved] = this.projects.splice(sourceIndex, 1)
      const insertIndex = sourceIndex < targetIndex ? targetIndex - 1 : targetIndex
      this.projects.splice(insertIndex, 0, moved)
    },

    async deleteProject(id) {
      await api.deleteProject(id)
      this.projects = this.projects.filter(p => p.id !== id)
      if (this.modal.project?.id === id) this.closeModal()
    },
  },
})
