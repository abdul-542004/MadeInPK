# MadeInPK Docker Setup Guide

This guide explains how to build and run the MadeInPK Django application using Docker.

## 📋 Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

Check your versions:
```bash
docker --version
docker-compose --version
```

## 🏗️ Architecture

The Docker setup includes the following services:

1. **PostgreSQL Database** (`db`) - Stores all application data
2. **Redis** (`redis`) - Message broker for Celery and Channels layer for WebSockets
3. **Django Web Application** (`web`) - Runs Daphne ASGI server for HTTP and WebSocket requests
4. **Celery Worker** (`celery_worker`) - Processes background tasks
5. **Celery Beat** (`celery_beat`) - Periodic task scheduler

## 🚀 Quick Start

### 1. Build the Docker Image

Build all services defined in docker-compose.yml:

```bash
docker-compose build
```

Or build just the web service:
```bash
docker-compose build web
```

### 2. Start All Services

Start all containers in detached mode:

```bash
docker-compose up -d
```

This will:
- ✅ Start PostgreSQL and Redis
- ✅ Wait for database to be ready
- ✅ Run database migrations (`python manage.py migrate`)
- ✅ Collect static files
- ✅ Create a superuser (username: `admin`, password: `admin123`)
- ✅ **Run the `populate_db` management command** to seed initial data
- ✅ Start all services

### 3. View Logs

View logs from all services:
```bash
docker-compose logs -f
```

View logs from a specific service:
```bash
docker-compose logs -f web
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
```

### 4. Access the Application

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
  - Username: `admin`
  - Password: `admin123`
- **WebSocket**: ws://localhost:8000/ws/

### 5. Stop Services

Stop all services:
```bash
docker-compose down
```

Stop and remove volumes (⚠️ this will delete all data):
```bash
docker-compose down -v
```

## 🔧 Common Commands

### Execute Django Management Commands

Run any Django management command in the web container:

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Populate database (already runs on startup)
docker-compose exec web python manage.py populate_db

# Open Django shell
docker-compose exec web python manage.py shell
```

### Access Container Shell

Access bash shell in the web container:
```bash
docker-compose exec web bash
```

Access PostgreSQL:
```bash
docker-compose exec db psql -U postgres -d madeinpk_db
```

Access Redis CLI:
```bash
docker-compose exec redis redis-cli
```

### Restart a Service

Restart a specific service:
```bash
docker-compose restart web
docker-compose restart celery_worker
```

### View Running Containers

```bash
docker-compose ps
```

### Rebuild and Restart

If you make changes to code or requirements:
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## 🔐 Environment Variables

The docker-compose.yml includes these environment variables. You can modify them:

```yaml
environment:
  - DEBUG=True
  - SECRET_KEY=your-secret-key
  - ALLOWED_HOSTS=localhost,127.0.0.1,web
  - DB_NAME=madeinpk_db
  - DB_USER=postgres
  - DB_PASSWORD=postgres123
  - DB_HOST=db
  - DB_PORT=5432
  - REDIS_URL=redis://redis:6379/0
```

For production, create a `.env` file and reference it in docker-compose.yml:

```yaml
env_file:
  - .env
```

## 📦 What Happens on Startup?

The `docker-entrypoint.sh` script runs these steps automatically:

1. **Wait for PostgreSQL** - Ensures database is ready
2. **Wait for Redis** - Ensures Redis is ready
3. **Run Migrations** - `python manage.py migrate --noinput`
4. **Collect Static Files** - `python manage.py collectstatic --noinput`
5. **Create Superuser** - Creates admin user if it doesn't exist
6. **Populate Database** - `python manage.py populate_db` (seeds sample data)
7. **Start Application** - Runs the main command (Daphne, Celery, etc.)

## 🗂️ Data Persistence

Docker volumes are used to persist data:

- `postgres_data` - PostgreSQL database files
- `static_volume` - Collected static files
- `media_volume` - Uploaded media files (product images)

## 🐛 Troubleshooting

### Database Connection Error

If you see database connection errors:
```bash
docker-compose down
docker-compose up -d db
# Wait a few seconds
docker-compose up -d
```

### Port Already in Use

If port 8000, 5432, or 6379 is already in use, change it in docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### View All Logs

```bash
docker-compose logs --tail=100
```

### Clean Everything and Start Fresh

```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Remove Docker images
docker-compose rm -f

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Check Service Health

```bash
# Check if services are healthy
docker-compose ps

# Check specific service logs
docker-compose logs db
docker-compose logs redis
```

## 🚢 Production Deployment

For production deployment:

1. **Set DEBUG=False** in environment variables
2. **Use strong SECRET_KEY**
3. **Use secure database password**
4. **Configure ALLOWED_HOSTS** properly
5. **Use environment file** for secrets
6. **Add Nginx** as reverse proxy
7. **Use Docker secrets** for sensitive data
8. **Set up SSL/TLS** certificates
9. **Configure backup strategy** for volumes
10. **Set up monitoring and logging**

Example production setup with Nginx:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Channels Documentation](https://channels.readthedocs.io/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 🆘 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Check PostgreSQL: `docker-compose exec db pg_isready -U postgres`
4. Check Redis: `docker-compose exec redis redis-cli ping`
