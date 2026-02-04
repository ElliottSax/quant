# Quick Start: Automated Data Pipeline

Get the congressional trading data pipeline running in 5 minutes.

## Prerequisites

- Python 3.10+
- PostgreSQL database
- Chrome/Chromium browser

## 1. Install Dependencies (1 min)

```bash
cd quant/backend

# Install Python packages
pip install -r requirements.txt

# Install Chrome (if not installed)
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# macOS
brew install chromium
```

## 2. Setup Redis (1 min)

```bash
# Install Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server &

# Verify
redis-cli ping  # Should return "PONG"
```

Update `.env`:
```env
REDIS_URL=redis://localhost:6379/0
```

## 3. Run Database Migration (30 sec)

```bash
# Create data_sources table
alembic upgrade head
```

## 4. Test Setup (1 min)

```bash
# Quick test (no internet required)
python scripts/test_scraping.py
```

Expected output:
```
Testing Data Validator
✓ AAPL → AAPL
✓ FB → META
✓ Valid transaction: True
✓ Validator test PASSED

Testing Database Import
✓ Created DataSource record
✓ Fetched DataSource record
✓ Database import test PASSED
```

## 5. Start Celery (30 sec)

```bash
# Start worker and scheduler
./scripts/start_celery.sh

# Or manually in separate terminals:
# Terminal 1:
celery -A app.tasks.scraping_tasks worker --loglevel=info

# Terminal 2:
celery -A app.tasks.scraping_tasks beat --loglevel=info
```

## 6. Trigger Manual Scrape (1 min)

```python
# Python shell
from app.tasks.scraping_tasks import scrape_senate_daily

# Scrape last 3 days (quick test)
result = scrape_senate_daily.delay(3)

# Wait for result
print(result.get(timeout=120))
# {
#   "success": True,
#   "source": "senate",
#   "records_found": 50,
#   "records_imported": 45,
#   ...
# }
```

## 7. Optional: Run Backfill

```bash
# Start with recent data (2023-2024)
python scripts/backfill_historical.py --start-year 2023 --end-year 2024

# Monitor progress
tail -f backfill.log
```

## That's It!

The pipeline is now running:
- **Automatic scraping**: Daily at 6 AM EST
- **Data validation**: Automatic
- **Duplicate detection**: Built-in
- **Error handling**: 3 retries with backoff

## Verify It's Working

```python
# Check recent runs
from app.models import DataSource
from sqlalchemy import select

stmt = select(DataSource).order_by(DataSource.run_date.desc()).limit(5)
recent_runs = await session.execute(stmt)

for run in recent_runs.scalars():
    print(f"{run.source_type} - {run.status}: {run.records_imported} imported")
```

## Monitor Logs

```bash
# Celery worker
tail -f logs/celery_worker.log

# Celery scheduler
tail -f logs/celery_beat.log

# Backfill
tail -f backfill.log
```

## Troubleshooting

### Redis not running?
```bash
redis-server &
redis-cli ping  # Should return "PONG"
```

### Celery not finding tasks?
```bash
# Restart worker
pkill -f 'celery worker'
celery -A app.tasks.scraping_tasks worker --loglevel=info
```

### Chrome/Selenium errors?
```bash
# Install webdriver-manager
pip install webdriver-manager

# Or specify chrome path in scraper
```

### No data found?
- Check internet connection
- Verify date range is valid
- Try with longer days_back parameter
- Check logs for errors

## Next Steps

1. ✅ Setup complete - pipeline is running
2. Monitor first few runs
3. Adjust rate limits if needed
4. Run full backfill when ready
5. Review data quality

## Full Documentation

For detailed information, see:
- `DATA_PIPELINE_GUIDE.md` - Complete guide
- `TASK_11_AUTOMATED_DATA_PIPELINE.md` - Implementation details

## Support

Check logs first:
- `logs/celery_worker.log`
- `logs/celery_beat.log`
- `backfill.log`

Then review DataSource records for statistics.
