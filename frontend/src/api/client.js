async function request(path, options = {}) {
  const res = await fetch(path, options)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export function getProjects() {
  return request('/api/projects')
}

export function getProject(id) {
  return request(`/api/projects/${id}`)
}

export function analyzeSource(source, context) {
  return request('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source, context }),
  })
}

export function analyzeFile(files, context) {
  const fd = new FormData()
  for (const file of files) fd.append('files', file)
  fd.append('context', JSON.stringify(context))
  return request('/api/analyze/file', { method: 'POST', body: fd })
}

export function saveProject(analysis, rawText, sourceMetadata) {
  return request('/api/projects', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis, raw_text: rawText, source_metadata: sourceMetadata }),
  })
}

export function patchProject(id, context, reanalyze = false, resumeBullets = null) {
  const body = { context, reanalyze }
  if (resumeBullets !== null) body.resume_bullets = resumeBullets
  return request(`/api/projects/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function deleteProject(id) {
  return request(`/api/projects/${id}`, { method: 'DELETE' })
}

// --- JD targets ---

export function getJDTargets() {
  return request('/api/jd-targets')
}

export function analyzeJDSource(source) {
  return request('/api/jd/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source }),
  })
}

export function analyzeJDFile(file) {
  const fd = new FormData()
  fd.append('file', file)
  return request('/api/jd/analyze/file', { method: 'POST', body: fd })
}

export function saveJDTarget(analysis, rawJdText, sourceMetadata) {
  return request('/api/jd-targets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis, raw_jd_text: rawJdText, source_metadata: sourceMetadata }),
  })
}

export function rematchJDTarget(id, projectIds = null) {
  return request(`/api/jd-targets/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_ids: projectIds }),
  })
}

export function saveJDBullets(id, matchedProjects) {
  return request(`/api/jd-targets/${id}/bullets`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ matched_projects: matchedProjects }),
  })
}

export function improveJDBullets(id, bullets) {
  return request(`/api/jd-targets/${id}/improve-bullets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bullets }),
  })
}

export function deleteJDTarget(id) {
  return request(`/api/jd-targets/${id}`, { method: 'DELETE' })
}
