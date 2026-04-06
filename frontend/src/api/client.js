const BASE = '/api'

async function request(method, path, body, isFormData = false) {
  const opts = { method, headers: {} }
  if (body && !isFormData) {
    opts.headers['Content-Type'] = 'application/json'
    opts.body = JSON.stringify(body)
  } else if (body && isFormData) {
    opts.body = body
  }
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

const get = (path) => request('GET', path)
const post = (path, body) => request('POST', path, body)
const patch = (path, body) => request('PATCH', path, body)
const del = (path) => request('DELETE', path)

export const projectsApi = {
  list: () => get('/projects'),
  get: (id) => get(`/projects/${id}`),
  analyzeText: (text, url, notionUrl, context) =>
    post('/analyze', { text, url, notion_url: notionUrl, context }),
  analyzeFile: (files, context) => {
    const fd = new FormData()
    const fileList = Array.isArray(files) ? files : [files]
    fileList.forEach(f => fd.append('files', f))
    fd.append('context', JSON.stringify(context))
    return request('POST', '/analyze/file', fd, true)
  },
  save: (source, context, analysis) =>
    post('/projects', { source, context, analysis }),
  update: (id, updates) => patch(`/projects/${id}`, updates),
  delete: (id) => del(`/projects/${id}`),
}

export const jdApi = {
  list: () => get('/jd-targets'),
  get: (id) => get(`/jd-targets/${id}`),
  analyzeText: (text) => post('/jd/analyze', { text }),
  analyzeUrl: (url) => post('/jd/analyze', { url }),
  analyzeFile: (files) => {
    const fd = new FormData()
    const fileList = Array.isArray(files) ? files : [files]
    fileList.forEach(f => fd.append('files', f))
    return request('POST', '/jd/analyze/file', fd, true)
  },
  save: (jd, saveAndMatch = true) =>
    post('/jd-targets', { jd, save_and_match: saveAndMatch }),
  rematch: (id) => post(`/jd-targets/${id}/rematch`),
  update: (id, updates) => patch(`/jd-targets/${id}`, updates),
  delete: (id) => del(`/jd-targets/${id}`),
  rewriteBullets: (jdId, bullets) =>
    post(`/jd/${jdId}/rewrite-bullets`, { bullets }),
}
