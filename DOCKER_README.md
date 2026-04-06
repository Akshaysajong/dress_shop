# Docker Deployment Guide

## 🐳 Docker Setup for Django Dress Shop

### Prerequisites
- Docker installed
- Docker Compose installed
- Git (for cloning)

### Quick Start

1. **Clone and Setup**
   ```bash
   git clone <your-repo-url>
   cd dress_shop
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Deploy with Script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Manual Deployment

1. **Build and Start**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

2. **Run Migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Collect Static Files**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### Services

- **Web Server**: http://localhost:8000
- **Database**: PostgreSQL on port 5432
- **Redis**: Redis on port 6379
- **Celery Worker**: Background tasks
- **Celery Beat**: Scheduled tasks

### Docker Compose Services

| Service | Description | Port |
|---------|-------------|------|
| web | Django application | 8000 |
| db | PostgreSQL database | 5432 |
| redis | Redis cache/message broker | 6379 |
| celery | Celery worker | - |
| celery-beat | Celery scheduler | - |

### Useful Commands

```bash
# View logs
docker-compose logs -f web

# View all services
docker-compose ps

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose up -d --build web

# Access Django shell
docker-compose exec web python manage.py shell

# Access database
docker-compose exec db psql -U postgres -d dress_shop_db
```

### Environment Variables

Key variables in `.env`:
- `DEBUG`: Set to False in production
- `SECRET_KEY`: Generate a secure key
- `DATABASE_URL`: PostgreSQL connection string
- `CELERY_BROKER_URL`: Redis connection string
- `EMAIL_*`: Email configuration for notifications

### Production Considerations

1. **Security**
   - Change default passwords
   - Use strong SECRET_KEY
   - Set DEBUG=False
   - Configure proper ALLOWED_HOSTS

2. **Performance**
   - Use PostgreSQL for production
   - Configure Redis persistence
   - Set up proper logging
   - Monitor container resources

3. **Backup**
   - Backup database regularly
   - Backup media files
   - Version control your code

### Troubleshooting

**Database Connection Issues**
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# Reset database
docker-compose down -v
docker-compose up -d db
sleep 10
docker-compose exec web python manage.py migrate
```

**Celery Issues**
```bash
# Check Celery logs
docker-compose logs celery

# Restart Celery
docker-compose restart celery celery-beat
```

**Static Files Issues**
```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput --clear
```

### Scaling

To scale the web service:
```bash
docker-compose up -d --scale web=3
```

This will run 3 instances of the Django application behind a load balancer.
