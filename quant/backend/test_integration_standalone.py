"""
Standalone integration test for Celery automation critical fixes.

Tests all critical fixes implemented in the code review.
"""

import sys
from celery.schedules import crontab

# Test 1: Beat Schedule Configuration
def test_beat_schedule_uses_crontab():
    """Test that Beat schedule uses crontab for precise timing."""
    print("\n=== Test 1: Beat Schedule Configuration ===")

    from app.celery_app import celery_app

    beat_schedule = celery_app.conf.beat_schedule

    # Test daily scrape
    print("Testing scrape-daily schedule...")
    assert 'scrape-daily' in beat_schedule, "scrape-daily not found in beat_schedule"

    daily_schedule = beat_schedule['scrape-daily']['schedule']
    assert isinstance(daily_schedule, crontab), \
        f"✗ Expected crontab, got {type(daily_schedule).__name__}"

    assert daily_schedule.hour == {2}, f"✗ Expected hour=2, got {daily_schedule.hour}"
    assert daily_schedule.minute == {0}, f"✗ Expected minute=0, got {daily_schedule.minute}"
    print("✓ Daily scrape uses crontab(hour=2, minute=0)")

    # Test weekly scrape
    print("Testing scrape-weekly schedule...")
    assert 'scrape-weekly' in beat_schedule, "scrape-weekly not found in beat_schedule"

    weekly_schedule = beat_schedule['scrape-weekly']['schedule']
    assert isinstance(weekly_schedule, crontab), \
        f"✗ Expected crontab, got {type(weekly_schedule).__name__}"

    assert weekly_schedule.hour == {3}, f"✗ Expected hour=3, got {weekly_schedule.hour}"
    assert weekly_schedule.minute == {0}, f"✗ Expected minute=0, got {weekly_schedule.minute}"
    assert weekly_schedule.day_of_week == {0}, f"✗ Expected day_of_week=0, got {weekly_schedule.day_of_week}"
    print("✓ Weekly scrape uses crontab(hour=3, minute=0, day_of_week=0)")

    print("✓ Test 1 PASSED: Beat schedule uses crontab")


# Test 2: Database Engine Management
def test_database_engine_singleton():
    """Test that database engine is properly managed as singleton."""
    print("\n=== Test 2: Database Engine Management ===")

    from app.tasks.scraper_tasks import get_engine, get_session_maker

    engine1 = get_engine()
    engine2 = get_engine()
    assert engine1 is engine2, "✗ Engine should be a singleton"
    print("✓ Engine is singleton (same instance returned)")

    maker1 = get_session_maker()
    maker2 = get_session_maker()
    assert maker1 is maker2, "✗ Session maker should be a singleton"
    print("✓ Session maker is singleton (same instance returned)")

    # Check pool configuration
    assert engine1.pool.size() == 5, f"✗ Pool size should be 5, got {engine1.pool.size()}"
    print("✓ Engine has correct pool size (5)")

    print("✓ Test 2 PASSED: Database engine properly managed")


# Test 3: Event Loop Management
def test_event_loop_reuse():
    """Test that event loop is reused across tasks."""
    print("\n=== Test 3: Event Loop Management ===")

    from app.tasks.scraper_tasks import get_event_loop

    loop1 = get_event_loop()
    loop2 = get_event_loop()
    assert loop1 is loop2, "✗ Event loop should be a singleton"
    print("✓ Event loop is singleton (same instance returned)")

    assert not loop1.is_running(), "✗ Event loop should not be running"
    print("✓ Event loop is not running (can be used with run_until_complete)")

    # Test that we can run multiple coroutines
    async def simple_coro():
        return "success"

    result1 = loop1.run_until_complete(simple_coro())
    result2 = loop1.run_until_complete(simple_coro())
    assert result1 == "success" and result2 == "success"
    print("✓ Multiple coroutines can run on same event loop")

    print("✓ Test 3 PASSED: Event loop properly reused")


# Test 4: Date Validation
def test_date_validation():
    """Test that date validation works correctly."""
    print("\n=== Test 4: Date Validation ===")

    from datetime import date, timedelta
    from app.tasks.scraper_tasks import scrape_senate, scrape_house, scrape_all_chambers

    # Test invalid date format using apply()
    print("Testing invalid date format...")
    result = scrape_senate.apply(kwargs={"start_date": "invalid-date", "end_date": None, "days_back": 1})
    data = result.result
    assert data["status"] == "error", "✗ Should return error for invalid date"
    assert "Invalid date parameters" in data["error"], "✗ Should have date validation error"
    print("✓ Invalid date format properly rejected")

    # Test start_date after end_date
    print("Testing start_date after end_date...")
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    today = date.today().isoformat()
    result = scrape_senate.apply(kwargs={"start_date": tomorrow, "end_date": today, "days_back": 1})
    data = result.result
    assert data["status"] == "error", "✗ Should return error for invalid range"
    assert "cannot be after" in data["error"], "✗ Should have range validation error"
    print("✓ Invalid date range properly rejected")

    # Test valid dates (will fail at scraper execution but not date validation)
    print("Testing valid date range...")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    result = scrape_house.apply(kwargs={"start_date": yesterday, "end_date": today, "days_back": 1})
    data = result.result
    # Should NOT be a date validation error
    if data["status"] == "error":
        assert "Invalid date parameters" not in data.get("error", ""), \
            "✗ Valid dates should not trigger validation error"
    print("✓ Valid dates accepted")

    print("✓ Test 4 PASSED: Date validation works correctly")


# Test 5: Task Configuration
def test_task_configuration():
    """Test task retry and configuration."""
    print("\n=== Test 5: Task Configuration ===")

    from app.tasks.scraper_tasks import scrape_senate, scrape_house
    from app.celery_app import celery_app

    # Test retry configuration
    assert scrape_senate.max_retries == 3, "✗ Senate scraper should have max_retries=3"
    assert scrape_house.max_retries == 3, "✗ House scraper should have max_retries=3"
    print("✓ Tasks have correct max_retries (3)")

    assert scrape_senate.default_retry_delay == 300, "✗ Should have 5 minute retry delay"
    assert scrape_house.default_retry_delay == 300, "✗ Should have 5 minute retry delay"
    print("✓ Tasks have correct retry delay (300s)")

    # Test Celery configuration
    assert celery_app.conf.worker_max_tasks_per_child == 10, "✗ Should restart after 10 tasks"
    print("✓ Worker restarts after 10 tasks (prevents memory leaks)")

    assert celery_app.conf.task_acks_late is True, "✗ Should acknowledge after completion"
    print("✓ Tasks acknowledge after completion (task_acks_late=True)")

    assert celery_app.conf.worker_prefetch_multiplier == 1, "✗ Should prefetch only 1 task"
    print("✓ Worker prefetches one task at a time")

    print("✓ Test 5 PASSED: Task configuration correct")


# Test 6: Health Check Task
def test_health_check_task():
    """Test health check task execution."""
    print("\n=== Test 6: Health Check Task ===")

    from app.tasks.scraper_tasks import health_check

    result = health_check.apply()
    assert result.successful(), "✗ Health check should succeed"
    print("✓ Health check task executed successfully")

    data = result.result
    assert "status" in data, "✗ Result should have 'status'"
    assert data["status"] == "healthy", "✗ Status should be 'healthy'"
    assert "timestamp" in data, "✗ Result should have 'timestamp'"
    assert "worker" in data, "✗ Result should have 'worker'"
    print(f"✓ Health check returned correct format: {data}")

    print("✓ Test 6 PASSED: Health check task works")


# Test 7: Redis and PostgreSQL Connectivity
def test_infrastructure_connectivity():
    """Test that Redis and PostgreSQL are accessible."""
    print("\n=== Test 7: Infrastructure Connectivity ===")

    # Test Redis
    import redis
    r = redis.from_url("redis://localhost:6379/0")
    assert r.ping(), "✗ Redis ping failed"
    print("✓ Redis is accessible")

    # Test PostgreSQL
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    async def test_pg():
        engine = create_async_engine(
            "postgresql+asyncpg://quant_user:quant_password@localhost:5432/quant_db"
        )
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        await engine.dispose()

    asyncio.run(test_pg())
    print("✓ PostgreSQL is accessible")

    print("✓ Test 7 PASSED: Infrastructure connectivity verified")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("INTEGRATION TEST SUITE: Celery Automation Critical Fixes")
    print("=" * 70)

    tests = [
        test_beat_schedule_uses_crontab,
        test_database_engine_singleton,
        test_event_loop_reuse,
        test_date_validation,
        test_task_configuration,
        test_health_check_task,
        test_infrastructure_connectivity,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n✗ {test.__name__} FAILED:")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is production-ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
