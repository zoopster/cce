import React from 'react'
import ReactMarkdown from 'react-markdown'

export default function ContentEditor({ content, readOnly = false, onChange }) {
  if (readOnly) {
    return (
      <div className="content-editor readonly">
        <div className="content-preview">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    )
  }

  return (
    <div className="content-editor">
      <textarea
        value={content}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder="Content will appear here..."
        aria-label="Content editor"
      />
    </div>
  )
}
