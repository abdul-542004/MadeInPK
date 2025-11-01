#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting MadeInPK Docker Entrypoint..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  sleep 1
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! redis-cli -h redis ping > /dev/null 2>&1; do
  sleep 1
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist (optional)
echo "👤 Creating superuser (if needed)..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: username=admin, password=admin123')
else:
    print('ℹ️  Superuser already exists')
END

# Populate database with sample data (only for web service)
# Check if we're running the web service (not celery)
if [[ "$@" == *"daphne"* ]]; then
    echo "🌱 Populating database with sample data..."
    python manage.py populate_db
fi

echo "✅ Setup complete! Starting application..."
echo ""

# Execute the main command (passed as arguments to this script)
exec "$@"
