#!/bin/bash

echo "🚀 Smart Checkout System - Setup Script"
echo "========================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Stop existing containers
echo "📦 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Initializing database..."
docker-compose exec -T backend python -m app.seed

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✨ Setup Complete!"
echo ""
echo "🌐 Services:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo "   n8n:       http://localhost:5678 (admin/admin123)"
echo ""
echo "👤 Test Credentials:"
echo "   Customer: Any 10-digit phone number"
echo "   Staff:    staff@store.com / staff123"
echo "   Admin:    admin@store.com / admin123"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
