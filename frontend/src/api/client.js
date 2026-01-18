const API_BASE = '/api'

export async function createSession(topic, parameters) {
  const response = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, parameters })
  })
  if (!response.ok) throw new Error('Failed to create session')
  return response.json()
}

export async function startResearch(sessionId, callbacks) {
  // Use fetch for SSE since the endpoint is POST (EventSource only supports GET)
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/research`, {
    method: 'POST',
    headers: { 'Accept': 'text/event-stream' }
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Research failed' }))
    throw new Error(error.detail || 'Research failed')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  const processEvents = async () => {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      let currentEvent = 'message'
      for (const line of lines) {
        if (line.startsWith('event:')) {
          currentEvent = line.slice(6).trim()
        } else if (line.startsWith('data:')) {
          const data = line.slice(5).trim()
          if (!data) continue

          try {
            const parsed = JSON.parse(data)
            if (currentEvent === 'complete') {
              callbacks.onComplete?.(parsed)
            } else {
              callbacks.onStatus?.(parsed)
            }
          } catch (e) {
            console.warn('Failed to parse SSE data:', e)
          }
        }
      }
    }
  }

  processEvents().catch((err) => {
    callbacks.onError?.(new Error(err.message || 'Connection lost'))
  })

  return { close: () => reader.cancel() }
}

export async function generateContent(sessionId, callbacks) {
  // Use fetch for SSE since the endpoint is POST
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/generate`, {
    method: 'POST',
    headers: { 'Accept': 'text/event-stream' }
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Generation failed' }))
    throw new Error(error.detail || 'Generation failed')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  const processEvents = async () => {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      let currentEvent = 'message'
      for (const line of lines) {
        if (line.startsWith('event:')) {
          currentEvent = line.slice(6).trim()
        } else if (line.startsWith('data:')) {
          const data = line.slice(5).trim()
          if (!data) continue

          try {
            const parsed = JSON.parse(data)
            if (currentEvent === 'complete') {
              callbacks.onComplete?.()
            } else if (currentEvent === 'content') {
              callbacks.onChunk?.(parsed.chunk)
            }
          } catch (e) {
            console.warn('Failed to parse content chunk:', e)
          }
        }
      }
    }
  }

  processEvents().catch((err) => {
    callbacks.onError?.(new Error(err.message || 'Content generation connection lost'))
  })

  return { close: () => reader.cancel() }
}

export async function iterateContent(sessionId, feedback, callbacks) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/iterate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feedback })
  })

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const text = decoder.decode(value)
    const lines = text.split('\n').filter(l => l.startsWith('data:'))

    for (const line of lines) {
      try {
        const data = JSON.parse(line.slice(5))
        if (data.chunk) callbacks.onChunk?.(data.chunk)
      } catch {}
    }
  }

  callbacks.onComplete?.()
}

export async function publishToWordPress(sessionId, config) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/publish/wordpress`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to publish' }))
    throw new Error(error.detail || 'Failed to publish')
  }
  return response.json()
}

export async function exportToHTML(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/publish/html`, {
    method: 'POST'
  })
  if (!response.ok) throw new Error('Failed to export')
  return response.json()
}

export async function downloadHTML(sessionId) {
  window.open(`${API_BASE}/sessions/${sessionId}/download`, '_blank')
}
