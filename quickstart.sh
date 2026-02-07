#!/bin/bash

# Smart Checkout System - Quick Start Script
# This script helps you set up and run the system quickly

echo "🛒 Smart Checkout System - Quick Start"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
else
    echo -e "${GREEN}✅ Docker found${NC}"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
else
    echo -e "${GREEN}✅ Docker Compose found${NC}"
fi

echo ""
echo "🔧 Setup Options:"
echo "1. Quick Start (Docker Compose - Recommended)"
echo "2. Manual Setup (Local Development)"
echo ""
read -p "Choose option (1 or 2): " option

if [ "$option" == "1" ]; then
    echo ""
    echo "🐳 Starting with Docker Compose..."
    
    # Create .env files if they don't exist
    if [ ! -f backend/.env ]; then
        echo "📝 Creating backend .env file..."
        cp backend/.env.example backend/.env
    fi
    
    if [ ! -f frontend/.env ]; then
        echo "📝 Creating frontend .env file..."
        echo "VITE_API_URL=http://localhost:8000/api/v1" > frontend/.env
    fi
    
    # Start Docker Compose
    echo "🚀 Starting services..."
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✅ Services started successfully!${NC}"
    echo ""
    echo "📱 Access the application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   n8n Automation: http://localhost:5678"
    echo ""
    echo "🔐 Default Credentials:"
    echo "   Staff Login: admin@store.com / admin123"
    echo "   n8n Login: admin / admin123"
    echo ""
    echo "📊 View logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
    
elif [ "$option" == "2" ]; then
    echo ""
    echo "🔧 Manual Setup Instructions"
    echo ""
    echo "1️⃣ Backend Setup:"
    echo "   cd backend"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "   pip install -r requirements.txt"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your configuration"
    echo "   createdb smartcheckout_db"
    echo "   uvicorn app.main:app --reload"
    echo ""
    echo "2️⃣ Frontend Setup:"
    echo "   cd frontend"
    echo "   npm install"
    echo "   npm run dev"
    echo ""
    echo "3️⃣ Database Setup:"
    echo "   Make sure PostgreSQL is running"
    echo "   Create database: createdb smartcheckout_db"
    echo ""
else
    echo -e "${RED}Invalid option${NC}"
    exit 1
fi
