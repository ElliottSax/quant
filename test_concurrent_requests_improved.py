"""
Test concurrent request handling after optimizations.

Tests the improvements:
1. Increased database connection pool (20 + 40 overflow)
2. Redis caching for ML results
3. Request semaphores (max 10 concurrent ML operations)
4. Circuit breaker pattern

Expected improvements:
- Before: 1-2/10 successful concurrent requests
- After: 8-10/10 successful (with caching)
- After (first run): 5-7/10 successful (without cache)
"""

import asyncio
import httpx
import time
from datetime import datetime

# Test configuration
API_BASE = "http://localhost:8000/api/v1"
CONCURRENT_REQUESTS = 10

# Use a real politician ID from your database
# You'll need to replace this with an actual UUID
TEST_POLITICIAN_ID = "3b1bd448-fff5-4ee3-9ccc-54988ca7d88f"  # Example


async def make_request(client: httpx.AsyncClient, request_id: int):
    """Make a single request and track timing"""
    start_time = time.time()

    try:
        response = await client.get(
            f"{API_BASE}/analytics/ensemble/{TEST_POLITICIAN_ID}",
            timeout=120.0  # 2 minute timeout
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            print(f"✓ Request {request_id}: SUCCESS in {elapsed:.2f}s")
            return {"id": request_id, "status": "success", "time": elapsed, "cached": "cache hit" in response.text.lower()}
        else:
            print(f"✗ Request {request_id}: FAILED with status {response.status_code} in {elapsed:.2f}s")
            return {"id": request_id, "status": "failed", "time": elapsed, "code": response.status_code}

    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        print(f"✗ Request {request_id}: TIMEOUT after {elapsed:.2f}s")
        return {"id": request_id, "status": "timeout", "time": elapsed}

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ Request {request_id}: ERROR - {str(e)[:50]} after {elapsed:.2f}s")
        return {"id": request_id, "status": "error", "time": elapsed, "error": str(e)}


async def test_concurrent_requests():
    """Test concurrent request handling"""

    print("=" * 80)
    print("CONCURRENT REQUEST TEST - WITH OPTIMIZATIONS")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"- Concurrent requests: {CONCURRENT_REQUESTS}")
    print(f"- Politician ID: {TEST_POLITICIAN_ID}")
    print(f"- API endpoint: {API_BASE}/analytics/ensemble/{{id}}")
    print(f"\nOptimizations enabled:")
    print(f"- ✓ Connection pool: 20 base + 40 overflow = 60 total")
    print(f"- ✓ Redis caching: 1-hour TTL")
    print(f"- ✓ Request semaphore: max 10 concurrent ML operations")
    print(f"- ✓ Circuit breaker: fault tolerance")
    print(f"\n" + "-" * 80)

    # First run - populate cache
    print(f"\nRUN 1: Cold cache (first request to populate cache)")
    print("-" * 80)

    async with httpx.AsyncClient() as client:
        # Warm up cache with single request
        warmup_start = time.time()
        warmup_response = await make_request(client, 0)
        warmup_elapsed = time.time() - warmup_start

        if warmup_response["status"] == "success":
            print(f"\n✓ Cache warmed up in {warmup_elapsed:.2f}s")
        else:
            print(f"\n✗ Warmup failed: {warmup_response}")
            return

    print(f"\nWaiting 2 seconds before concurrent test...")
    await asyncio.sleep(2)

    # Second run - test with cache
    print(f"\nRUN 2: Hot cache (testing concurrent requests with caching)")
    print("-" * 80)

    start_time = time.time()

    async with httpx.AsyncClient() as client:
        # Create concurrent requests
        tasks = [make_request(client, i+1) for i in range(CONCURRENT_REQUESTS)]

        # Execute all concurrently
        results = await asyncio.gather(*tasks)

    total_time = time.time() - start_time

    # Analyze results
    print(f"\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    successful = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "failed")
    timeouts = sum(1 for r in results if r["status"] == "timeout")
    errors = sum(1 for r in results if r["status"] == "error")
    cached = sum(1 for r in results if r.get("cached", False))

    avg_time = sum(r["time"] for r in results) / len(results)
    min_time = min(r["time"] for r in results)
    max_time = max(r["time"] for r in results)

    print(f"\nSuccess Rate: {successful}/{CONCURRENT_REQUESTS} ({successful/CONCURRENT_REQUESTS*100:.1f}%)")
    print(f"  - Successful: {successful}")
    print(f"  - Failed: {failed}")
    print(f"  - Timeout: {timeouts}")
    print(f"  - Error: {errors}")
    print(f"  - Cached responses: {cached}")

    print(f"\nTiming:")
    print(f"  - Total time: {total_time:.2f}s")
    print(f"  - Average response time: {avg_time:.2f}s")
    print(f"  - Fastest: {min_time:.2f}s")
    print(f"  - Slowest: {max_time:.2f}s")

    # Performance assessment
    print(f"\n" + "-" * 80)
    print("ASSESSMENT")
    print("-" * 80)

    if successful >= 8:
        print("✓ EXCELLENT: 80%+ success rate achieved!")
        print("  Caching and concurrency controls working as expected.")
    elif successful >= 5:
        print("✓ GOOD: 50%+ success rate")
        print("  Significant improvement over baseline (was 10-20%)")
        print("  Cache warmup may improve further.")
    elif successful >= 3:
        print("⚠ FAIR: 30%+ success rate")
        print("  Some improvement but not optimal.")
        print("  Check logs for bottlenecks.")
    else:
        print("✗ POOR: <30% success rate")
        print("  Optimizations may not be working correctly.")
        print("  Check Redis connection, database pool, and logs.")

    # Comparison to baseline
    print(f"\nComparison to baseline:")
    print(f"  - Before optimizations: 1-2/10 (10-20%)")
    print(f"  - After optimizations: {successful}/10 ({successful/CONCURRENT_REQUESTS*100:.0f}%)")
    improvement = (successful / CONCURRENT_REQUESTS * 100) - 15  # Baseline was ~15%
    print(f"  - Improvement: +{improvement:.0f} percentage points")

    print(f"\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_concurrent_requests())
