import React, { useState } from 'react'
import { publishToWordPress, downloadHTML } from '../api/client'

export default function PublishPanel({ sessionId, onBack }) {
  const [wpConfig, setWpConfig] = useState({
    site_url: '',
    username: '',
    app_password: '',
    status: 'draft'
  })
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleWordPress = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await publishToWordPress(sessionId, wpConfig)
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownload = () => downloadHTML(sessionId)

  return (
    <div className="publish-panel">
      <h2>Publish Your Content</h2>

      {result && (
        <div className="success-message" role="status">
          Published successfully via {result.method === 'mcp' ? 'WordPress MCP' : 'REST API'}!{' '}
          <a href={result.url} target="_blank" rel="noopener noreferrer">View Post</a>
        </div>
      )}

      {error && <div className="error-message" role="alert">{error}</div>}

      <div className="publish-options">
        <div className="option-card">
          <h3>Download HTML</h3>
          <p>Download as a standalone HTML file</p>
          <button onClick={handleDownload} className="btn primary" type="button">
            Download HTML
          </button>
        </div>

        <div className="option-card">
          <h3>Publish to WordPress</h3>
          <div className="wp-form">
            <input
              type="url"
              placeholder="Site URL (https://your-site.com)"
              value={wpConfig.site_url}
              onChange={(e) => setWpConfig({ ...wpConfig, site_url: e.target.value })}
              aria-label="WordPress site URL"
            />
            <input
              type="text"
              placeholder="Username"
              value={wpConfig.username}
              onChange={(e) => setWpConfig({ ...wpConfig, username: e.target.value })}
              aria-label="WordPress username"
            />
            <input
              type="password"
              placeholder="App Password"
              value={wpConfig.app_password}
              onChange={(e) => setWpConfig({ ...wpConfig, app_password: e.target.value })}
              aria-label="WordPress app password"
            />
            <select
              value={wpConfig.status}
              onChange={(e) => setWpConfig({ ...wpConfig, status: e.target.value })}
              aria-label="Post status"
            >
              <option value="draft">Save as Draft</option>
              <option value="publish">Publish Now</option>
            </select>
            <button
              onClick={handleWordPress}
              disabled={isLoading}
              className="btn primary"
              type="button"
            >
              {isLoading ? 'Publishing...' : 'Publish to WordPress'}
            </button>
          </div>
        </div>
      </div>

      <button onClick={onBack} className="btn secondary back-btn" type="button">
        &larr; Back to Edit
      </button>
    </div>
  )
}
