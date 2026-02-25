#!/bin/bash
# Start Celery worker and beat scheduler for scraping tasks

echo "Starting Celery worker and beat scheduler..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A app.tasks.scraping_tasks worker \
    --loglevel=info \
    --logfile=logs/celery_worker.log \
    --detach

# Wait a moment
sleep 2

# Start Celery beat scheduler in background
echo "Starting Celery beat scheduler..."
celery -A app.tasks.scraping_tasks beat \
    --loglevel=info \
    --logfile=logs/celery_beat.log \
    --detach

echo "Celery started!"
echo "Worker log: logs/celery_worker.log"
echo "Beat log: logs/celery_beat.log"
echo ""
echo "To stop Celery:"
echo "  pkill -f 'celery worker'"
echo "  pkill -f 'celery beat'"
