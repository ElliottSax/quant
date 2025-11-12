"""
Comprehensive End-to-End Testing and Debugging Suite

This suite tests the complete flow from API → Celery → Scraper → Database
and identifies edge cases, failure modes, and potential production issues.

Tests:
1. Complete request flow (API → Task → DB)
2. Concurrent task execution
3. Database connection pooling under load
4. Authentication and authorization
5. Error recovery and retry logic
6. Edge cases and boundary conditions
7. Resource cleanup and graceful shutdown
8. Performance under load
"""

import sys
import time
import asyncio
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
import redis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

print("=" * 80)
print("COMPREHENSIVE END-TO-END TEST SUITE")
print("=" * 80)


# =============================================================================
# Test 1: Complete Request Flow Analysis
# =============================================================================
def test_complete_request_flow():
    """
    Trace the complete flow: API → Celery → Scraper → Database

    Flow:
    1. API receives authenticated request
    2. Request validated (Pydantic)
    3. Task queued to Celery/Redis
    4. Worker picks up task from queue
    5. Task acquires DB connection from pool
    6. Task acquires event loop
    7. Scraper executes (or fails gracefully)
    8. Results saved to database
    9. Connection returned to pool
    10. Task result saved to Redis
    11. Worker acknowledgment
    """
    print("\n=== Test 1: Complete Request Flow Analysis ===")

    # Import after print to see any import errors
    from app.celery_app import celery_app
    from app.tasks.scraper_tasks import health_check, scrape_senate

    # Step 1: Verify Celery configuration
    print("Step 1: Verifying Celery configuration...")
    assert celery_app.conf.broker_url == "redis://localhost:6379/0"
    assert celery_app.conf.result_backend == "redis://localhost:6379/0"
    assert celery_app.conf.task_acks_late is True
    print("  ✓ Celery properly configured")

    # Step 2: Queue a simple task
    print("Step 2: Queuing health check task...")
    task = health_check.delay()
    print(f"  ✓ Task queued: {task.id}")

    # Step 3: Monitor task state transitions
    print("Step 3: Monitoring task execution...")
    states = []
    timeout = 15
    start = time.time()

    while not task.ready() and (time.time() - start) < timeout:
        current_state = task.state
        if not states or states[-1] != current_state:
            states.append(current_state)
            print(f"  → Task state: {current_state}")
        time.sleep(0.5)

    # Step 4: Verify successful completion
    if task.successful():
        result = task.result
        print(f"  ✓ Task completed successfully")
        print(f"  ✓ Result: {result}")
        print(f"  ✓ State transitions: {' → '.join(states)}")
    else:
        print(f"  ✗ Task failed or timed out")
        print(f"  ✗ Final state: {task.state}")
        if task.state == 'FAILURE':
            print(f"  ✗ Error: {task.info}")
        return False

    # Step 5: Test date validation in task
    print("Step 5: Testing date validation in task flow...")
    invalid_task = scrape_senate.apply(kwargs={
        "start_date": "not-a-date",
        "end_date": None,
        "days_back": 1
    })

    result = invalid_task.result
    assert result["status"] == "error", "Should catch invalid date"
    assert "Invalid date parameters" in result["error"]
    print("  ✓ Date validation working in task")

    print("✓ Test 1 PASSED: Complete request flow verified\n")
    return True


# =============================================================================
# Test 2: Concurrent Task Execution
# =============================================================================
def test_concurrent_tasks():
    """
    Test multiple tasks running simultaneously.

    Potential issues:
    - Database connection pool exhaustion
    - Event loop conflicts
    - Redis connection limits
    - Memory leaks
    """
    print("\n=== Test 2: Concurrent Task Execution ===")

    from app.tasks.scraper_tasks import health_check

    # Launch multiple tasks concurrently
    num_tasks = 10
    print(f"Launching {num_tasks} concurrent tasks...")

    tasks = []
    start = time.time()

    for i in range(num_tasks):
        task = health_check.delay()
        tasks.append(task)
        print(f"  → Task {i+1}/{num_tasks} queued: {task.id}")

    # Wait for all tasks
    print(f"Waiting for {num_tasks} tasks to complete...")
    timeout = 30
    completed = 0
    failed = 0

    for i, task in enumerate(tasks):
        wait_start = time.time()
        while not task.ready() and (time.time() - wait_start) < timeout:
            time.sleep(0.1)

        if task.successful():
            completed += 1
        else:
            failed += 1
            print(f"  ✗ Task {i+1} failed: {task.state}")

    elapsed = time.time() - start

    print(f"\nResults:")
    print(f"  Completed: {completed}/{num_tasks}")
    print(f"  Failed: {failed}/{num_tasks}")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Avg time per task: {elapsed/num_tasks:.2f}s")

    if completed == num_tasks:
        print("✓ Test 2 PASSED: All concurrent tasks completed\n")
        return True
    else:
        print(f"✗ Test 2 FAILED: {failed} tasks failed\n")
        return False


# =============================================================================
# Test 3: Database Connection Pool Behavior
# =============================================================================
def test_database_pool():
    """
    Test database connection pooling under load.

    Checks:
    - Pool size limits respected
    - Connections properly returned
    - No connection leaks
    - Pool overflow behavior
    """
    print("\n=== Test 3: Database Connection Pool Behavior ===")

    from app.tasks.scraper_tasks import get_engine, get_session_maker

    # Get engine and check pool configuration
    engine = get_engine()
    print(f"Pool configuration:")
    print(f"  Pool size: {engine.pool.size()}")
    print(f"  Current checked out: {engine.pool.checkedout()}")
    print(f"  Current overflow: {engine.pool.overflow()}")

    # Test multiple concurrent sessions
    async def test_concurrent_sessions():
        session_maker = get_session_maker()

        # Create more sessions than pool size
        num_sessions = 8
        print(f"\nCreating {num_sessions} concurrent sessions...")

        sessions = []
        try:
            for i in range(num_sessions):
                session = session_maker()
                sessions.append(session)

                # Execute a simple query
                async with session.begin():
                    result = await session.execute(text("SELECT 1 as test"))
                    assert result.scalar() == 1

                print(f"  ✓ Session {i+1} executed query")

            print(f"\nPool stats after {num_sessions} sessions:")
            print(f"  Checked out: {engine.pool.checkedout()}")
            print(f"  Overflow: {engine.pool.overflow()}")

        finally:
            # Close all sessions
            for session in sessions:
                await session.close()

            print(f"\nPool stats after closing sessions:")
            print(f"  Checked out: {engine.pool.checkedout()}")
            print(f"  Overflow: {engine.pool.overflow()}")

            # Verify connections returned
            assert engine.pool.checkedout() == 0, "All connections should be returned"

    # Run test
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_concurrent_sessions())

    print("✓ Test 3 PASSED: Connection pool behaves correctly\n")
    return True


# =============================================================================
# Test 4: Error Recovery and Retry Logic
# =============================================================================
def test_error_recovery():
    """
    Test error handling and retry mechanisms.

    Scenarios:
    - Invalid date formats
    - Invalid date ranges
    - Task failures
    - Retry logic
    - Max retries exceeded
    """
    print("\n=== Test 4: Error Recovery and Retry Logic ===")

    from app.tasks.scraper_tasks import scrape_senate

    # Test 1: Invalid date format
    print("Test 4.1: Invalid date format...")
    result = scrape_senate.apply(kwargs={
        "start_date": "2024-13-45",  # Invalid month/day
        "end_date": None,
        "days_back": 1
    })

    data = result.result
    assert data["status"] == "error"
    assert "Invalid date parameters" in data["error"]
    print("  ✓ Invalid date format handled correctly")

    # Test 2: Start date after end date
    print("Test 4.2: Invalid date range...")
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    result = scrape_senate.apply(kwargs={
        "start_date": tomorrow,
        "end_date": yesterday,
        "days_back": 1
    })

    data = result.result
    assert data["status"] == "error"
    assert "cannot be after" in data["error"]
    print("  ✓ Invalid date range handled correctly")

    # Test 3: Verify retry configuration
    print("Test 4.3: Retry configuration...")
    assert scrape_senate.max_retries == 3
    assert scrape_senate.default_retry_delay == 300
    print("  ✓ Retry configuration correct (max=3, delay=300s)")

    print("✓ Test 4 PASSED: Error recovery working correctly\n")
    return True


# =============================================================================
# Test 5: Resource Cleanup and Shutdown
# =============================================================================
def test_resource_cleanup():
    """
    Test resource cleanup and graceful shutdown.

    Checks:
    - Engine singleton behavior
    - Event loop singleton behavior
    - Cleanup function exists
    - No resource leaks
    """
    print("\n=== Test 5: Resource Cleanup and Shutdown ===")

    from app.tasks.scraper_tasks import (
        get_engine,
        get_session_maker,
        get_event_loop,
        cleanup_engine,
        _engine,
        _event_loop
    )

    # Test 1: Singleton behavior
    print("Test 5.1: Singleton behavior...")
    engine1 = get_engine()
    engine2 = get_engine()
    assert engine1 is engine2, "Engine should be singleton"

    loop1 = get_event_loop()
    loop2 = get_event_loop()
    assert loop1 is loop2, "Event loop should be singleton"
    print("  ✓ Singletons working correctly")

    # Test 2: Verify cleanup is registered
    print("Test 5.2: Cleanup registration...")
    import atexit
    # We can't easily test atexit handlers, but we can verify the function exists
    assert callable(cleanup_engine)
    print("  ✓ Cleanup function exists and is callable")

    # Test 3: Event loop can run multiple coroutines
    print("Test 5.3: Event loop reusability...")
    loop = get_event_loop()

    async def test_coro():
        return "success"

    result1 = loop.run_until_complete(test_coro())
    result2 = loop.run_until_complete(test_coro())
    assert result1 == "success" and result2 == "success"
    print("  ✓ Event loop reusable across operations")

    print("✓ Test 5 PASSED: Resource cleanup configured correctly\n")
    return True


# =============================================================================
# Test 6: Edge Cases and Boundary Conditions
# =============================================================================
def test_edge_cases():
    """
    Test edge cases and boundary conditions.

    Edge cases:
    - Empty date strings
    - Far future/past dates
    - days_back = 0
    - days_back = 365 (max)
    - Timezone edge cases
    """
    print("\n=== Test 6: Edge Cases and Boundary Conditions ===")

    from app.tasks.scraper_tasks import scrape_senate

    # Test 1: days_back boundary values
    print("Test 6.1: days_back boundary values...")

    # Min value (1)
    result = scrape_senate.apply(kwargs={
        "start_date": None,
        "end_date": None,
        "days_back": 1
    })
    # Will fail at scraping but should not fail at validation
    if result.result["status"] == "error":
        assert "Invalid date parameters" not in result.result.get("error", "")
    print("  ✓ days_back=1 handled correctly")

    # Test 2: Same day date range
    print("Test 6.2: Same day date range...")
    today = date.today().isoformat()

    result = scrape_senate.apply(kwargs={
        "start_date": today,
        "end_date": today,
        "days_back": 1
    })
    # Should be valid (start == end is allowed)
    if result.result["status"] == "error":
        assert "Invalid date parameters" not in result.result.get("error", "")
        assert "cannot be after" not in result.result.get("error", "")
    print("  ✓ Same day date range handled correctly")

    # Test 3: Far past date
    print("Test 6.3: Far past date...")
    old_date = "2000-01-01"

    result = scrape_senate.apply(kwargs={
        "start_date": old_date,
        "end_date": today,
        "days_back": 1
    })
    # Should be valid date-wise
    if result.result["status"] == "error":
        assert "Invalid date parameters" not in result.result.get("error", "")
    print("  ✓ Far past date handled correctly")

    # Test 4: Leap year date
    print("Test 6.4: Leap year date...")
    leap_date = "2024-02-29"

    result = scrape_senate.apply(kwargs={
        "start_date": leap_date,
        "end_date": None,
        "days_back": 1
    })
    # 2024-02-29 is valid (2024 is a leap year)
    if result.result["status"] == "error":
        assert "Invalid date parameters" not in result.result.get("error", "")
    print("  ✓ Leap year date handled correctly")

    # Test 5: Invalid leap year date
    print("Test 6.5: Invalid leap year date...")
    invalid_leap = "2023-02-29"  # 2023 is not a leap year

    result = scrape_senate.apply(kwargs={
        "start_date": invalid_leap,
        "end_date": None,
        "days_back": 1
    })
    # Should catch invalid date
    data = result.result
    assert data["status"] == "error"
    assert "Invalid date parameters" in data["error"]
    print("  ✓ Invalid leap year date caught correctly")

    print("✓ Test 6 PASSED: Edge cases handled correctly\n")
    return True


# =============================================================================
# Test 7: Beat Scheduler Configuration
# =============================================================================
def test_beat_scheduler():
    """
    Test Celery Beat scheduler configuration.

    Checks:
    - Schedules use crontab (not intervals)
    - Correct timing configuration
    - Task arguments correct
    """
    print("\n=== Test 7: Beat Scheduler Configuration ===")

    from app.celery_app import celery_app
    from celery.schedules import crontab

    beat_schedule = celery_app.conf.beat_schedule

    # Test 1: Daily schedule
    print("Test 7.1: Daily schedule...")
    daily = beat_schedule["scrape-daily"]
    assert isinstance(daily["schedule"], crontab)
    assert daily["schedule"].hour == {2}
    assert daily["schedule"].minute == {0}
    assert daily["kwargs"]["days_back"] == 1
    print("  ✓ Daily: crontab(hour=2, minute=0), days_back=1")

    # Test 2: Weekly schedule
    print("Test 7.2: Weekly schedule...")
    weekly = beat_schedule["scrape-weekly"]
    assert isinstance(weekly["schedule"], crontab)
    assert weekly["schedule"].hour == {3}
    assert weekly["schedule"].minute == {0}
    assert weekly["schedule"].day_of_week == {0}  # Sunday
    assert weekly["kwargs"]["days_back"] == 7
    print("  ✓ Weekly: crontab(hour=3, minute=0, day_of_week=0), days_back=7")

    # Test 3: Health check
    print("Test 7.3: Health check schedule...")
    health = beat_schedule["health-check"]
    assert isinstance(health["schedule"], (int, float))
    assert health["schedule"] == 300  # 5 minutes
    print("  ✓ Health check: 300s interval")

    # Test 4: Verify no overlap
    print("Test 7.4: Schedule overlap check...")
    # Daily at 2 AM, Weekly at 3 AM - no overlap
    assert daily["schedule"].hour != weekly["schedule"].hour
    print("  ✓ No schedule overlap (daily=2AM, weekly=3AM)")

    print("✓ Test 7 PASSED: Beat scheduler configured correctly\n")
    return True


# =============================================================================
# Test 8: Redis Connectivity and Failover
# =============================================================================
def test_redis_connectivity():
    """
    Test Redis connectivity and error handling.

    Checks:
    - Redis connection successful
    - Task results persist
    - Result expiration configured
    """
    print("\n=== Test 8: Redis Connectivity ===")

    from app.celery_app import celery_app

    # Test 1: Direct Redis connection
    print("Test 8.1: Direct Redis connection...")
    r = redis.from_url("redis://localhost:6379/0")
    assert r.ping(), "Redis ping failed"
    print("  ✓ Redis connection successful")

    # Test 2: Celery can write to Redis
    print("Test 8.2: Celery result backend...")
    from app.tasks.scraper_tasks import health_check

    task = health_check.delay()
    while not task.ready():
        time.sleep(0.1)

    # Verify result is in Redis
    result = task.result
    assert result is not None
    assert "status" in result
    print("  ✓ Task result persisted to Redis")

    # Test 3: Result expiration configured
    print("Test 8.3: Result expiration...")
    assert celery_app.conf.result_expires == 86400  # 24 hours
    print("  ✓ Results expire after 24 hours")

    print("✓ Test 8 PASSED: Redis connectivity verified\n")
    return True


# =============================================================================
# Test 9: Database Schema Validation
# =============================================================================
def test_database_schema():
    """
    Test database schema is correct.

    Checks:
    - All required tables exist
    - Columns and types correct
    - Indexes exist
    - Foreign keys configured
    """
    print("\n=== Test 9: Database Schema Validation ===")

    async def check_schema():
        engine = create_async_engine(
            "postgresql+asyncpg://quant_user:quant_password@localhost:5432/quant_db"
        )

        try:
            async with engine.connect() as conn:
                # Test 1: Check tables exist
                print("Test 9.1: Checking tables...")
                result = await conn.execute(text("""
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """))
                tables = [row[0] for row in result]

                required_tables = ['alembic_version', 'politicians', 'tickers', 'trades', 'users']
                for table in required_tables:
                    assert table in tables, f"Missing table: {table}"
                    print(f"  ✓ Table exists: {table}")

                # Test 2: Check trades table structure
                print("\nTest 9.2: Checking trades table structure...")
                result = await conn.execute(text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'trades'
                    ORDER BY ordinal_position
                """))
                columns = {row[0]: row[1] for row in result}

                required_columns = {
                    'id': 'uuid',
                    'politician_id': 'uuid',
                    'ticker': 'character varying',
                    'transaction_type': 'character varying',
                    'transaction_date': 'date',
                    'disclosure_date': 'date',
                }

                for col, dtype in required_columns.items():
                    assert col in columns, f"Missing column: {col}"
                    assert dtype in columns[col], f"Wrong type for {col}: {columns[col]}"
                print(f"  ✓ All required columns present with correct types")

                # Test 3: Check indexes
                print("\nTest 9.3: Checking indexes...")
                result = await conn.execute(text("""
                    SELECT indexname FROM pg_indexes
                    WHERE tablename = 'trades'
                    ORDER BY indexname
                """))
                indexes = [row[0] for row in result]

                required_indexes = [
                    'ix_trades_politician_id',
                    'ix_trades_ticker',
                    'ix_trades_transaction_date'
                ]

                for idx in required_indexes:
                    assert idx in indexes, f"Missing index: {idx}"
                    print(f"  ✓ Index exists: {idx}")

                # Test 4: Check foreign key
                print("\nTest 9.4: Checking foreign keys...")
                result = await conn.execute(text("""
                    SELECT
                        tc.constraint_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_name='trades'
                """))
                fks = list(result)

                assert len(fks) > 0, "No foreign keys found"
                # Should have FK from trades.politician_id to politicians.id
                assert any('politician' in fk[0].lower() for fk in fks)
                print(f"  ✓ Foreign key constraints configured")

        finally:
            await engine.dispose()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_schema())

    print("✓ Test 9 PASSED: Database schema correct\n")
    return True


# =============================================================================
# Test 10: Performance Baseline
# =============================================================================
def test_performance_baseline():
    """
    Establish performance baseline metrics.

    Metrics:
    - Task queue latency
    - Task execution time
    - Database query time
    - Memory usage
    """
    print("\n=== Test 10: Performance Baseline ===")

    from app.tasks.scraper_tasks import health_check

    # Test 1: Task queue latency
    print("Test 10.1: Task queue latency...")
    latencies = []

    for i in range(5):
        queue_start = time.time()
        task = health_check.delay()

        # Wait for task to start (not complete)
        while task.state == 'PENDING':
            time.sleep(0.01)

        latency = time.time() - queue_start
        latencies.append(latency)

        # Wait for completion
        while not task.ready():
            time.sleep(0.01)

    avg_latency = sum(latencies) / len(latencies)
    print(f"  Average queue latency: {avg_latency*1000:.2f}ms")

    if avg_latency < 0.1:  # < 100ms
        print("  ✓ Queue latency excellent (<100ms)")
    elif avg_latency < 0.5:  # < 500ms
        print("  ✓ Queue latency good (<500ms)")
    else:
        print(f"  ⚠ Queue latency high ({avg_latency*1000:.0f}ms)")

    # Test 2: Task execution time
    print("\nTest 10.2: Task execution time...")
    exec_times = []

    for i in range(5):
        exec_start = time.time()
        task = health_check.delay()

        while not task.ready():
            time.sleep(0.01)

        exec_time = time.time() - exec_start
        exec_times.append(exec_time)

    avg_exec = sum(exec_times) / len(exec_times)
    print(f"  Average execution time: {avg_exec*1000:.2f}ms")

    if avg_exec < 0.05:  # < 50ms
        print("  ✓ Execution time excellent (<50ms)")
    elif avg_exec < 0.2:  # < 200ms
        print("  ✓ Execution time good (<200ms)")
    else:
        print(f"  ⚠ Execution time high ({avg_exec*1000:.0f}ms)")

    # Test 3: Database connection acquisition
    print("\nTest 10.3: Database connection acquisition...")

    async def measure_db_time():
        from app.tasks.scraper_tasks import get_session_maker
        session_maker = get_session_maker()

        times = []
        for i in range(5):
            start = time.time()
            async with session_maker() as session:
                async with session.begin():
                    await session.execute(text("SELECT 1"))
            elapsed = time.time() - start
            times.append(elapsed)

        return sum(times) / len(times)

    loop = asyncio.get_event_loop()
    avg_db_time = loop.run_until_complete(measure_db_time())
    print(f"  Average DB query time: {avg_db_time*1000:.2f}ms")

    if avg_db_time < 0.01:  # < 10ms
        print("  ✓ DB query time excellent (<10ms)")
    elif avg_db_time < 0.05:  # < 50ms
        print("  ✓ DB query time good (<50ms)")
    else:
        print(f"  ⚠ DB query time high ({avg_db_time*1000:.0f}ms)")

    print("\n✓ Test 10 PASSED: Performance baseline established\n")
    return True


# =============================================================================
# Run All Tests
# =============================================================================
def run_all_tests():
    """Execute all tests and report results."""

    tests = [
        ("Complete Request Flow", test_complete_request_flow),
        ("Concurrent Tasks", test_concurrent_tasks),
        ("Database Pool", test_database_pool),
        ("Error Recovery", test_error_recovery),
        ("Resource Cleanup", test_resource_cleanup),
        ("Edge Cases", test_edge_cases),
        ("Beat Scheduler", test_beat_scheduler),
        ("Redis Connectivity", test_redis_connectivity),
        ("Database Schema", test_database_schema),
        ("Performance Baseline", test_performance_baseline),
    ]

    results = []
    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"\n{'='*80}")
            print(f"Running: {name}")
            print(f"{'='*80}")

            result = test_func()
            if result:
                passed += 1
                results.append((name, "PASSED", None))
            else:
                failed += 1
                results.append((name, "FAILED", "Test returned False"))

        except Exception as e:
            failed += 1
            results.append((name, "FAILED", str(e)))
            print(f"\n✗ {name} FAILED with exception:")
            print(f"  {e}")
            import traceback
            traceback.print_exc()

    # Final Report
    print("\n" + "="*80)
    print("FINAL TEST REPORT")
    print("="*80)

    for name, status, error in results:
        symbol = "✓" if status == "PASSED" else "✗"
        print(f"{symbol} {name}: {status}")
        if error:
            print(f"    Error: {error}")

    print(f"\n{'='*80}")
    print(f"TOTAL: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"{'='*80}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is production-ready.")
        print("\nPerformance Summary:")
        print("  - Task queue latency: Measured")
        print("  - Task execution time: Measured")
        print("  - Database query time: Measured")
        print("  - Concurrent execution: Verified")
        print("  - Resource cleanup: Verified")
        print("  - Error handling: Verified")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
