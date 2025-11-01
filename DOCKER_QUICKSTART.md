# 🚀 MadeInPK Docker Quick Reference

## ⚡ Quick Start (3 Commands)

```bash
# 1. Build the Docker image
docker-compose build

# 2. Start all services (includes auto-setup & populate_db)
docker-compose up -d

# 3. Check logs
docker-compose logs -f
```

**That's it!** Your app is now running at http://localhost:8000

---

## 📊 Access Your App

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000/api/ | - |
| **Admin Panel** | http://localhost:8000/admin/ | admin / admin123 |
| **WebSocket** | ws://localhost:8000/ws/ | - |
| **PostgreSQL** | localhost:5432 | postgres / postgres123 |
| **Redis** | localhost:6379 | - |

---

## 🎯 Using Makefile (Recommended)

If you have `make` installed, use these shortcuts:

```bash
make build          # Build images
make up             # Start services
make down           # Stop services
make logs           # View all logs
make logs-web       # View web logs only
make shell          # Open Django shell
make bash           # Open bash in container
make migrate        # Run migrations
make populate-db    # Re-run populate_db
make clean          # Remove everything
make rebuild        # Clean rebuild
```

---

## 🛠️ Common Tasks

### View Logs
```bash
docker-compose logs -f              # All services
docker-compose logs -f web          # Web only
docker-compose logs -f celery_worker # Celery only
```

### Run Django Commands
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py populate_db
docker-compose exec web python manage.py shell
```

### Access Containers
```bash
docker-compose exec web bash                    # Web container
docker-compose exec db psql -U postgres -d madeinpk_db  # Database
docker-compose exec redis redis-cli             # Redis
```

### Restart Services
```bash
docker-compose restart web          # Restart web only
docker-compose restart              # Restart all
```

### Stop Everything
```bash
docker-compose down                 # Stop services
docker-compose down -v              # Stop and delete data
```

---

## 🔄 What Runs on Startup?

The `docker-entrypoint.sh` automatically:

1. ✅ Waits for PostgreSQL and Redis to be ready
2. ✅ Runs `python manage.py migrate`
3. ✅ Runs `python manage.py collectstatic`
4. ✅ Creates superuser (admin/admin123)
5. ✅ **Runs `python manage.py populate_db`** ← Your command!
6. ✅ Starts the application

---

## 🐛 Troubleshooting

### Services won't start?
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use?
Edit `docker-compose.yml` and change:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Check service health
```bash
docker-compose ps
docker-compose logs db
docker-compose logs redis
```

---

## 📦 Services Running

| Container | Service | Port | Purpose |
|-----------|---------|------|---------|
| `madeinpk_web` | Django/Daphne | 8000 | HTTP + WebSocket |
| `madeinpk_celery_worker` | Celery Worker | - | Background tasks |
| `madeinpk_celery_beat` | Celery Beat | - | Scheduled tasks |
| `madeinpk_db` | PostgreSQL | 5432 | Database |
| `madeinpk_redis` | Redis | 6379 | Cache + Broker |

---

## 💾 Data Persistence

Data is stored in Docker volumes:
- `postgres_data` - Database files
- `static_volume` - Static files  
- `media_volume` - Uploaded images

To completely remove all data:
```bash
docker-compose down -v
```

---

## 🚢 Next Steps

1. **Access Admin Panel**: http://localhost:8000/admin/ (admin/admin123)
2. **Explore API**: http://localhost:8000/api/
3. **Check Sample Data**: The `populate_db` command created sample users, products, auctions, etc.
4. **Test WebSocket**: Connect to ws://localhost:8000/ws/

---

## 📚 Full Documentation

For complete details, see `DOCKER_GUIDE.md`
