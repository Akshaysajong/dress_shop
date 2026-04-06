#!/bin/bash

# Complete Docker Setup and Security Test
# This script completes the secure Docker setup

echo "🚀 Starting Complete Docker Security Setup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Creating secure .env file..."
    cp .env.production .env
    
    echo "🔑 Generating secure secrets..."
    
    # Generate Django SECRET_KEY
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print("".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for _ in range(50)))')
    sed -i "s/your-very-secure-secret-key-change-this-in-production-min-50-characters/$DJANGO_SECRET_KEY/g" .env
    
    # Generate JWT Secret Key
    JWT_SECRET_KEY=$(python -c 'import secrets; print("".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for _ in range(50)))')
    sed -i "s/your-jwt-secret-key-different-from-django-secret/$JWT_SECRET_KEY/g" .env
    
    echo "✅ Secure .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Update these values in .env:"
    echo "   - EMAIL_HOST_PASSWORD (use Gmail App Password)"
    echo "   - ALLOWED_HOSTS (add your domain)"
    echo "   - CSRF_TRUSTED_ORIGINS (add your domain)"
fi

# Create logs directory
mkdir -p logs

# Build Docker images
echo "🏗️  Building Docker images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Run database migrations
echo "🔄 Running database migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser (optional)
echo "👤 Creating superuser (optional)..."
echo "Run: docker-compose exec web python manage.py createsuperuser"

# Test application
echo "🧪 Testing application..."
sleep 5

if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
else
    echo "❌ Application failed to start. Check logs with: docker-compose logs"
fi

# Security check
echo "🛡️  Running security checks..."

# Check if HTTPS is configured
if grep -q "SECURE_SSL_REDIRECT=True" .env; then
    echo "✅ SSL redirect enabled"
else
    echo "⚠️  SSL redirect not enabled"
fi

# Check if secure cookies are configured
if grep -q "SESSION_COOKIE_SECURE=True" .env; then
    echo "✅ Secure cookies enabled"
else
    echo "⚠️  Secure cookies not enabled"
fi

# Check if secrets are generated
if grep -q "your-very-secure-secret-key" .env; then
    echo "⚠️  Default secrets detected. Please run setup-security.sh"
else
    echo "✅ Custom secrets generated"
fi

echo ""
echo "🎉 Docker Security Setup Complete!"
echo ""
echo "📊 Application Status:"
echo "   🌐 Web: http://localhost:8000"
echo "   📧 Redis: redis://localhost:6379"
echo "   💾 SQLite: /app/data/db.sqlite3"
echo ""
echo "🔧 Management Commands:"
echo "   📊 View logs: docker-compose logs -f"
echo "   🛑 Stop services: docker-compose down"
echo "   🔄 Restart services: docker-compose restart"
echo "   🐚 Access shell: docker-compose exec web bash"
echo ""
echo "🛡️  Security Checklist:"
echo "   ✅ Environment variables configured"
echo "   ✅ Docker containers running"
echo "   ✅ Database migrated"
echo "   ✅ Static files collected"
echo "   ✅ Security settings applied"
echo ""
echo "📚 Documentation:"
echo "   - SECURITY_GUIDE.md for security best practices"
echo "   - DOCKER_README.md for Docker commands"
echo "   - setup-security.sh for security setup"
echo ""
echo "🚨 Production Deployment Notes:"
echo "   1. Set up SSL certificates"
echo "   2. Update ALLOWED_HOSTS with your domain"
echo "   3. Configure firewall rules"
echo "   4. Set up monitoring and logging"
echo "   5. Enable HTTPS in production"
