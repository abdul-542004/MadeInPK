#!/bin/bash

# MadeInPK Backend Start Script
# This script starts all required services for the backend

echo "🚀 Starting MadeInPK Backend Services..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Using default configuration..."
fi

# Activate virtual environment
source venv/bin/activate

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null && ! ss -tlnp | grep -q ":6379 "; then
    echo "⚠️  Redis is not running!"
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
else
    echo "✅ Redis is already running"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo "✅ Virtual environment activated"
echo ""
echo "Starting services in background..."
echo ""

# Start Celery Worker
echo "📦 Starting Celery Worker..."
celery -A MadeInPK worker --loglevel=info --logfile=logs/celery_worker.log &
CELERY_WORKER_PID=$!
echo "   PID: $CELERY_WORKER_PID"

# Start Celery Beat
echo "⏰ Starting Celery Beat..."
celery -A MadeInPK beat --loglevel=info --logfile=logs/celery_beat.log &
CELERY_BEAT_PID=$!
echo "   PID: $CELERY_BEAT_PID"

# Start Stripe Webhook Listener
echo "💳 Starting Stripe Webhook Listener..."
stripe listen --forward-to localhost:8000/api/stripe/webhook/ --log-level info > logs/stripe_webhook.log 2>&1 &
STRIPE_WEBHOOK_PID=$!
echo "   PID: $STRIPE_WEBHOOK_PID"

# Give Celery services time to start
sleep 3

# Start Daphne ASGI Server (with WebSocket support)
echo "🌐 Starting Daphne ASGI Server on http://localhost:8000..."
echo ""
daphne -b 0.0.0.0 -p 8000 MadeInPK.asgi:application

# This line will only execute if Daphne is stopped (Ctrl+C)
echo ""
echo "🛑 Daphne stopped. Cleaning up background services..."

# Kill Celery processes
kill $CELERY_WORKER_PID 2>/dev/null
kill $CELERY_BEAT_PID 2>/dev/null
kill $STRIPE_WEBHOOK_PID 2>/dev/null

echo "✅ All services stopped"


echo "
# Terminal 1: ASGI Server (for WebSockets)
cd MadeInPK
daphne -p 8000 MadeInPK.asgi:application

# Terminal 2: Celery Worker
celery -A MadeInPK worker --loglevel=info

# Terminal 3: Celery Beat
celery -A MadeInPK beat --loglevel=info

# Terminal 4: Redis
redis-server

# Terminal 5: Stripe Webhook Listener
stripe listen --forward-to localhost:8000/api/stripe/webhook/"

