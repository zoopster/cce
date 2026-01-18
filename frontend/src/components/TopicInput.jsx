import React, { useState } from 'react'

export default function TopicInput({ onSubmit, isLoading }) {
  const [topic, setTopic] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (topic.trim()) onSubmit(topic.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="topic-input">
      <h2>What would you like to write about?</h2>
      <textarea
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter your topic or content idea..."
        rows={4}
        disabled={isLoading}
        aria-label="Content topic"
      />
      <button type="submit" disabled={!topic.trim() || isLoading} className="btn primary">
        {isLoading ? 'Starting...' : 'Start Creating'}
      </button>
    </form>
  )
}
