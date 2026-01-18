# Content Creation Engine - Frontend

A modern React frontend for the multi-agent content creation system.

## Features

- **Topic Input**: Enter content ideas with customizable parameters
- **Real-time Agent Activity**: Watch AI agents research and create content via Server-Sent Events
- **Research Visualization**: See synthesized research results before generation
- **Streaming Content**: Watch content being generated in real-time
- **Iterative Refinement**: Provide feedback and iterate on content
- **Publishing Options**: Export to HTML or publish directly to WordPress

## Tech Stack

- React 18.3
- Vite 5.4 (build tool)
- React Markdown (content preview)
- Modern CSS with CSS Variables
- Server-Sent Events for real-time updates

## Prerequisites

- Node.js 18+ or npm
- Backend API running at http://localhost:8000

## Installation

```bash
cd /Users/johnpugh/Documents/source/cce/frontend
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at http://localhost:5173

## Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

Preview production build:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── index.html                 # Entry HTML
├── vite.config.js            # Vite configuration
├── package.json              # Dependencies
├── src/
│   ├── index.jsx            # React entry point
│   ├── App.jsx              # Main app component with workflow state machine
│   ├── api/
│   │   └── client.js        # API client with SSE support
│   ├── components/
│   │   ├── TopicInput.jsx           # Topic entry form
│   │   ├── ParameterPanel.jsx       # Content settings
│   │   ├── AgentStatusPanel.jsx     # Real-time agent activity
│   │   ├── ResearchPanel.jsx        # Research results
│   │   ├── ContentEditor.jsx        # Content display/preview
│   │   ├── FeedbackPanel.jsx        # Iteration controls
│   │   └── PublishPanel.jsx         # Publishing options
│   └── styles/
│       └── main.css         # Global styles
```

## Workflow Steps

1. **Input**: Enter topic and configure parameters (content type, tone, audience, word count, keywords)
2. **Research**: Watch agents gather and synthesize information (real-time SSE updates)
3. **Generate**: Trigger content generation (streaming output)
4. **Review**: Preview generated content, provide feedback for iteration
5. **Publish**: Export as HTML or publish to WordPress

## API Integration

The frontend connects to the backend API via proxy configuration:

- `/api/*` → `http://localhost:8000/api/*`

All API calls are made through `/Users/johnpugh/Documents/source/cce/frontend/src/api/client.js` which handles:

- Session creation
- Research SSE stream
- Content generation SSE stream
- Iteration requests
- WordPress publishing
- HTML export

## Accessibility Features

- Semantic HTML structure
- ARIA labels on all interactive elements
- ARIA live regions for dynamic content
- Keyboard navigation support
- Focus visible styles
- Reduced motion support
- High contrast colors (WCAG 2.1 AA compliant)

## Performance Optimizations

- Vite's fast HMR for development
- Code splitting ready
- Optimized CSS with variables
- Efficient React rendering patterns
- Minimal dependencies

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Modern mobile browsers

## Troubleshooting

### Backend Connection Issues

If you see connection errors, ensure:
1. Backend is running at http://localhost:8000
2. Check browser console for CORS errors
3. Verify proxy configuration in `vite.config.js`

### SSE Not Working

Server-Sent Events require:
1. Backend to send proper SSE headers
2. Connection to stay open
3. No aggressive firewalls blocking streaming connections

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

## Contributing

When adding new components:
1. Follow the existing component structure
2. Add proper PropTypes or TypeScript interfaces
3. Include accessibility attributes (ARIA labels, roles)
4. Use CSS variables for colors and spacing
5. Test with keyboard navigation
6. Ensure mobile responsiveness

## License

MIT
