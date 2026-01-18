import React from 'react'

export default function AgentStatusPanel({ agents }) {
  if (!agents.length) return null

  return (
    <div className="agent-status-panel">
      <h3>Agent Activity</h3>
      <div className="agent-list" role="log" aria-live="polite">
        {agents.map((agent, i) => (
          <div key={i} className={`agent-item ${agent.status || 'active'}`}>
            <span className="agent-phase">{agent.phase || agent.type}</span>
            <span className="agent-message">{agent.message}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
