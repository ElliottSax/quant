# Database Migration Guide - Hybrid Model Fields

## Overview
This guide walks through applying the Alembic migration to add hybrid revenue model fields to the users table.

## Migration Details

**Migration File**: `alembic/versions/010_add_hybrid_model_fields.py`

### Fields Added
- `ad_free` (Boolean) - Tracks if user has ad-free tier
- `referral_code` (String 50) - Unique referral code per user
- `referral_credit_balance` (Float) - Account balance from referrals ($10 per referral)
- `referred_by_user_id` (String 36) - Track which user referred this user

### Constraint Update
Updates `subscription_tier` constraint from:
```sql
subscription_tier IN ('free', 'premium', 'enterprise')
```
to:
```sql
subscription_tier IN ('free', 'starter', 'professional', 'enterprise')
```

## Prerequisites

1. **Database Running**
   ```bash
   # PostgreSQL should be running (or your configured database)
   psql -U postgres -d quant_db  # Test connection
   ```

2. **Environment Variables Configured**
   ```bash
   # In backend/.env, ensure DATABASE_URL is set
   cat .env | grep DATABASE_URL
   # Should show: DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
   ```

3. **Python Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt  # Already includes alembic
   ```

## Running the Migration

### Step 1: Navigate to Backend Directory
```bash
cd /mnt/e/projects/quant/quant/backend
```

### Step 2: Check Migration Status
```bash
# See current revision and pending migrations
alembic current
alembic history
```

### Step 3: Apply the Migration
```bash
# Upgrade to the latest migration
alembic upgrade head

# Or upgrade to specific revision
alembic upgrade 010
```

### Step 4: Verify Migration
```bash
# Check the current revision
alembic current
# Should show: 010_add_hybrid_model_fields

# Connect to database and verify fields exist
psql -U postgres -d quant_db -c "\d users"
# Should show new columns: ad_free, referral_code, referral_credit_balance, referred_by_user_id
```

## Rolling Back (if needed)

### Downgrade to Previous Revision
```bash
alembic downgrade 009
```

### Downgrade All
```bash
alembic downgrade base
```

## Troubleshooting

### Issue: "Can't locate revision identified by '009_add_prediction_models'"
**Solution**: Check that migration 009 exists in `alembic/versions/`
```bash
ls -la alembic/versions/ | grep "009"
```

### Issue: "Database connection refused"
**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct
```bash
# Check environment variable
echo $DATABASE_URL

# Test connection
psql "$DATABASE_URL" -c "SELECT 1"
```

### Issue: "Constraint 'valid_subscription_tier' already exists"
**Solution**: Drop the old constraint first
```bash
psql "$DATABASE_URL" -c "ALTER TABLE users DROP CONSTRAINT valid_subscription_tier;"
```

### Issue: "Alembic command not found"
**Solution**: Install alembic or activate virtual environment
```bash
pip install alembic
# OR
source venv/bin/activate  # if using venv
```

## Verifying the Migration

### Check Users Table Schema
```sql
\d users  -- in psql
```

Should see columns:
```
 Column                    | Type                     | Collation | Nullable | Default
-----------------------------+----------------------------+-----------+----------+---------
 ad_free                   | boolean                  |           | not null | false
 referral_code             | character varying(50)    |           |          |
 referral_credit_balance   | double precision         |           | not null | 0.0
 referred_by_user_id       | character varying(36)    |           |          |
```

### Check Indexes
```sql
SELECT * FROM pg_indexes WHERE tablename = 'users';
```

Should include:
- `ix_users_referral_code` (unique)
- `ix_users_referred_by`

### Check Constraints
```sql
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'users';
```

Should show `valid_subscription_tier` with updated constraint.

## After Migration

1. **Verify backend starts**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   # Should start without database errors
   ```

2. **Test subscription endpoints**
   ```bash
   # Get subscription tiers
   curl http://localhost:8000/api/v1/subscription/tiers

   # Get subscription status (requires auth)
   curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/subscription/status
   ```

3. **Test referral endpoints**
   ```bash
   # Get referral code (requires auth)
   curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/subscription/referral/code
   ```

## Automated Deployments

If using CI/CD, add to your deployment script:

```bash
#!/bin/bash
set -e

# Navigate to backend
cd backend

# Run migrations before starting app
alembic upgrade head

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Production Checklist

- [ ] Backup database before migration
- [ ] Test migration on staging environment first
- [ ] Verify all 4 new fields created with correct types
- [ ] Verify indexes created
- [ ] Verify constraint updated
- [ ] Run subscription tests against new schema
- [ ] Monitor application logs after deployment
- [ ] Verify no data loss or corruption

## Next Steps

After successful migration:
1. Set up Stripe dashboard with price IDs
2. Configure environment variables with Stripe keys
3. Test payment flow in development
4. Deploy frontend with new components
5. Enable referral system
6. Monitor conversion metrics

## Support

For Alembic issues: https://alembic.sqlalchemy.org/
For database questions: Check PostgreSQL documentation or your DB provider's docs
