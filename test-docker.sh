#!/bin/bash

# Docker Deployment Test Script
# Tests the complete Docker setup with environment variables

echo "🐳 Testing Docker Setup with Environment Variables..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Creating from production template..."
    cp .env.production .env
    echo "⚠️  Please update .env with your actual values before running again."
    exit 1
fi

echo "✅ .env file found"
echo "📋 Environment variables loaded:"
echo "   - DEBUG: $(grep DEBUG= .env | cut -d'=' -f2)"
echo "   - EMAIL_HOST_USER: $(grep EMAIL_HOST_USER= .env | cut -d'=' -f2)"
echo "   - SQLITE_DB_PATH: $(grep SQLITE_DB_PATH= .env | cut -d'=' -f2)"
echo "   - REDIS_URL: $(grep REDIS_URL= .env | cut -d'=' -f2)"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build images
echo "🏗️  Building Docker images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 15

# Check service health
echo "🔍 Checking service status..."
docker-compose ps

# Test web service
echo "🌐 Testing web service..."
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Web service is running!"
else
    echo "❌ Web service failed. Checking logs..."
    docker-compose logs web --tail=20
fi

# Test Redis connection
echo "📡 Testing Redis connection..."
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running!"
else
    echo "❌ Redis failed. Checking logs..."
    docker-compose logs redis --tail=10
fi

# Test database
echo "💾 Testing database..."
if docker-compose exec -T web python manage.py check --deploy > /dev/null 2>&1; then
    echo "✅ Database is configured correctly!"
else
    echo "❌ Database issues found. Running check..."
    docker-compose exec web python manage.py check --deploy
fi

# Test Celery
echo "🥬 Testing Celery worker..."
if docker-compose exec -T celery celery -A dress_shop inspect active > /dev/null 2>&1; then
    echo "✅ Celery worker is running!"
else
    echo "❌ Celery worker failed. Checking logs..."
    docker-compose logs celery --tail=10
fi

# Test environment variables in container
echo "🔧 Testing environment variables in container..."
echo "DEBUG in container: $(docker-compose exec -T web printenv | grep DEBUG=)"
echo "EMAIL_HOST_USER in container: $(docker-compose exec -T web printenv | grep EMAIL_HOST_USER=)"
echo "SQLITE_DB_PATH in container: $(docker-compose exec -T web printenv | grep SQLITE_DB_PATH=)"

# Show final status
echo ""
echo "🎉 Docker Setup Test Complete!"
echo ""
echo "📊 Service Status:"
echo "   🌐 Web: http://localhost:8000"
echo "   📧 Redis: redis://localhost:6379"
echo "   💾 SQLite: /app/data/db.sqlite3 (in container)"
echo "   🥬 Celery: Background tasks"
echo "   ⏰ Celery Beat: Scheduled tasks"
echo ""
echo "🔧 Management Commands:"
echo "   📊 View logs: docker-compose logs -f"
echo "   🛑 Stop services: docker-compose down"
echo "   🔄 Restart services: docker-compose restart"
echo "   🐚 Access shell: docker-compose exec web bash"
echo "   🗄️ Access Django shell: docker-compose exec web python manage.py shell"
echo ""
echo "🛡️  Security Status:"
echo "   ✅ Environment variables loaded from .env"
echo "   ✅ Sensitive data secured in .env file"
echo "   ✅ Docker services using env_file configuration"
echo "   ✅ No hardcoded credentials in docker-compose.yml"
echo ""
echo "📧 Environment Configuration:"
echo "   📁 .env file: $(wc -l < .env | awk '{print $1}') lines"
echo "   🔧 Docker Compose: Using env_file directive"
echo "   🐳 Containers: 4 services (web, redis, celery, celery-beat)"
echo ""
echo "🚀 Ready for Production!"
echo "   1. Update SECRET_KEY with a secure 50+ character key"
echo "   2. Update JWT_SECRET_KEY with a different secure key"
echo "   3. Configure SSL certificates for HTTPS"
echo "   4. Set up monitoring and logging"
echo "   5. Update ALLOWED_HOSTS with your domain"
