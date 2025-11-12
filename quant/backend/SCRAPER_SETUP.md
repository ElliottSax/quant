# Congressional Trading Scrapers - Setup & Deployment Guide

This guide provides step-by-step instructions for setting up and deploying the congressional trading scrapers in development and production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Production Setup](#production-setup)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS 11+, or Windows 10+ with WSL2
- **RAM**: Minimum 2GB available (4GB+ recommended)
- **Disk Space**: 500MB for Chrome + dependencies
- **Network**: Stable internet connection

### Software Requirements

#### 1. Python 3.11+

```bash
# Check Python version
python --version  # Must be 3.11.0 or higher

# If needed, install Python 3.11
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev

# macOS (using Homebrew)
brew install python@3.11

# Verify installation
python3.11 --version
```

#### 2. Chrome/Chromium Browser

**The scrapers REQUIRE Chrome or Chromium to function.**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Verify installation
which chromium-browser
chromium-browser --version

# Alternative: Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb

# macOS
brew install --cask google-chrome

# Verify
which google-chrome
google-chrome --version
```

#### 3. PostgreSQL 12+

**The application REQUIRES PostgreSQL (SQLite is not supported).**

```bash
# Ubuntu/Debian
sudo apt-get install -y postgresql-12 postgresql-contrib-12 postgresql-client-12

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version  # Should be 12.x or higher

# macOS
brew install postgresql@12
brew services start postgresql@12

# Verify
psql --version
```

#### 4. Optional: TimescaleDB (Recommended for Production)

TimescaleDB provides time-series optimizations for trade data:

```bash
# Ubuntu/Debian
sudo apt-get install -y postgresql-12-timescaledb

# Enable TimescaleDB
sudo timescaledb-tune --quiet --yes

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify
psql -c "SELECT * FROM pg_available_extensions WHERE name = 'timescaledb';"
```

---

## Development Setup

### 1. Clone Repository

```bash
cd /path/to/your/workspace
git clone <repository-url> quant
cd quant/quant/backend
```

### 2. Create Virtual Environment

```bash
# Create venv
python3.11 -m venv venv

# Activate venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Verify critical packages
python -c "import selenium; print(f'Selenium: {selenium.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
python -c "from app.scrapers import SenateScraper, HouseScraper; print('✓ Scrapers OK')"
```

### 4. Configure PostgreSQL Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE quant_dev;
CREATE USER quant_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE quant_dev TO quant_user;

# Optional: Enable TimescaleDB
\c quant_dev
CREATE EXTENSION IF NOT EXISTS timescaledb;

# Exit psql
\q
```

### 5. Create Environment File

```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**.env Configuration**:

```bash
# Database (REQUIRED)
DATABASE_URL=postgresql://quant_user:your_secure_password_here@localhost:5432/quant_dev

# Security (REQUIRED)
# Generate secure key with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=<your-generated-32-char-key>

# Environment
ENVIRONMENT=development
DEBUG=true

# Redis (Optional - for Celery in Phase 2)
REDIS_URL=redis://localhost:6379/0

# API Keys (Optional - for data enrichment)
POLYGON_API_KEY=
ALPHA_VANTAGE_API_KEY=
```

### 6. Run Database Migrations

```bash
# Run Alembic migrations
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: politicians, trades, tickers, users
```

### 7. Run Tests

```bash
# Run all unit tests
pytest tests/test_senate_scraper.py tests/test_house_scraper.py tests/test_scraper_service.py -v

# Expected: 50 passed ✅

# Run single scraper test (optional)
pytest tests/test_senate_scraper.py::TestSenateScraper::test_clean_ticker_basic -v
```

### 8. Test Scraper (Manual)

```bash
# Run Senate scraper for last 7 days (visible browser for debugging)
python scripts/run_scrapers.py --chamber senate --days-back 7 --no-headless

# If successful, run in headless mode
python scripts/run_scrapers.py --chamber senate --days-back 7

# Run both scrapers
python scripts/run_scrapers.py --chamber all --days-back 30
```

---

## Production Setup

### 1. Server Provisioning

**Recommended Specs**:
- **CPU**: 2+ cores
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 50GB+ (depends on data retention)
- **OS**: Ubuntu 22.04 LTS

### 2. Install System Packages

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y \
    python3.11 python3.11-venv python3.11-dev \
    postgresql-12 postgresql-contrib-12 \
    chromium-browser chromium-chromedriver \
    nginx supervisor \
    git curl wget

# Install TimescaleDB (recommended)
sudo apt-get install -y postgresql-12-timescaledb
sudo timescaledb-tune --quiet --yes
sudo systemctl restart postgresql
```

### 3. Create Application User

```bash
# Create non-root user for app
sudo useradd -m -s /bin/bash quant
sudo usermod -aG www-data quant

# Switch to app user
sudo su - quant
```

### 4. Deploy Application

```bash
# Clone repository
cd /home/quant
git clone <repository-url> quant-app
cd quant-app/quant/backend

# Create venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt gunicorn
```

### 5. Configure Production Database

```bash
# As postgres user
sudo -u postgres psql

# Create production database
CREATE DATABASE quant_prod;
CREATE USER quant_prod_user WITH PASSWORD '<strong-random-password>';
GRANT ALL PRIVILEGES ON DATABASE quant_prod TO quant_prod_user;

# Enable TimescaleDB
\c quant_prod
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Create hypertable for trades (time-series optimization)
SELECT create_hypertable('trades', 'transaction_date', if_not_exists => TRUE);

\q
```

### 6. Production Environment Variables

```bash
# Create production .env
sudo nano /home/quant/quant-app/quant/backend/.env.production
```

**.env.production**:

```bash
# Database
DATABASE_URL=postgresql://quant_prod_user:<password>@localhost:5432/quant_prod

# Security
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(64))">
ENVIRONMENT=production
DEBUG=false

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/quant/scraper.log

# API Keys
POLYGON_API_KEY=<your-key-here>
ALPHA_VANTAGE_API_KEY=<your-key-here>
```

### 7. Set Proper Permissions

```bash
# Set file permissions
sudo chown -R quant:www-data /home/quant/quant-app
sudo chmod 700 /home/quant/quant-app/quant/backend/.env.production

# Create log directory
sudo mkdir -p /var/log/quant
sudo chown quant:www-data /var/log/quant
```

### 8. Run Migrations

```bash
# As quant user
cd /home/quant/quant-app/quant/backend
source venv/bin/activate
export $(cat .env.production | xargs)

# Run migrations
alembic upgrade head
```

### 9. Setup Cron for Automated Scraping

```bash
# Edit crontab
crontab -e

# Add scraping schedule
# Run daily at 2 AM
0 2 * * * cd /home/quant/quant-app/quant/backend && source venv/bin/activate && python scripts/run_scrapers.py --chamber all --days-back 1 >> /var/log/quant/cron.log 2>&1

# Run weekly full sync on Sundays at 3 AM
0 3 * * 0 cd /home/quant/quant-app/quant/backend && source venv/bin/activate && python scripts/run_scrapers.py --chamber all --days-back 7 >> /var/log/quant/cron.log 2>&1
```

### 10. Setup Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/quant
```

**/etc/logrotate.d/quant**:

```
/var/log/quant/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 quant www-data
    sharedscripts
}
```

---

## Verification

### 1. Test Scraper Execution

```bash
# Test Senate scraper (7 days)
python scripts/run_scrapers.py --chamber senate --days-back 7

# Expected output:
# ================================================================================
# Senate Scraping Results:
#   Total processed: X
#   Successfully saved: X
#   Skipped (duplicates): X
#   Errors: X
# ================================================================================
```

### 2. Verify Database

```bash
# Check trades
psql $DATABASE_URL -c "SELECT COUNT(*) FROM trades;"

# Check politicians
psql $DATABASE_URL -c "SELECT COUNT(*) FROM politicians;"

# View recent trades
psql $DATABASE_URL -c "SELECT p.name, t.ticker, t.transaction_type, t.transaction_date FROM trades t JOIN politicians p ON t.politician_id = p.id ORDER BY t.transaction_date DESC LIMIT 10;"
```

### 3. Check Logs

```bash
# View scraper log
tail -f /var/log/quant/scraper.log

# Check for errors
grep ERROR /var/log/quant/scraper.log

# View cron log
tail -f /var/log/quant/cron.log
```

### 4. Monitor System Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Troubleshooting

### Chrome/Chromium Issues

**Error**: "chrome not found" or "WebDriver not found"

```bash
# Install Chrome
sudo apt-get install -y chromium-browser chromium-chromedriver

# Verify
which chromium-browser
chromium-browser --version

# If still failing, specify Chrome path in code
export CHROME_BIN=/usr/bin/chromium-browser
```

**Error**: "SessionNotCreatedException: session not created: Chrome version mismatch"

```bash
# Update webdriver-manager
pip install --upgrade webdriver-manager

# Or install matching chromedriver manually
# Check Chrome version: chromium-browser --version
# Download matching chromedriver from: https://chromedriver.chromium.org/downloads
```

### Database Issues

**Error**: "database 'quant_dev' does not exist"

```bash
# Create database
sudo -u postgres createdb quant_dev
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE quant_dev TO quant_user;"
```

**Error**: "char_length function does not exist"

This indicates you're trying to use SQLite instead of PostgreSQL. **SQLite is not supported.**

```bash
# Verify DATABASE_URL points to PostgreSQL
echo $DATABASE_URL
# Should start with: postgresql://
```

**Error**: "JSONB type does not exist"

Your PostgreSQL version is too old. Requires PostgreSQL 9.4+.

```bash
# Check version
psql --version

# Upgrade if needed
sudo apt-get install postgresql-12
```

### Scraping Issues

**Error**: "NavigationException: Failed to navigate"

```bash
# Check internet connectivity
curl -I https://efdsearch.senate.gov/search/

# Try with visible browser to diagnose
python scripts/run_scrapers.py --chamber senate --days-back 1 --no-headless
```

**Error**: "TimeoutException: Timeout waiting for"

```bash
# Increase timeout
# Edit app/scrapers/senate.py or house.py
# Change: SenateScraper(timeout=60)  # Default is 30
```

**Error**: "No trades found"

- Website structure may have changed
- Check logs for parsing errors
- Run with `--no-headless` to observe browser behavior
- Verify date range has actual filings

### Permission Issues

**Error**: "Permission denied: /var/log/quant/scraper.log"

```bash
# Fix permissions
sudo mkdir -p /var/log/quant
sudo chown quant:www-data /var/log/quant
sudo chmod 755 /var/log/quant
```

---

## FAQ

### Q: Can I use SQLite instead of PostgreSQL?

**A**: No. The application uses PostgreSQL-specific features (JSONB, char_length, UUID) that are not compatible with SQLite.

### Q: Can I run scrapers without Chrome?

**A**: No. The scrapers use Selenium WebDriver which requires a browser (Chrome or Chromium).

### Q: How often should I run the scrapers?

**A**: Recommended schedule:
- **Daily**: Last 1-2 days to catch new filings
- **Weekly**: Last 7 days to catch any missed filings
- **Monthly**: Full sync to ensure consistency

### Q: What if the government websites change?

**A**: The scrapers use flexible selectors and fallback strategies, but major website redesigns may require code updates. Monitor error logs and update selectors in `app/scrapers/senate.py` and `app/scrapers/house.py` as needed.

### Q: How much data will be stored?

**A**: Approximate storage per trade record:
- Trade record: ~500 bytes
- Politician record: ~200 bytes
- 10,000 trades ≈ 5 MB

Expect ~100-500 MB per year depending on congressional activity.

### Q: Can I run multiple scrapers in parallel?

**A**: Currently, scrapers run sequentially. Parallel execution will be added in Phase 2 with Celery task queues.

### Q: How do I back up the database?

```bash
# Backup
pg_dump quant_prod > backup_$(date +%Y%m%d).sql

# Restore
psql quant_prod < backup_20250112.sql

# Automated daily backups via cron
0 1 * * * pg_dump quant_prod | gzip > /backups/quant_$(date +\%Y\%m\%d).sql.gz
```

### Q: What are the rate limits?

**A**: The scrapers have built-in retry logic but no explicit rate limiting. Government websites typically don't have strict rate limits. As a courtesy, we recommend:
- Max 1 request per second
- Max 5 concurrent filings
- Add 1-2 second delays between filing processing

---

## Support

For issues, questions, or contributions:
1. Check this documentation first
2. Review `SCRAPER_TESTING_REPORT.md` for known limitations
3. Check logs: `/var/log/quant/scraper.log` and `scraper.log`
4. Consult the codebase documentation in `scripts/README.md`

---

## Next Steps

After successful setup:
1. ✅ Verify scrapers run successfully
2. ✅ Set up automated scheduling (cron)
3. ✅ Configure monitoring and alerting
4. ⏭️ Proceed to **Phase 2**: Celery task automation (see MVP_ROADMAP.md)
