import { defineStore } from 'pinia'
import { ref } from 'vue'
import { jdApi } from '../api/client'

export const useResumeStore = defineStore('resume', () => {
  const list = ref([])
  const loading = ref(false)
  const error = ref(null)

  const upload = ref({
    open: false,
    activeTab: 'text',
    text: '',
    url: '',
    files: [],
    analyzing: false,
    analyzeError: null,
    result: null,       // { jd, duplicate_check }
    savingAndMatching: false,
  })

  const detail = ref({
    open: false,
    jd: null,
  })

  const exportModal = ref({
    open: false,
    jd: null,
  })

  async function fetchJdTargets() {
    loading.value = true
    error.value = null
    try {
      list.value = await jdApi.list()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function analyzeJd() {
    const u = upload.value
    u.analyzing = true
    u.analyzeError = null
    u.result = null
    try {
      let res
      if (u.activeTab === 'files' && u.files.length > 0) {
        res = await jdApi.analyzeFile(u.files)
      } else if (u.activeTab === 'url') {
        res = await jdApi.analyzeUrl(u.url)
      } else {
        res = await jdApi.analyzeText(u.text)
      }
      u.result = res
    } catch (e) {
      u.analyzeError = e.message
    } finally {
      u.analyzing = false
    }
  }

  async function saveJd() {
    const u = upload.value
    if (!u.result?.jd) return
    u.savingAndMatching = true
    try {
      const saved = await jdApi.save(u.result.jd, true)
      list.value.unshift(saved)
      resetUpload()
      upload.value.open = true
      return saved
    } finally {
      u.savingAndMatching = false
    }
  }

  async function rematch(jdId) {
    const updated = await jdApi.rematch(jdId)
    const idx = list.value.findIndex(j => j.id === jdId)
    if (idx !== -1) list.value[idx] = updated
    if (detail.value.jd?.id === jdId) detail.value.jd = updated
    return updated
  }

  async function rewriteBullets(jdId, bullets) {
    return jdApi.rewriteBullets(jdId, bullets)
  }

  async function updateJdBullets(jdId, matchResults) {
    const updated = await jdApi.update(jdId, { match_results: matchResults })
    const idx = list.value.findIndex(j => j.id === jdId)
    if (idx !== -1) list.value[idx] = updated
    if (detail.value.jd?.id === jdId) detail.value.jd = updated
    return updated
  }

  async function deleteJd(jdId) {
    await jdApi.delete(jdId)
    list.value = list.value.filter(j => j.id !== jdId)
    if (detail.value.jd?.id === jdId) { detail.value.open = false; detail.value.jd = null }
  }

  function openDetail(jd) {
    detail.value.open = true
    detail.value.jd = jd
  }

  function closeDetail() {
    detail.value.open = false
    detail.value.jd = null
  }

  function openExport(jd) {
    exportModal.value.open = true
    exportModal.value.jd = jd
  }

  function closeExport() {
    exportModal.value.open = false
    exportModal.value.jd = null
  }

  function resetUpload() {
    upload.value = {
      open: false,
      activeTab: 'text',
      text: '',
      url: '',
      files: [],
      analyzing: false,
      analyzeError: null,
      result: null,
      savingAndMatching: false,
    }
  }

  return {
    list, loading, error, upload, detail, exportModal,
    fetchJdTargets, analyzeJd, saveJd, rematch,
    rewriteBullets, updateJdBullets, deleteJd,
    openDetail, closeDetail, openExport, closeExport, resetUpload,
  }
})
