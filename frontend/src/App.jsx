import React, { useState, useCallback } from 'react'
import TopicInput from './components/TopicInput'
import ParameterPanel from './components/ParameterPanel'
import AgentStatusPanel from './components/AgentStatusPanel'
import ResearchPanel from './components/ResearchPanel'
import ContentEditor from './components/ContentEditor'
import FeedbackPanel from './components/FeedbackPanel'
import PublishPanel from './components/PublishPanel'
import { createSession, startResearch, generateContent, iterateContent } from './api/client'

const STEPS = ['input', 'research', 'generate', 'review', 'publish']

export default function App() {
  const [step, setStep] = useState('input')
  const [session, setSession] = useState(null)
  const [parameters, setParameters] = useState({
    content_type: 'blog_post',
    tone: 'professional',
    audience_level: 'general',
    word_count: 1500,
    keywords: [],
    custom_instructions: ''
  })
  const [agentStates, setAgentStates] = useState([])
  const [research, setResearch] = useState(null)
  const [content, setContent] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleStartSession = useCallback(async (topic) => {
    setIsLoading(true)
    setError(null)
    try {
      const newSession = await createSession(topic, parameters)
      setSession(newSession)
      setStep('research')

      // Start research with SSE
      await startResearch(newSession.session_id, {
        onStatus: (data) => setAgentStates(prev => [...prev, { type: 'status', ...data }]),
        onComplete: (data) => {
          setResearch(data)
          setStep('generate')
        },
        onError: (err) => setError(err?.message || 'Research failed')
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [parameters])

  const handleGenerate = useCallback(async () => {
    setIsLoading(true)
    setContent('')
    try {
      await generateContent(session.session_id, {
        onChunk: (chunk) => setContent(prev => prev + chunk),
        onComplete: () => setStep('review'),
        onError: (err) => setError(err?.message || 'Content generation failed')
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [session])

  const handleIterate = useCallback(async (feedback) => {
    setIsLoading(true)
    setContent('')
    try {
      await iterateContent(session.session_id, feedback, {
        onChunk: (chunk) => setContent(prev => prev + chunk),
        onComplete: () => setStep('review'),
        onError: (err) => setError(err?.message || 'Content iteration failed')
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [session])

  const handlePublish = () => setStep('publish')
  const handleBack = () => setStep('review')

  return (
    <div className="app">
      <header className="header">
        <h1>Content Creation Engine</h1>
        <div className="step-indicator">
          {STEPS.map((s, i) => (
            <span key={s} className={`step ${step === s ? 'active' : ''} ${STEPS.indexOf(step) > i ? 'completed' : ''}`}>
              {s}
            </span>
          ))}
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <main className="main">
        {step === 'input' && (
          <div className="input-section">
            <TopicInput onSubmit={handleStartSession} isLoading={isLoading} />
            <ParameterPanel parameters={parameters} onChange={setParameters} />
          </div>
        )}

        {step === 'research' && (
          <div className="research-section">
            <AgentStatusPanel agents={agentStates} />
            {research && <ResearchPanel research={research} />}
          </div>
        )}

        {step === 'generate' && (
          <div className="generate-section">
            <AgentStatusPanel agents={agentStates} />
            <button onClick={handleGenerate} disabled={isLoading} className="btn primary">
              {isLoading ? 'Generating...' : 'Generate Content'}
            </button>
            {content && <ContentEditor content={content} readOnly />}
          </div>
        )}

        {step === 'review' && (
          <div className="review-section">
            <ContentEditor content={content} readOnly />
            <FeedbackPanel onIterate={handleIterate} onPublish={handlePublish} isLoading={isLoading} />
          </div>
        )}

        {step === 'publish' && (
          <PublishPanel sessionId={session?.session_id} onBack={handleBack} />
        )}
      </main>
    </div>
  )
}
