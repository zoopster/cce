# Frontend Architecture

## Overview

The Content Creation Engine frontend is a single-page React application that guides users through a multi-step content creation workflow with real-time updates from backend AI agents.

## State Machine Architecture

The application uses a finite state machine pattern with 5 steps:

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌────────┐     ┌─────────┐
│  INPUT  │────▶│ RESEARCH │────▶│ GENERATE │────▶│ REVIEW │────▶│ PUBLISH │
└─────────┘     └──────────┘     └──────────┘     └────────┘     └─────────┘
                     │                                  │
                     │                                  │
                     └──────── agents work ─────────────┘
                              (real-time SSE)
```

### State Transitions

1. **INPUT → RESEARCH**: User submits topic and parameters
2. **RESEARCH → GENERATE**: Research completes via SSE
3. **GENERATE → REVIEW**: Content generation completes
4. **REVIEW → REVIEW**: User iterates with feedback (loops)
5. **REVIEW → PUBLISH**: User satisfied with content
6. **PUBLISH → REVIEW**: User wants to edit before publishing

## Component Tree

```
App.jsx (state machine controller)
│
├─ Header
│  ├─ Title
│  └─ StepIndicator [input, research, generate, review, publish]
│
├─ ErrorBanner (conditional)
│
└─ Main
   │
   ├─ InputSection (step === 'input')
   │  ├─ TopicInput
   │  │  ├─ Form
   │  │  ├─ Textarea
   │  │  └─ SubmitButton
   │  │
   │  └─ ParameterPanel
   │     ├─ ContentTypeSelect
   │     ├─ ToneSelect
   │     ├─ AudienceSelect
   │     ├─ WordCountSlider
   │     ├─ KeywordsInput
   │     └─ CustomInstructionsTextarea
   │
   ├─ ResearchSection (step === 'research')
   │  ├─ AgentStatusPanel
   │  │  └─ AgentList
   │  │     └─ AgentItem[] (animated, real-time)
   │  │
   │  └─ ResearchPanel (when complete)
   │     ├─ Summary
   │     └─ SynthesisPreview
   │
   ├─ GenerateSection (step === 'generate')
   │  ├─ AgentStatusPanel
   │  ├─ GenerateButton
   │  └─ ContentEditor (readonly, streaming)
   │
   ├─ ReviewSection (step === 'review')
   │  ├─ ContentEditor (readonly, markdown preview)
   │  └─ FeedbackPanel
   │     ├─ SuggestionButtons[]
   │     ├─ FeedbackTextarea
   │     └─ Actions
   │        ├─ ApplyChangesButton
   │        └─ ReadyToPublishButton
   │
   └─ PublishSection (step === 'publish')
      ├─ SuccessMessage (conditional)
      ├─ ErrorMessage (conditional)
      ├─ PublishOptions
      │  ├─ DownloadHTMLCard
      │  │  └─ DownloadButton
      │  │
      │  └─ WordPressCard
      │     ├─ SiteURLInput
      │     ├─ UsernameInput
      │     ├─ AppPasswordInput
      │     ├─ StatusSelect
      │     └─ PublishButton
      │
      └─ BackToEditButton
```

## Data Flow

### Application State

Managed in `App.jsx`:

```javascript
{
  step: 'input' | 'research' | 'generate' | 'review' | 'publish',
  session: { session_id, topic, created_at },
  parameters: {
    content_type: string,
    tone: string,
    audience_level: string,
    word_count: number,
    keywords: string[],
    custom_instructions: string
  },
  agentStates: [{ type, phase, message, status }],
  research: { total_sources, synthesis_preview },
  content: string,
  isLoading: boolean,
  error: string | null
}
```

### Event Flow

#### 1. Session Creation

```
User Input
    ↓
TopicInput.handleSubmit()
    ↓
App.handleStartSession()
    ↓
API.createSession(topic, parameters)
    ↓
Response: { session_id, topic, ... }
    ↓
setSession(newSession)
setStep('research')
```

#### 2. Research Phase (SSE)

```
App.handleStartSession() continues...
    ↓
API.startResearch(session_id, callbacks)
    ↓
EventSource: /api/sessions/{id}/research
    ↓
onmessage: { phase, message }
    ↓
setAgentStates(prev => [...prev, data])
    ↓
'complete' event: { total_sources, ... }
    ↓
setResearch(data)
setStep('generate')
```

#### 3. Content Generation (SSE)

```
User clicks "Generate Content"
    ↓
App.handleGenerate()
    ↓
API.generateContent(session_id, callbacks)
    ↓
EventSource: /api/sessions/{id}/generate
    ↓
'content' events: { chunk }
    ↓
setContent(prev => prev + chunk)
    ↓
'complete' event
    ↓
setStep('review')
```

#### 4. Iteration (SSE)

```
User provides feedback
    ↓
FeedbackPanel.handleIterate()
    ↓
App.handleIterate(feedback)
    ↓
API.iterateContent(session_id, feedback, callbacks)
    ↓
POST /api/sessions/{id}/iterate
    ↓
Streaming response chunks
    ↓
setContent(prev => prev + chunk)
    ↓
Complete → setStep('review')
```

#### 5. Publishing

```
User clicks publish option
    ↓
PublishPanel actions
    ↓
WordPress:
  API.publishToWordPress(session_id, config)
  → POST /api/sessions/{id}/publish/wordpress
  → Response: { url, status }
  → Display success message

HTML Download:
  API.downloadHTML(session_id)
  → window.open(/api/sessions/{id}/download)
  → Browser downloads file
```

## API Client Architecture

### Client Methods

Located in `/Users/johnpugh/Documents/source/cce/frontend/src/api/client.js`:

```javascript
// REST Endpoints
createSession(topic, parameters) → Promise<Session>
publishToWordPress(sessionId, config) → Promise<PublishResult>
exportToHTML(sessionId) → Promise<ExportResult>
downloadHTML(sessionId) → void

// SSE Endpoints
startResearch(sessionId, callbacks) → EventSource
  callbacks: { onStatus, onComplete, onError }

generateContent(sessionId, callbacks) → EventSource
  callbacks: { onChunk, onComplete, onError }

iterateContent(sessionId, feedback, callbacks) → Promise<void>
  callbacks: { onChunk, onComplete, onError }
  (uses fetch with streaming reader)
```

### SSE Implementation

```javascript
// EventSource pattern for research
const eventSource = new EventSource(`${API_BASE}/sessions/${id}/research`)

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  callbacks.onStatus?.(data)
}

eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data)
  callbacks.onComplete?.(data)
  eventSource.close()
})

eventSource.onerror = (err) => {
  callbacks.onError?.(err)
  eventSource.close()
}
```

### Streaming Response Pattern

```javascript
// ReadableStream pattern for iteration
const response = await fetch(url, { method: 'POST', body: ... })
const reader = response.body.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break

  const text = decoder.decode(value)
  const lines = text.split('\n').filter(l => l.startsWith('data:'))

  for (const line of lines) {
    const data = JSON.parse(line.slice(5))
    if (data.chunk) callbacks.onChunk?.(data.chunk)
  }
}
```

## CSS Architecture

### Design System

CSS Variables in `main.css`:

```css
:root {
  /* Colors */
  --color-primary: #2563eb;
  --color-secondary: #64748b;
  --color-success: #10b981;
  --color-error: #ef4444;

  /* Backgrounds */
  --color-bg: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);

  /* Border Radius */
  --radius: 8px;
  --radius-sm: 4px;
  --radius-lg: 12px;

  /* Transitions */
  --transition: 150ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Component Styling Pattern

Each component follows BEM-inspired naming:

```css
/* Block */
.component-name { }

/* Elements */
.component-name__element { }

/* Modifiers */
.component-name--modifier { }
.component-name__element--modifier { }

/* States */
.component-name.active { }
.component-name.completed { }
.component-name.error { }
```

### Responsive Strategy

Mobile-first approach:

```css
/* Base styles (mobile) */
.component { }

/* Tablet and up */
@media (min-width: 768px) { }

/* Desktop */
@media (min-width: 1024px) { }
```

## Performance Optimizations

### React Patterns

1. **useCallback for handlers**: Prevents unnecessary re-renders
2. **Conditional rendering**: Only render active step components
3. **Key props**: Stable keys for list items
4. **Minimal state updates**: Batch related updates

### CSS Optimizations

1. **CSS Variables**: Centralized theming
2. **Hardware acceleration**: transform, opacity for animations
3. **Efficient selectors**: Avoid deep nesting
4. **Critical CSS**: Inline above-fold styles (future)

### Network Optimizations

1. **Vite code splitting**: Automatic chunk splitting
2. **SSE connection reuse**: Single connection per stream
3. **Proxy configuration**: No CORS preflight
4. **Streaming responses**: Progressive content display

## Accessibility Features

### Semantic HTML

```jsx
<header role="banner">
<main role="main">
<form role="form">
<div role="log" aria-live="polite"> // for agent updates
<div role="status"> // for success messages
<div role="alert"> // for errors
```

### ARIA Attributes

```jsx
<textarea aria-label="Content topic" />
<input aria-label={`Word count: ${value}`} />
<div aria-live="polite"> // dynamic content
<div aria-atomic="true"> // read entire region
```

### Keyboard Navigation

- All interactive elements focusable
- Tab order matches visual flow
- Focus visible styles for keyboard users
- No keyboard traps

### Screen Reader Support

- Descriptive labels
- Status updates announced
- Error messages linked to inputs
- Landmarks for navigation

## Build Configuration

### Vite Config

```javascript
{
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}
```

### Production Build

```bash
npm run build
```

Outputs to `dist/`:
- Minified JavaScript bundles
- Optimized CSS
- Hashed filenames for caching
- Source maps for debugging

## Error Handling

### Levels

1. **Network Errors**: Caught by API client, shown in ErrorBanner
2. **SSE Errors**: EventSource onerror, shown in ErrorBanner
3. **Validation Errors**: Form-level validation, inline errors
4. **Server Errors**: HTTP error responses, shown in ErrorBanner

### User Feedback

```javascript
try {
  await apiCall()
} catch (err) {
  setError(err.message) // Displayed in ErrorBanner
} finally {
  setIsLoading(false)
}
```

## Testing Strategy (Future)

### Unit Tests

- Component rendering
- User interactions
- State updates
- API client methods

### Integration Tests

- Multi-step workflows
- SSE connection handling
- Form submission flows
- Error scenarios

### E2E Tests

- Complete content creation flow
- WordPress publishing
- HTML export
- Iteration loops

## Deployment Considerations

### Environment Variables

```env
VITE_API_BASE_URL=https://api.example.com
```

### Production Checklist

- [ ] Build optimized bundle
- [ ] Configure backend URL
- [ ] Set up HTTPS
- [ ] Configure CORS
- [ ] Enable compression
- [ ] Add analytics
- [ ] Set up error tracking
- [ ] Configure CDN

## Future Enhancements

1. **TypeScript migration**: Type safety
2. **Redux/Zustand**: Complex state management
3. **React Query**: Server state caching
4. **Web Workers**: Background processing
5. **Service Workers**: Offline support
6. **Progressive Web App**: Install prompt
7. **Advanced analytics**: User behavior tracking
8. **A/B testing**: Feature experiments
9. **Internationalization**: Multi-language support
10. **Dark mode**: User preference
