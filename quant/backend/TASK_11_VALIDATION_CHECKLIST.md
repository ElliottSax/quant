# Task #11 Validation Checklist

## Pre-Deployment Checklist

### ✅ Code Implementation

- [x] Senate scraper created (`app/scrapers/senate_scraper.py`)
- [x] House scraper created (`app/scrapers/house_scraper.py`)
- [x] Data validator created (`app/scrapers/data_validator.py`)
- [x] Celery tasks created (`app/tasks/scraping_tasks.py`)
- [x] Historical backfill script (`scripts/backfill_historical.py`)
- [x] DataSource model created (`app/models/data_source.py`)
- [x] Database migration created (`alembic/versions/007_add_data_source_table.py`)

### ✅ Features Implemented

**Senate Scraper:**
- [x] Scrapes efdsearch.senate.gov
- [x] Selenium WebDriver integration
- [x] Agreement acceptance automation
- [x] Date range filtering
- [x] Individual report parsing
- [x] Ticker extraction
- [x] Transaction type detection
- [x] Amount range parsing
- [x] Date extraction
- [x] Error handling
- [x] Rate limiting

**House Scraper:**
- [x] Scrapes disclosures.house.gov
- [x] PTR filtering
- [x] Year-based search
- [x] HTML report parsing
- [x] PDF detection (skip for now)
- [x] Ticker extraction
- [x] Transaction type detection
- [x] Amount range parsing
- [x] Date extraction
- [x] Error handling
- [x] Rate limiting

**Data Validator:**
- [x] Ticker normalization
- [x] Ticker validation
- [x] Ticker corrections (FB→META)
- [x] Invalid ticker filtering
- [x] Amount range parsing
- [x] Date validation
- [x] Name normalization
- [x] Duplicate detection
- [x] Batch validation
- [x] Statistics tracking

**Celery Tasks:**
- [x] scrape_senate_daily task
- [x] scrape_house_daily task
- [x] scrape_all_daily task
- [x] Automatic retry (3 attempts)
- [x] Exponential backoff
- [x] Error handling
- [x] DataSource tracking
- [x] Alert on failure
- [x] Celery Beat schedule (6 AM EST)
- [x] Task timeout (1 hour)

**Historical Backfill:**
- [x] Year range selection
- [x] Progress tracking
- [x] Checkpoint saving
- [x] Resume capability
- [x] Quarterly processing
- [x] Senate/House filtering
- [x] Comprehensive logging
- [x] Error recovery

**Database Models:**
- [x] DataSource model
- [x] source_type field
- [x] status tracking
- [x] Record counts
- [x] Error messages
- [x] Metadata (JSONB)
- [x] Timestamps
- [x] Helper methods (mark_completed, mark_failed)

### ✅ Documentation

- [x] Quick Start Guide (`QUICK_START_DATA_PIPELINE.md`)
- [x] Comprehensive Guide (`DATA_PIPELINE_GUIDE.md`)
- [x] Implementation Details (`TASK_11_AUTOMATED_DATA_PIPELINE.md`)
- [x] Complete Summary (`TASK_11_COMPLETE_SUMMARY.md`)
- [x] Validation Checklist (this file)

### ✅ Helper Scripts

- [x] start_celery.sh
- [x] test_scraping.py
- [x] backfill_historical.py

### ✅ Error Handling

- [x] Scraper timeouts
- [x] Selenium errors
- [x] Parse failures
- [x] Validation errors
- [x] Database errors
- [x] Task retries
- [x] Logging
- [x] Alerts

## Deployment Checklist

### Infrastructure Setup

- [ ] Install Chrome/Chromium
  ```bash
  sudo apt-get install chromium-browser chromium-chromedriver
  ```

- [ ] Install Redis
  ```bash
  sudo apt-get install redis-server
  redis-server &
  ```

- [ ] Update .env
  ```bash
  echo "REDIS_URL=redis://localhost:6379/0" >> .env
  ```

### Database Setup

- [ ] Run migration
  ```bash
  alembic upgrade head
  ```

- [ ] Verify data_sources table created
  ```sql
  SELECT * FROM information_schema.tables WHERE table_name = 'data_sources';
  ```

### Testing

- [ ] Run test suite
  ```bash
  python scripts/test_scraping.py
  ```

- [ ] Test validator
  - [ ] Ticker normalization works
  - [ ] Ticker validation works
  - [ ] Transaction validation works

- [ ] Test database import
  - [ ] DataSource record created
  - [ ] Can query DataSource

- [ ] Test scrapers (optional - requires internet)
  - [ ] Senate scraper runs
  - [ ] House scraper runs
  - [ ] Data returned

### Celery Setup

- [ ] Start Celery worker
  ```bash
  celery -A app.tasks.scraping_tasks worker --loglevel=info
  ```

- [ ] Start Celery beat
  ```bash
  celery -A app.tasks.scraping_tasks beat --loglevel=info
  ```

- [ ] Verify tasks registered
  ```bash
  celery -A app.tasks.scraping_tasks inspect registered
  ```

### Manual Testing

- [ ] Trigger Senate scrape
  ```python
  from app.tasks.scraping_tasks import scrape_senate_daily
  result = scrape_senate_daily.delay(3)
  print(result.get(timeout=120))
  ```

- [ ] Verify results
  - [ ] Task completed
  - [ ] Records found
  - [ ] Records imported
  - [ ] DataSource created

- [ ] Trigger House scrape
  ```python
  from app.tasks.scraping_tasks import scrape_house_daily
  result = scrape_house_daily.delay(3)
  print(result.get(timeout=120))
  ```

- [ ] Verify results

### Scheduled Tasks

- [ ] Verify Celery Beat schedule
  ```python
  from app.tasks.scraping_tasks import celery_app
  print(celery_app.conf.beat_schedule)
  ```

- [ ] Wait for scheduled run (6 AM EST)
- [ ] Check logs
  ```bash
  tail -f logs/celery_worker.log
  tail -f logs/celery_beat.log
  ```

- [ ] Verify data imported

### Historical Backfill (Optional)

- [ ] Test with recent year
  ```bash
  python scripts/backfill_historical.py --start-year 2024 --end-year 2024
  ```

- [ ] Verify checkpoint saved
  ```bash
  cat scripts/backfill_checkpoint.json
  ```

- [ ] Test resume
  ```bash
  python scripts/backfill_historical.py --resume
  ```

- [ ] Run full backfill (when ready)
  ```bash
  python scripts/backfill_historical.py --start-year 2012
  ```

### Monitoring

- [ ] Set up log rotation
  ```bash
  # Add to logrotate.d
  /path/to/logs/*.log {
      daily
      rotate 7
      compress
      delaycompress
      missingok
      notifempty
  }
  ```

- [ ] Monitor DataSource records
  ```sql
  SELECT
      source_type,
      status,
      COUNT(*) as runs,
      SUM(records_imported) as total_imported
  FROM data_sources
  GROUP BY source_type, status;
  ```

- [ ] Set up alerts (optional)
  - [ ] Email on failure
  - [ ] Slack notification
  - [ ] Dashboard

### Performance Tuning

- [ ] Adjust rate limiting if needed
  - Default: 2 seconds
  - Conservative: 5 seconds
  - Fast: 1 second (risky)

- [ ] Adjust Celery settings
  - [ ] Worker concurrency
  - [ ] Task timeout
  - [ ] Retry settings

- [ ] Monitor resource usage
  - [ ] CPU
  - [ ] Memory
  - [ ] Database connections

## Production Checklist

### Security

- [ ] Redis authentication
  ```bash
  # redis.conf
  requirepass your_password
  ```

- [ ] Secure environment variables
- [ ] Firewall rules
- [ ] SSL/TLS if exposed

### Reliability

- [ ] Celery worker supervisor/systemd
- [ ] Redis persistence
- [ ] Database backups
- [ ] Error alerting

### Monitoring

- [ ] Set up Flower (optional)
  ```bash
  pip install flower
  celery -A app.tasks.scraping_tasks flower
  ```

- [ ] CloudWatch/Datadog/etc. (optional)
- [ ] Custom dashboard
- [ ] Health checks

### Documentation

- [ ] Internal documentation
- [ ] Runbook for operations
- [ ] Troubleshooting guide
- [ ] Contact information

## Verification Tests

### Unit Tests
```bash
# Validator tests
python -c "
from app.scrapers import DataValidator
v = DataValidator()
assert v.normalize_ticker('aapl') == 'AAPL'
assert v.normalize_ticker('fb') == 'META'
assert v.is_valid_ticker('AAPL')
assert not v.is_valid_ticker('LLC')
print('✓ Validator tests passed')
"
```

### Integration Tests
```bash
# Database test
python -c "
import asyncio
from sqlalchemy import select
from app.core.database import get_session
from app.models import DataSource

async def test():
    async for session in get_session():
        ds = DataSource(source_type='test', status='completed')
        session.add(ds)
        await session.commit()

        stmt = select(DataSource).where(DataSource.id == ds.id)
        result = await session.execute(stmt)
        fetched = result.scalar_one()

        await session.delete(fetched)
        await session.commit()
        print('✓ Database test passed')
        break

asyncio.run(test())
"
```

### End-to-End Test
```bash
# Full pipeline test
python scripts/test_scraping.py
```

## Sign-off

- [ ] All code reviewed
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Deployment tested
- [ ] Monitoring in place
- [ ] Team trained

## Rollback Plan

If issues occur:

1. Stop Celery
   ```bash
   pkill -f 'celery worker'
   pkill -f 'celery beat'
   ```

2. Rollback migration
   ```bash
   alembic downgrade -1
   ```

3. Remove code
   ```bash
   git checkout HEAD -- app/scrapers app/tasks scripts
   ```

4. Restart services

## Success Metrics

After 1 week:
- [ ] Daily scrapes running successfully
- [ ] Data being imported
- [ ] No recurring errors
- [ ] Performance acceptable

After 1 month:
- [ ] Consistent data collection
- [ ] Low error rate (<5%)
- [ ] Good data quality
- [ ] Team comfortable with system

## Notes

- **Rate Limiting**: Be respectful of government servers
- **Website Changes**: Monitor for structural changes
- **Data Quality**: Review invalid/skipped records periodically
- **Costs**: Monitor Redis/database size

---

**Checklist completed**: _____ / _____ / _____
**Deployed by**: _____________________
**Approved by**: _____________________
