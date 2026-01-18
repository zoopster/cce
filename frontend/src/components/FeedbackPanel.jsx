import React, { useState } from 'react'

const SUGGESTIONS = [
  'Make it more technical',
  'Add more examples',
  'Shorten the introduction',
  'Make the tone more casual',
  'Add a summary section'
]

export default function FeedbackPanel({ onIterate, onPublish, isLoading }) {
  const [feedback, setFeedback] = useState('')

  const handleIterate = () => {
    if (feedback.trim()) {
      onIterate(feedback.trim())
      setFeedback('')
    }
  }

  return (
    <div className="feedback-panel">
      <h3>Refine Your Content</h3>

      <div className="suggestions">
        {SUGGESTIONS.map(s => (
          <button
            key={s}
            onClick={() => setFeedback(s)}
            className="suggestion-btn"
            type="button"
          >
            {s}
          </button>
        ))}
      </div>

      <textarea
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
        placeholder="Describe what changes you'd like..."
        rows={3}
        disabled={isLoading}
        aria-label="Feedback for content iteration"
      />

      <div className="actions">
        <button
          onClick={handleIterate}
          disabled={!feedback.trim() || isLoading}
          className="btn secondary"
          type="button"
        >
          {isLoading ? 'Updating...' : 'Apply Changes'}
        </button>
        <button
          onClick={onPublish}
          disabled={isLoading}
          className="btn primary"
          type="button"
        >
          Ready to Publish
        </button>
      </div>
    </div>
  )
}
