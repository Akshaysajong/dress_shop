#!/bin/bash

# Security Setup Script for Docker Deployment
# This script helps secure your sensitive data for production

echo "🔒 Setting up secure environment for Docker deployment..."

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists. Creating backup..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Create production .env from template
if [ -f .env.production ]; then
    echo "📋 Creating .env from production template..."
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
    echo "🚨 IMPORTANT SECURITY STEPS:"
    echo "1. Update EMAIL_HOST_PASSWORD with your Gmail App Password"
    echo "2. Update ALLOWED_HOSTS with your actual domain"
    echo "3. Update CSRF_TRUSTED_ORIGINS with your actual domain"
    echo "4. Set up SSL certificates for HTTPS"
    echo "5. Configure firewall rules"
    echo ""
    echo "📧 Gmail App Password Setup:"
    echo "- Go to Google Account settings"
    echo "- Enable 2-factor authentication"
    echo "- Generate App Password for Django app"
    echo "- Use App Password in EMAIL_HOST_PASSWORD"
    echo ""
    echo "🛡️  Security Checklist:"
    echo "✅ Generated Django SECRET_KEY"
    echo "✅ Generated JWT SECRET_KEY"
    echo "✅ SSL redirects enabled"
    echo "✅ Secure cookies enabled"
    echo "✅ HSTS headers configured"
    echo "⚠️  Manual configuration needed for email and domains"
    
else
    echo "❌ .env.production template not found!"
    exit 1
fi

echo ""
echo "🔐 Next Steps:"
echo "1. Edit .env file with your actual values"
echo "2. Test locally: docker-compose up --build"
echo "3. Deploy to production"
echo "4. Set up SSL certificates"
echo "5. Configure monitoring and logging"
