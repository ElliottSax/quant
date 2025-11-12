# Congressional Trading Scrapers

This directory contains scripts for scraping congressional financial disclosures from Senate and House websites.

## Overview

The scrapers extract Periodic Transaction Report (PTR) data from:
- **Senate**: efdsearch.senate.gov
- **House**: disclosuresclerk.house.gov

## Requirements

- Python 3.11+
- Chrome/Chromium browser installed
- All dependencies from requirements.txt

## Usage

### Unified Scraper (Recommended)

Run both Senate and House scrapers:

```bash
cd quant/backend
python scripts/run_scrapers.py --chamber all
```

Run only Senate:

```bash
python scripts/run_scrapers.py --chamber senate
```

Run only House:

```bash
python scripts/run_scrapers.py --chamber house
```

### Date Range Options

Last 30 days (default):
```bash
python scripts/run_scrapers.py --chamber all
```

Last 90 days:
```bash
python scripts/run_scrapers.py --chamber all --days-back 90
```

Custom date range:
```bash
python scripts/run_scrapers.py --chamber all \
    --start-date 2024-01-01 \
    --end-date 2024-01-31
```

### Debug Mode

Run with visible browser for debugging:
```bash
python scripts/run_scrapers.py --chamber senate --no-headless
```

### Legacy Scripts

Individual scrapers (backward compatibility):

```bash
# Senate only
python scripts/run_senate_scraper.py

# With options
python scripts/run_senate_scraper.py --days-back 60 --no-headless
```

## Output

The scrapers will:
1. Navigate to disclosure websites
2. Search for PTR filings in the specified date range
3. Extract transaction data (politician, ticker, type, amount, dates)
4. Validate and clean the data
5. Save to the database (skipping duplicates)
6. Print statistics

Example output:
```
================================================================================
Senate Scraping Results:
  Total processed: 150
  Successfully saved: 145
  Skipped (duplicates): 3
  Errors: 2
================================================================================
House Scraping Results:
  Total processed: 230
  Successfully saved: 225
  Skipped (duplicates): 4
  Errors: 1
================================================================================
Combined Results:
  Total saved: 370
  Total errors: 3
================================================================================
```

## Logging

All scraping activity is logged to:
- **Console**: INFO level and above
- **File**: `scraper.log` (all levels)

## Data Validation

The scrapers include comprehensive validation:

- **Required fields**: politician_name, chamber, ticker, transaction_type, dates
- **Ticker format**: 1-10 alphanumeric characters (normalized to uppercase)
- **Transaction types**: Only 'buy' or 'sell' (normalizes 'sale' → 'sell')
- **Date validation**: Disclosure date must be >= transaction date
- **Amount validation**: Non-negative, min <= max
- **Duplicate detection**: Prevents duplicate trades via unique index

## Error Handling

- **Retry logic**: 3 attempts with 5-second delays for network errors
- **Graceful failure**: Continues processing on individual record errors
- **Transaction rollback**: Database rollback on save errors
- **Detailed logging**: All errors logged with stack traces

## Architecture

```
scripts/
├── run_scrapers.py          # Unified CLI for all scrapers
└── run_senate_scraper.py    # Legacy Senate-only CLI

app/scrapers/
├── base.py                  # Abstract base class with Selenium setup
├── senate.py                # Senate scraper implementation
└── house.py                 # House scraper implementation

app/services/
└── scraper_service.py       # Data validation and database storage
```

## Scheduling

For automated scraping, use cron:

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/quant/backend && python scripts/run_scrapers.py --chamber all

# Run weekly on Sundays at 3 AM
0 3 * * 0 cd /path/to/quant/backend && python scripts/run_scrapers.py --chamber all --days-back 7
```

Or use Celery tasks (see MVP_ROADMAP.md Phase 1, Sprint 5).

## Troubleshooting

### Chrome/ChromeDriver Issues

If you get "chromedriver not found":
```bash
# The webdriver-manager package should auto-download, but you can manually install:
apt-get install chromium-browser chromium-chromedriver  # Ubuntu/Debian
```

### Timeout Errors

Increase timeout in scraper initialization:
```python
scraper = SenateScraper(timeout=60)  # Default is 30 seconds
```

### Website Structure Changes

If scrapers fail due to website changes:
1. Run with `--no-headless` to see what's happening
2. Check browser console for JavaScript errors
3. Inspect element selectors in the scraper code
4. Update XPath/CSS selectors as needed

### Rate Limiting

If you're getting blocked:
1. Reduce frequency of scraping
2. Add delays between requests (modify `retry_delay` in BaseScraper)
3. Use residential proxy (configure in ChromeOptions)

## Performance

- **Senate scraper**: ~2-3 seconds per filing
- **House scraper**: ~2-3 seconds per filing
- **Memory usage**: ~200-300 MB (Chrome browser)
- **Database**: Uses connection pooling for efficiency

## Security

- Runs in headless mode by default (no GUI)
- No sensitive data logged
- Database credentials from environment variables
- XSS protection via Pydantic validation
- SQL injection protection via SQLAlchemy ORM

## Development

Run tests:
```bash
pytest tests/test_scraper_service.py -v
```

Add new scrapers by:
1. Subclassing `BaseScraper`
2. Implementing abstract methods
3. Adding to `run_all_scrapers()`

## Support

For issues or questions:
- Check logs in `scraper.log`
- Review error messages in console output
- Consult the codebase documentation
