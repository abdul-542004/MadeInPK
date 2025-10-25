#!/bin/bash

# MadeInPK Backend Quick Setup Script

echo "🚀 Starting MadeInPK Backend Setup..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual credentials"
fi

# Navigate to Django project
cd MadeInPK

# Run migrations
echo "🗄️  Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser prompt
echo ""
read -p "👤 Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python manage.py createsuperuser
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  cd MadeInPK"
echo "  python manage.py runserver"
echo ""
echo "To start Celery worker:"
echo "  celery -A MadeInPK worker --loglevel=info"
echo ""
echo "To start Celery beat:"
echo "  celery -A MadeInPK beat --loglevel=info"
echo ""
echo "Don't forget to start Redis server!"
