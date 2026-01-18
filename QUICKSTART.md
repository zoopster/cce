# Quick Start Guide

Get the Content Creation Engine up and running in 5 minutes.

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] Git installed
- [ ] Anthropic API key
- [ ] Firecrawl API key

### Check Versions

```bash
python --version    # Should be 3.10+
node --version      # Should be 18+
npm --version       # Should be included with Node
```

## Step 1: Get API Keys

### Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy your key (starts with `sk-ant-`)

### Firecrawl API Key

1. Go to https://www.firecrawl.dev/
2. Sign up for an account
3. Get your API key from dashboard
4. Copy your key (starts with `fc-`)

## Step 2: Setup Backend

```bash
# Navigate to project directory
cd /Users/johnpugh/Documents/source/cce/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
```

### Edit .env file

Open `.env` in a text editor and add your keys:

```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
FIRECRAWL_API_KEY=fc-your-actual-key-here

# WordPress is optional
WORDPRESS_SITE_URL=
WORDPRESS_USERNAME=
WORDPRESS_APP_PASSWORD=
```

### Start Backend

```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this terminal window open.**

## Step 3: Setup Frontend

Open a **new terminal window**:

```bash
# Navigate to frontend directory
cd /Users/johnpugh/Documents/source/cce/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

You should see:
```
  VITE v5.4.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Keep this terminal window open too.**

## Step 4: Access the Application

1. Open your browser
2. Go to http://localhost:5173
3. You should see the Content Creation Engine interface

## Step 5: Create Your First Content

### 1. Enter a Topic

In the topic input field, enter something like:
```
Write a guide about getting started with sustainable urban gardening
```

### 2. Configure Parameters

Set your preferences:
- **Content Type:** Guide
- **Tone:** Professional
- **Audience:** Beginner
- **Word Count:** 1500

### 3. Start Research

Click "Start Session" and watch:
- Lead agent analyzes your topic
- Multiple research agents search the web in parallel
- Research findings appear in real-time

This takes about 30-120 seconds.

### 4. Generate Content

Once research completes:
- Content begins generating automatically
- Watch it stream in real-time
- This takes about 60-180 seconds

### 5. Iterate (Optional)

If you want to improve the content:
1. Enter feedback like "Add more specific examples"
2. Click "Iterate"
3. Watch the content improve

### 6. Publish or Export

Choose your publishing method:
- **Download HTML:** Get a standalone HTML file
- **WordPress:** Publish directly (if configured)

## Verify Everything Works

### Check Backend

In a new terminal:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status":"healthy","service":"content-creation-engine"}
```

### Check API Docs

Visit: http://localhost:8000/docs

You should see interactive API documentation.

## Common Issues

### "Module not found" error

Make sure you activated the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Port already in use

If port 8000 or 5173 is already in use:

**Backend (8000):**
```bash
uvicorn app.main:app --reload --port 8001
```

**Frontend (5173):**
```bash
npm run dev -- --port 5174
```

### CORS errors

1. Make sure backend is running on port 8000
2. Check that frontend is using correct API URL
3. Restart both servers

### API key errors

1. Verify `.env` file is in the `backend` directory
2. Check that API keys have no spaces or quotes
3. Make sure keys are correct format:
   - Anthropic: `sk-ant-...`
   - Firecrawl: `fc-...`

### Research fails

1. Check Firecrawl API key is valid
2. Verify internet connection
3. Check Firecrawl API status

## Next Steps

Now that you're up and running:

1. **Read the Full README:** `/Users/johnpugh/Documents/source/cce/README.md`
2. **Explore the API:** http://localhost:8000/docs
3. **Try Different Topics:** Experiment with various content types
4. **Configure WordPress:** For direct publishing
5. **Read Architecture Docs:** Understand how it works

## Stopping the Application

### Stop Frontend
In the frontend terminal: Press `Ctrl+C`

### Stop Backend
In the backend terminal: Press `Ctrl+C`

### Deactivate Virtual Environment
```bash
deactivate
```

## Restarting Later

### Backend
```bash
cd /Users/johnpugh/Documents/source/cce/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend
```bash
cd /Users/johnpugh/Documents/source/cce/frontend
npm run dev
```

## Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | User interface |
| Backend API | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Interactive docs |
| Health Check | http://localhost:8000/health | Status check |

## Development Scripts

### Backend
```bash
cd backend

# Run with auto-reload
uvicorn app.main:app --reload

# Test API
python verify_api.py

# Test agents
python test_agents.py
```

### Frontend
```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Getting Help

If you run into issues:

1. Check the [README.md](README.md)
2. Review [ARCHITECTURE.md](ARCHITECTURE.md)
3. Check the terminal output for errors
4. Verify all prerequisites are met
5. Make sure API keys are valid

## Example Workflow

Here's a complete example from start to finish:

```bash
# Terminal 1 - Backend
cd /Users/johnpugh/Documents/source/cce/backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd /Users/johnpugh/Documents/source/cce/frontend
npm run dev

# Browser
# 1. Go to http://localhost:5173
# 2. Enter topic: "Best practices for remote team collaboration"
# 3. Set parameters: Blog Post, Professional, General, 2000 words
# 4. Click "Start Session"
# 5. Wait for research (30-120 seconds)
# 6. Wait for generation (60-180 seconds)
# 7. Review content
# 8. (Optional) Provide feedback and iterate
# 9. Download HTML or publish to WordPress
```

## Success Indicators

You'll know it's working when:

- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] Health check returns {"status":"healthy"}
- [ ] Topic input accepts text
- [ ] Research starts and shows agent activity
- [ ] Content generates and streams to screen
- [ ] You can download or publish the result

## Performance Expectations

- **Research:** 30-120 seconds (depends on topic)
- **Generation:** 60-180 seconds (depends on length)
- **Iteration:** 30-90 seconds
- **Total Time:** 2-5 minutes for complete workflow

## What You Just Built

You now have a working multi-agent AI content creation system that:

1. Uses multiple AI agents working in parallel
2. Researches topics using web search
3. Generates high-quality content
4. Allows iterative refinement
5. Publishes to WordPress or exports HTML

## Learn More

- **Full Documentation:** [README.md](README.md)
- **Architecture Details:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **API Reference:** http://localhost:8000/docs

---

**Congratulations!** You've successfully set up the Content Creation Engine.

Start creating amazing content with AI!
