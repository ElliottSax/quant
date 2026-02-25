#!/bin/bash

# Database Cleanup and Maintenance Script

echo "=========================================="
echo " Database Cleanup & Maintenance"
echo "=========================================="
echo ""

# Check if we have access to database
if ! docker exec quant-postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running or not accessible"
    exit 1
fi

echo "✓ PostgreSQL is accessible"
echo ""

# Function to run SQL
run_sql() {
    docker exec quant-postgres psql -U postgres -d quant_db -c "$1"
}

# 1. Clean up failed auth attempts (if users table exists)
echo "1. Checking for cleanup opportunities..."

# Check if alembic_version table exists
if run_sql "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version';" 2>/dev/null | grep -q "1"; then
    echo "  ✓ Database schema initialized"

    # Check for users table
    if run_sql "SELECT 1 FROM information_schema.tables WHERE table_name='users';" 2>/dev/null | grep -q "1"; then
        echo "  ✓ Users table exists"

        # Count test users
        TEST_USER_COUNT=$(run_sql "SELECT COUNT(*) FROM users WHERE email LIKE 'concurrent_%' OR email LIKE 'test%';" -t 2>/dev/null | tr -d ' ')

        if [ "$TEST_USER_COUNT" -gt 0 ] 2>/dev/null; then
            echo "  ⚠  Found $TEST_USER_COUNT test users"
            echo ""
            read -p "  Remove test users? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_sql "DELETE FROM users WHERE email LIKE 'concurrent_%' OR email LIKE 'test%';" > /dev/null 2>&1
                echo "  ✓ Test users removed"
            fi
        else
            echo "  ✓ No test users to clean up"
        fi
    else
        echo "  ℹ  Users table not yet created (run migrations)"
    fi
else
    echo "  ℹ  Database not yet migrated (tables will be created on first run)"
fi

echo ""
echo "2. Database Statistics:"

# Database size
DB_SIZE=$(run_sql "SELECT pg_size_pretty(pg_database_size('quant_db'));" -t 2>/dev/null | tr -d ' ')
echo "  Database size: $DB_SIZE"

# Connection count
CONN_COUNT=$(run_sql "SELECT count(*) FROM pg_stat_activity WHERE datname='quant_db';" -t 2>/dev/null | tr -d ' ')
echo "  Active connections: $CONN_COUNT"

# Table count
TABLE_COUNT=$(run_sql "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" -t 2>/dev/null | tr -d ' ')
echo "  Tables: $TABLE_COUNT"

echo ""
echo "3. Vacuum and Analyze:"
echo "  Running VACUUM ANALYZE..."
run_sql "VACUUM ANALYZE;" > /dev/null 2>&1
echo "  ✓ Database optimized"

echo ""
echo "=========================================="
echo " Cleanup Complete"
echo "=========================================="
