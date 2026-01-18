# Quick Setup Guide

## Installation Steps

### 1. Install Dependencies

```bash
cd /Users/johnpugh/Documents/source/cce/frontend
npm install
```

This will install:
- React 18.3.1
- React DOM 18.3.1
- React Markdown 9.0.0
- Vite 5.4.0
- @vitejs/plugin-react 4.3.0

### 2. Verify Backend is Running

Ensure your backend API is running at:
```
http://localhost:8000
```

You can test it with:
```bash
curl http://localhost:8000/api/health
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will start at:
```
http://localhost:5173
```

## First Time Usage

1. Open http://localhost:5173 in your browser
2. You'll see the "Input" step with a topic textarea
3. Enter a topic like "Benefits of AI in Healthcare"
4. Configure settings (optional):
   - Content Type: Blog Post, Technical Tutorial, or Marketing Content
   - Tone: Professional, Casual, Technical, or Friendly
   - Audience: General, Beginner, Intermediate, or Expert
   - Word Count: 500-5000 (slider)
   - Keywords: Comma-separated list
   - Custom Instructions: Additional guidance
5. Click "Start Creating"
6. Watch the research phase with real-time agent updates
7. Click "Generate Content" when research completes
8. Review the generated content
9. Optionally provide feedback to iterate
10. Publish to WordPress or download as HTML

## Architecture Overview

### State Machine Flow

```
INPUT → RESEARCH → GENERATE → REVIEW → PUBLISH
  ↓         ↓          ↓          ↓        ↓
topic   SSE events  SSE stream  feedback  export
params   research    content    iterate   WordPress
```

### Component Hierarchy

```
App (state machine)
├── TopicInput (step: input)
├── ParameterPanel (step: input)
├── AgentStatusPanel (steps: research, generate)
├── ResearchPanel (step: research)
├── ContentEditor (steps: generate, review)
├── FeedbackPanel (step: review)
└── PublishPanel (step: publish)
```

### API Client Methods

- `createSession(topic, parameters)` - Initialize session
- `startResearch(sessionId, callbacks)` - SSE research stream
- `generateContent(sessionId, callbacks)` - SSE content stream
- `iterateContent(sessionId, feedback, callbacks)` - Stream iteration
- `publishToWordPress(sessionId, config)` - WordPress publishing
- `downloadHTML(sessionId)` - Download HTML file

## Testing the Full Workflow

### Example 1: Blog Post

```
Topic: "How to build a REST API with FastAPI"
Content Type: Technical Tutorial
Tone: Professional
Audience: Intermediate
Word Count: 2000
Keywords: FastAPI, Python, REST API, backend
```

### Example 2: Marketing Content

```
Topic: "Why small businesses need automation"
Content Type: Marketing Content
Tone: Friendly
Audience: General
Word Count: 1500
Keywords: automation, small business, efficiency
```

### Example 3: Technical Deep Dive

```
Topic: "Understanding OAuth 2.0 authentication flows"
Content Type: Technical Tutorial
Tone: Technical
Audience: Expert
Word Count: 3000
Keywords: OAuth, authentication, security, JWT
```

## Troubleshooting

### Issue: Page is blank

**Solution**: Check browser console for errors. Common causes:
- Backend not running at http://localhost:8000
- CORS issues (backend must allow localhost:5173)
- JavaScript errors (check React DevTools)

### Issue: SSE not connecting

**Solution**:
- Verify backend SSE endpoints are working
- Check network tab for EventSource connections
- Ensure backend sends proper `Content-Type: text/event-stream`
- Check for proxy errors in Vite logs

### Issue: Styles not loading

**Solution**:
- Clear browser cache
- Check that `src/styles/main.css` is imported in `src/index.jsx`
- Restart Vite dev server

### Issue: Components not rendering

**Solution**:
- Check React DevTools component tree
- Look for PropTypes warnings in console
- Verify imports are using correct paths
- Check for missing dependencies with `npm list`

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. Changes to:
- JSX files update instantly
- CSS files update without reload
- State is preserved during updates

### React DevTools

Install React DevTools browser extension to:
- Inspect component tree
- View component props and state
- Profile performance
- Track re-renders

### Browser Console

Watch for:
- API errors (network failures)
- SSE connection status
- State updates
- Render cycles

### Network Tab

Monitor:
- SSE connections (should stay open)
- API request/response bodies
- Response times
- Error status codes

## Performance Monitoring

### Key Metrics

- First Contentful Paint (FCP): < 1.8s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.8s
- Cumulative Layout Shift (CLS): < 0.1

### Tools

```bash
# Lighthouse audit
npm run build
npm run preview
# Then run Lighthouse in Chrome DevTools
```

## Customization

### Colors

Edit CSS variables in `/Users/johnpugh/Documents/source/cce/frontend/src/styles/main.css`:

```css
:root {
  --color-primary: #2563eb;
  --color-secondary: #64748b;
  --color-success: #10b981;
  --color-error: #ef4444;
}
```

### Layout

Modify max-width and padding in:
```css
.main {
  max-width: 1200px; /* Change this */
  padding: 2rem;
}
```

### Components

Each component is self-contained in `/Users/johnpugh/Documents/source/cce/frontend/src/components/`. Modify as needed:

- `TopicInput.jsx` - Topic entry form
- `ParameterPanel.jsx` - Content settings
- `AgentStatusPanel.jsx` - Real-time updates
- `ResearchPanel.jsx` - Research results
- `ContentEditor.jsx` - Content preview
- `FeedbackPanel.jsx` - Iteration controls
- `PublishPanel.jsx` - Publishing options

## Next Steps

1. Run the backend API
2. Install frontend dependencies
3. Start development server
4. Test the full workflow
5. Customize styles and components as needed
6. Build for production when ready

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review browser console for errors
3. Check backend API logs
4. Verify all dependencies are installed
5. Ensure Node.js version is 18+
