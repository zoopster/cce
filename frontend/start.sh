#!/bin/bash

# Content Creation Engine - Frontend Start Script
# This script helps you get started with the frontend development

set -e

echo "=================================="
echo "Content Creation Engine - Frontend"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}Error: Node.js version must be 18 or higher${NC}"
    echo "Current version: $(node -v)"
    echo "Please upgrade from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓ Node.js $(node -v) detected${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ npm $(npm -v) detected${NC}"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
    echo ""
fi

# Check if backend is running
echo -e "${YELLOW}Checking backend API...${NC}"
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API is running at http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠ Backend API is not running at http://localhost:8000${NC}"
    echo "Please start the backend first:"
    echo "  cd /Users/johnpugh/Documents/source/cce/backend"
    echo "  uvicorn app.main:app --reload"
    echo ""
    echo -e "${YELLOW}Continue anyway? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "=================================="
echo "Starting Development Server"
echo "=================================="
echo ""
echo "Frontend will be available at:"
echo -e "${GREEN}http://localhost:5173${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
npm run dev
