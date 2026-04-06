#!/bin/bash

# Docker Deployment Script for Django Dress Shop (SQLite)

echo "🐳 Starting Docker Deployment with SQLite..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your actual values before running again."
    exit 1
fi

# Build and start containers
echo "🏗️  Building Docker images..."
docker-compose build

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec web python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser (optional)..."
echo "Run 'docker-compose exec web python manage.py createsuperuser' to create admin user"

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

echo "✅ Docker deployment complete!"
echo "🌐 Application is running at: http://localhost:8000"
echo "� SQLite database is persisted in Docker volume"
echo "�📊 View logs with: docker-compose logs -f"
echo "🛑 Stop containers with: docker-compose down"
echo "💡 To access database: docker-compose exec web python manage.py dbshell"
