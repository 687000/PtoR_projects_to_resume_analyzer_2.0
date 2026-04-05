import { defineStore } from 'pinia'
import * as api from '../api/client'

export const useResumeStore = defineStore('resume', {
  state: () => ({
    targets: [],
    loading: false,
    error: null,

    upload: {
      open: false,
      activeTab: 'text',
      source: '',
      file: null,
      analyzing: false,
      result: null,       // raw analysis result before save
      analyzeError: null,
      duplicate: null,    // existing target with >= 70% overlap, or null
    },

    modal: {
      open: false,
      target: null,       // full JD target being viewed/edited
      rematching: false,
      deleteConfirm: false,
      saving: false,
    },
  }),

  getters: {
    sortedTargets(state) {
      return [...state.targets].sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at)
      )
    },
    // Maps project_id → array of JD target summaries that matched it
    jdTargetsByProject(state) {
      const map = {}
      for (const target of state.targets) {
        for (const mp of (target.matched_projects || [])) {
          if (!map[mp.project_id]) map[mp.project_id] = []
          map[mp.project_id].push({
            id: target.id,
            role_title: target.role_title,
            company: target.company,
            fit_score: mp.fit_score,
            created_at: target.created_at,
          })
        }
      }
      return map
    },
  },

  actions: {
    async fetchAll() {
      this.loading = true
      this.error = null
      try {
        this.targets = await api.getJDTargets()
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
      this.upload.duplicate = null
      try {
        let res
        if (this.upload.activeTab === 'file') {
          if (!this.upload.file) throw new Error('No file selected')
          res = await api.analyzeJDFile(this.upload.file)
        } else {
          if (!this.upload.source.trim()) throw new Error('Input is empty')
          res = await api.analyzeJDSource(this.upload.source.trim())
        }
        this.upload.duplicate = res.duplicate || null
        // Auto-select bullets for recommended matches (fit >= 60), unselect low fits
        if (res.matched_projects) {
          res.matched_projects.forEach(mp => {
            ;(mp.tailored_bullets || []).forEach(b => { b.included = mp.fit_score >= 60 })
          })
        }
        this.upload.result = res
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
        const { raw_jd_text, source_metadata, duplicate, ...analysis } = r
        const saved = await api.saveJDTarget(analysis, raw_jd_text, source_metadata || {})
        this.targets.unshift(saved)
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
      this.upload.file = null
      this.upload.result = null
      this.upload.analyzeError = null
      this.upload.analyzing = false
      this.upload.duplicate = null
    },

    openModal(target) {
      // Deep clone matched_projects so bullet edits don't mutate the list
      this.modal.target = JSON.parse(JSON.stringify(target))
      // Only auto-select when the bullet has no saved included state yet
      if (this.modal.target.matched_projects) {
        this.modal.target.matched_projects.forEach(mp => {
          ;(mp.tailored_bullets || []).forEach(b => {
            if (b.included === undefined) b.included = mp.fit_score >= 60
          })
        })
      }
      this.modal.deleteConfirm = false
      this.modal.rematching = false
      this.modal.saving = false
      this.modal.open = true
    },

    closeModal() {
      this.modal.open = false
      this.modal.target = null
      this.modal.deleteConfirm = false
      this.modal.rematching = false
      this.modal.saving = false
    },

    async rematch(id, projectIds = null) {
      this.modal.rematching = true
      try {
        const updated = await api.rematchJDTarget(id, projectIds)
        // Auto-select bullets for recommended matches (fit >= 60), unselect low fits
        if (updated.matched_projects) {
          updated.matched_projects.forEach(mp => {
            ;(mp.tailored_bullets || []).forEach(b => { b.included = mp.fit_score >= 60 })
          })
        }
        const idx = this.targets.findIndex(t => t.id === id)
        if (idx !== -1) this.targets[idx] = updated
        if (this.modal.target?.id === id) {
          this.modal.target = JSON.parse(JSON.stringify(updated))
        }
      } catch (e) {
        this.error = e.message
      } finally {
        this.modal.rematching = false
      }
    },

    async saveBullets() {
      if (!this.modal.target) return
      this.modal.saving = true
      try {
        const updated = await api.saveJDBullets(
          this.modal.target.id,
          this.modal.target.matched_projects,
        )
        const idx = this.targets.findIndex(t => t.id === updated.id)
        if (idx !== -1) this.targets[idx] = updated
      } catch (e) {
        this.error = e.message
      } finally {
        this.modal.saving = false
      }
    },

    async improveBullets(bullets) {
      const id = this.modal.target?.id
      if (!id || !bullets.length) return null
      return api.improveJDBullets(id, bullets)
    },

    async deleteTarget(id) {
      await api.deleteJDTarget(id)
      this.targets = this.targets.filter(t => t.id !== id)
      if (this.modal.target?.id === id) this.closeModal()
    },
  },
})
