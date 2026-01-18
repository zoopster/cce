#!/bin/bash
# Content Creation Engine - Setup and Run Script

set -e

echo "================================================"
echo "Content Creation Engine - Setup & Run"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Verify API key is set
if ! grep -q "^ANTHROPIC_API_KEY=sk-" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: ANTHROPIC_API_KEY not properly set in .env"
    echo "Please edit .env and add your API key:"
    echo "ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
fi

# Create memory directory
mkdir -p app/memory

echo ""
echo "================================================"
echo "Setup complete! Starting server..."
echo "================================================"
echo ""
echo "Server will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Start the server
uvicorn app.main:app --reload
