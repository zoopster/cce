import React from 'react'

export default function ResearchPanel({ research }) {
  if (!research) return null

  return (
    <div className="research-panel">
      <h3>Research Complete</h3>
      <p className="research-summary">
        Found {research.total_sources || 0} sources
      </p>
      {research.synthesis_preview && (
        <div className="synthesis-preview">
          <h4>Key Findings</h4>
          <p>{research.synthesis_preview}</p>
        </div>
      )}
    </div>
  )
}
