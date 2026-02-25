# Automated Data Pipeline Guide

This guide covers the automated congressional trading data collection system.

## Overview

The data pipeline automatically scrapes trading data from:
- **Senate**: efdsearch.senate.gov (Periodic Transaction Reports)
- **House**: disclosures.house.gov (Financial Disclosure Forms)

Data is validated, cleaned, and imported into the database with duplicate detection.

## Components

### 1. Scrapers

#### Senate Scraper (`app/scrapers/senate_scraper.py`)
```python
from app.scrapers import SenateScraper

with SenateScraper(headless=True) as scraper:
    transactions = scraper.scrape_recent_transactions(days_back=7)
```

**Features:**
- Selenium-based web scraping
- Handles JavaScript-rendered content
- Automatic agreement acceptance
- Date range filtering
- Individual report parsing

#### House Scraper (`app/scrapers/house_scraper.py`)
```python
from app.scrapers import HouseScraper

with HouseScraper(headless=True) as scraper:
    transactions = scraper.scrape_recent_transactions(days_back=7)
```

**Features:**
- Periodic Transaction Report filtering
- Quarterly data collection
- PDF and HTML report handling
- Rate limiting (configurable delay)

### 2. Data Validator (`app/scrapers/data_validator.py`)

```python
from app.scrapers import DataValidator

validator = DataValidator()

# Validate single transaction
is_valid, error = validator.validate_transaction(transaction)

# Validate batch
valid, invalid = validator.validate_batch(transactions)
```

**Validation Features:**
- Ticker symbol normalization
- Amount range parsing (`"$1,001 - $15,000"` → min/max)
- Duplicate detection (per politician, ticker, date, type)
- Date validation
- Name normalization
- Transaction type validation

**Ticker Normalization:**
- Converts to uppercase
- Applies known corrections (e.g., FB → META)
- Filters invalid tickers (LLC, INC, etc.)
- Validates format (1-5 letters, optional .A/.B)

### 3. Database Models

#### DataSource Model (`app/models/data_source.py`)
Tracks each scraping run:
```python
class DataSource:
    source_type: str       # 'senate' or 'house'
    status: str           # 'running', 'completed', 'failed'
    records_found: int
    records_imported: int
    records_skipped: int
    records_invalid: int
    error_message: str
    metadata: dict        # Additional info (year, days_back, etc.)
    started_at: datetime
    completed_at: datetime
```

#### Trade Model (Extended)
Already includes:
- `source_url`: URL of disclosure
- `raw_data`: Original scraped data (JSONB)
- Unique constraint to prevent duplicates

### 4. Celery Tasks (`app/tasks/scraping_tasks.py`)

#### Daily Senate Scraping
```python
from app.tasks.scraping_tasks import scrape_senate_daily

# Trigger manually
result = scrape_senate_daily.delay(days_back=7)

# Scheduled: Daily at 6:00 AM EST
```

#### Daily House Scraping
```python
from app.tasks.scraping_tasks import scrape_house_daily

# Trigger manually
result = scrape_house_daily.delay(days_back=7)

# Scheduled: Daily at 6:30 AM EST
```

#### Combined Scraping
```python
from app.tasks.scraping_tasks import scrape_all_daily

# Scrape both in parallel
result = scrape_all_daily.delay(days_back=7)
```

**Task Features:**
- Automatic retry (3 attempts)
- Exponential backoff
- Error logging
- Progress tracking in DataSource model
- Alert on failure (3rd retry)

### 5. Historical Backfill (`scripts/backfill_historical.py`)

Load historical data from 2012 to present:

```bash
# Full backfill (2012-2024)
python scripts/backfill_historical.py

# Specific year range
python scripts/backfill_historical.py --start-year 2020 --end-year 2024

# Senate only
python scripts/backfill_historical.py --senate-only

# House only
python scripts/backfill_historical.py --house-only

# Resume from checkpoint
python scripts/backfill_historical.py --resume
```

**Features:**
- Progress tracking (saves checkpoint)
- Can resume if interrupted
- Processes data quarterly to avoid timeouts
- Automatic duplicate detection
- Comprehensive logging

**Checkpoint File:** `scripts/backfill_checkpoint.json`
```json
{
  "senate": {
    "completed_years": [2012, 2013, 2014],
    "current_year": 2015
  },
  "house": {
    "completed_years": [2012, 2013],
    "current_year": 2014
  },
  "total_records": 45000,
  "total_imported": 42500
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd quant/backend
pip install -r requirements.txt
```

Required packages:
- `selenium>=4.22.0`
- `beautifulsoup4>=4.12.3`
- `webdriver-manager>=4.0.1`
- `celery>=5.4.0`
- `redis>=5.0.7`

### 2. Install Chrome/Chromium

For headless scraping:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# macOS
brew install chromium
```

### 3. Setup Redis

Celery requires Redis for task queue:

```bash
# Install Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

Update `.env`:
```env
REDIS_URL=redis://localhost:6379/0
```

### 4. Run Database Migration

```bash
cd quant/backend
alembic upgrade head
```

This creates the `data_sources` table.

### 5. Start Celery

```bash
# Start worker and beat scheduler
./scripts/start_celery.sh

# Or manually:
# Worker
celery -A app.tasks.scraping_tasks worker --loglevel=info

# Beat scheduler (in separate terminal)
celery -A app.tasks.scraping_tasks beat --loglevel=info
```

### 6. Run Historical Backfill (Optional)

```bash
# Start with recent years first
python scripts/backfill_historical.py --start-year 2022 --end-year 2024

# Then backfill older data
python scripts/backfill_historical.py --start-year 2012 --end-year 2021 --resume
```

## Usage

### Manual Scraping

```python
from app.tasks.scraping_tasks import scrape_senate_daily, scrape_house_daily

# Scrape last 7 days
senate_result = scrape_senate_daily.delay(7)
house_result = scrape_house_daily.delay(7)

# Get results
print(senate_result.get())
# {
#   "success": True,
#   "source": "senate",
#   "records_found": 150,
#   "records_imported": 142,
#   "records_skipped": 5,
#   "records_invalid": 3
# }
```

### Scheduled Tasks

Tasks run automatically via Celery Beat:

- **Senate**: Daily at 6:00 AM EST
- **House**: Daily at 6:30 AM EST

Schedule is configured in `app/tasks/scraping_tasks.py`:
```python
celery_app.conf.beat_schedule = {
    'scrape-senate-daily': {
        'task': 'scrape_senate_daily',
        'schedule': crontab(hour=6, minute=0),
        'args': (7,)
    },
    'scrape-house-daily': {
        'task': 'scrape_house_daily',
        'schedule': crontab(hour=6, minute=30),
        'args': (7,)
    },
}
```

### Monitor Scraping Runs

Query DataSource model:

```python
from app.models import DataSource
from sqlalchemy import select

# Get recent runs
stmt = select(DataSource).order_by(DataSource.run_date.desc()).limit(10)
recent_runs = await session.execute(stmt)

for run in recent_runs.scalars():
    print(f"{run.source_type} - {run.status}: {run.records_imported} imported")
```

## Rate Limiting

Both scrapers include rate limiting to avoid being blocked:

```python
# Default: 2 seconds between requests
scraper = SenateScraper(rate_limit_delay=2.0)

# More conservative for backfill
scraper = SenateScraper(rate_limit_delay=5.0)
```

## Error Handling

### Retry Logic

Tasks automatically retry on failure:
- **Max retries**: 3
- **Backoff**: Exponential (1s, 2s, 4s)
- **Jitter**: Randomized to avoid thundering herd

### Error Logging

All errors are logged to:
- `logs/celery_worker.log`
- `logs/celery_beat.log`
- `backfill.log` (for backfill script)

### Alerts

On 3rd retry failure, alerts are sent via `app.core.alerts.send_alert()`.

## Data Flow

```
1. Scraper → Raw HTML/JSON
2. Parser → Extract transactions
3. Validator → Clean & validate
4. Database → Import (with duplicate check)
5. DataSource → Track statistics
```

## Performance Tips

1. **Use headless mode** for faster scraping:
   ```python
   scraper = SenateScraper(headless=True)
   ```

2. **Adjust rate limiting** based on server response:
   - Increase delay if getting 429 errors
   - Decrease for faster scraping (with caution)

3. **Run backfill in chunks**:
   - Process 1-2 years at a time
   - Use `--resume` to continue

4. **Monitor database size**:
   - Raw data stored in JSONB can grow large
   - Consider archiving old raw_data

## Troubleshooting

### Selenium Issues

**Error**: "ChromeDriver not found"
```bash
# Install webdriver-manager will auto-download
pip install webdriver-manager

# Or install manually
# Ubuntu
sudo apt-get install chromium-chromedriver
```

**Error**: "Chrome binary not found"
```python
# Specify chrome binary path
chrome_options.binary_location = "/usr/bin/chromium-browser"
```

### Celery Issues

**Error**: "Broker connection error"
```bash
# Check Redis is running
redis-cli ping
# Should return "PONG"

# Start Redis
redis-server
```

**Error**: "Task not found"
```bash
# Restart Celery worker
pkill -f 'celery worker'
celery -A app.tasks.scraping_tasks worker --loglevel=info
```

### Scraping Issues

**No data found**:
- Check if website structure changed
- Verify date range is valid
- Increase timeout values

**Duplicate detection false positives**:
- Reset validator between batches:
  ```python
  validator.reset_duplicate_tracking()
  ```

## Monitoring Dashboard

View scraping statistics:

```python
# Get success rate
from sqlalchemy import func

stmt = select(
    DataSource.source_type,
    func.count(DataSource.id).label('total_runs'),
    func.sum(
        case((DataSource.status == 'completed', 1), else_=0)
    ).label('successful_runs')
).group_by(DataSource.source_type)

results = await session.execute(stmt)
```

## API Endpoints (Future)

Planned endpoints for monitoring:

- `GET /api/admin/scraping/status` - Current status
- `GET /api/admin/scraping/history` - Recent runs
- `POST /api/admin/scraping/trigger` - Manual trigger
- `GET /api/admin/scraping/stats` - Statistics

## Best Practices

1. **Test with small date ranges first**
2. **Monitor logs during initial runs**
3. **Use resume feature for large backfills**
4. **Keep rate limits reasonable**
5. **Review invalid transactions periodically**
6. **Update ticker corrections as needed**

## Support

For issues or questions:
1. Check logs first
2. Review DataSource records
3. Test scrapers individually
4. Check website structure changes

## Next Steps

1. ✅ Set up Redis
2. ✅ Run database migration
3. ✅ Start Celery
4. ✅ Test manual scraping
5. ✅ Run small backfill test
6. ✅ Monitor scheduled tasks
7. ✅ Review and adjust settings
