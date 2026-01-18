import React, { useState } from 'react'

export default function ParameterPanel({ parameters, onChange }) {
  const update = (key, value) => onChange({ ...parameters, [key]: value })

  // Track raw keyword input separately to allow typing commas
  const [keywordInput, setKeywordInput] = useState(parameters.keywords?.join(', ') || '')

  return (
    <div className="parameter-panel">
      <h3>Content Settings</h3>

      <div className="param-group">
        <label htmlFor="content-type">Content Type</label>
        <select
          id="content-type"
          value={parameters.content_type}
          onChange={(e) => update('content_type', e.target.value)}
        >
          <option value="blog_post">Blog Post</option>
          <option value="technical_tutorial">Technical Tutorial</option>
          <option value="marketing_content">Marketing Content</option>
        </select>
      </div>

      <div className="param-group">
        <label htmlFor="tone">Tone</label>
        <select
          id="tone"
          value={parameters.tone}
          onChange={(e) => update('tone', e.target.value)}
        >
          <option value="professional">Professional</option>
          <option value="casual">Casual</option>
          <option value="technical">Technical</option>
          <option value="friendly">Friendly</option>
        </select>
      </div>

      <div className="param-group">
        <label htmlFor="audience">Audience</label>
        <select
          id="audience"
          value={parameters.audience_level}
          onChange={(e) => update('audience_level', e.target.value)}
        >
          <option value="general">General</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="expert">Expert</option>
        </select>
      </div>

      <div className="param-group">
        <label htmlFor="word-count">Word Count: {parameters.word_count}</label>
        <input
          id="word-count"
          type="range"
          min="500"
          max="5000"
          step="100"
          value={parameters.word_count}
          onChange={(e) => update('word_count', parseInt(e.target.value))}
          aria-label={`Word count: ${parameters.word_count}`}
        />
      </div>

      <div className="param-group">
        <label htmlFor="keywords">Keywords (comma-separated)</label>
        <input
          id="keywords"
          type="text"
          value={keywordInput}
          onChange={(e) => setKeywordInput(e.target.value)}
          onBlur={(e) => update('keywords', e.target.value.split(',').map(k => k.trim()).filter(Boolean))}
          placeholder="keyword1, keyword2..."
        />
      </div>

      <div className="param-group">
        <label htmlFor="custom-instructions">Custom Instructions</label>
        <textarea
          id="custom-instructions"
          value={parameters.custom_instructions}
          onChange={(e) => update('custom_instructions', e.target.value)}
          placeholder="Any specific instructions for content generation..."
          rows={2}
        />
      </div>
    </div>
  )
}
