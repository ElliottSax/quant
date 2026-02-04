"""
Locust load testing scenarios for the Quant API.
Run with: locust -f tests/performance/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between, TaskSet
import random
import json


class UserBehavior(TaskSet):
    """Simulates typical user behavior patterns."""

    def on_start(self):
        """Called when a simulated user starts."""
        # Register and login
        self.register_and_login()

    def register_and_login(self):
        """Register a new user and login."""
        user_id = random.randint(100000, 999999)
        self.email = f"loadtest{user_id}@test.com"
        self.password = "testpass123"

        # Register
        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": self.email,
                "username": f"user{user_id}",
                "password": self.password,
                "password_confirm": self.password
            },
            name="Register User"
        )

        # Login
        login_response = self.client.post(
            "/api/v1/auth/login",
            json={"email": self.email, "password": self.password},
            name="Login"
        )

        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(10)
    def browse_trades(self):
        """Browse recent trades - most common action."""
        params = {
            "limit": 50,
            "skip": random.randint(0, 100)
        }
        self.client.get(
            "/api/v1/trades/",
            params=params,
            headers=self.headers,
            name="Browse Trades"
        )

    @task(8)
    def search_politicians(self):
        """Search for politicians."""
        search_terms = ["john", "smith", "johnson", "williams", "brown"]
        params = {"search": random.choice(search_terms)}
        self.client.get(
            "/api/v1/politicians/",
            params=params,
            headers=self.headers,
            name="Search Politicians"
        )

    @task(5)
    def view_politician_profile(self):
        """View a specific politician's profile."""
        # Random politician ID (would need real IDs in production)
        self.client.get(
            "/api/v1/politicians/1",
            headers=self.headers,
            name="View Politician Profile",
            catch_response=True
        )

    @task(6)
    def get_analytics(self):
        """Fetch analytics data."""
        self.client.get(
            "/api/v1/analytics/summary",
            headers=self.headers,
            name="Get Analytics Summary"
        )

    @task(4)
    def search_tickers(self):
        """Search for stock tickers."""
        tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"]
        params = {"ticker": random.choice(tickers)}
        self.client.get(
            "/api/v1/trades/",
            params=params,
            headers=self.headers,
            name="Search by Ticker"
        )

    @task(3)
    def view_patterns(self):
        """View trading patterns."""
        self.client.get(
            "/api/v1/patterns/",
            headers=self.headers,
            name="View Patterns"
        )

    @task(2)
    def get_market_data(self):
        """Fetch market data."""
        tickers = ["AAPL", "GOOGL", "MSFT"]
        ticker = random.choice(tickers)
        self.client.get(
            f"/api/v1/market-data/{ticker}",
            headers=self.headers,
            name="Get Market Data",
            catch_response=True
        )

    @task(2)
    def view_statistics(self):
        """View statistics."""
        self.client.get(
            "/api/v1/stats/overview",
            headers=self.headers,
            name="View Statistics"
        )

    @task(1)
    def create_alert(self):
        """Create a new alert."""
        if hasattr(self, 'token'):
            alert_data = {
                "name": f"Load Test Alert {random.randint(1000, 9999)}",
                "alert_type": "trade",
                "conditions": {"min_amount": random.randint(50000, 500000)},
                "notification_channels": ["email"]
            }
            self.client.post(
                "/api/v1/alerts/",
                json=alert_data,
                headers=self.headers,
                name="Create Alert",
                catch_response=True
            )

    @task(1)
    def export_data(self):
        """Export data - resource intensive."""
        if hasattr(self, 'token'):
            export_data = {
                "format": "csv",
                "filters": {"limit": 100}
            }
            self.client.post(
                "/api/v1/export/trades",
                json=export_data,
                headers=self.headers,
                name="Export Data",
                catch_response=True
            )


class WebsiteUser(HttpUser):
    """Simulates website users with realistic timing."""
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks


class ApiUser(HttpUser):
    """Simulates API users with faster requests."""
    tasks = [UserBehavior]
    wait_time = between(0.5, 2)  # Faster API requests


class HeavyUser(HttpUser):
    """Simulates heavy users with minimal wait time."""
    tasks = [UserBehavior]
    wait_time = between(0.1, 0.5)  # Very fast requests


class ReadOnlyUser(HttpUser):
    """Simulates read-only users (no writes)."""
    wait_time = between(1, 3)

    @task(10)
    def browse_trades(self):
        """Browse recent trades."""
        self.client.get("/api/v1/trades/", params={"limit": 50})

    @task(5)
    def search_politicians(self):
        """Search politicians."""
        search_terms = ["john", "smith", "johnson"]
        self.client.get("/api/v1/politicians/", params={"search": random.choice(search_terms)})

    @task(3)
    def view_analytics(self):
        """View analytics."""
        self.client.get("/api/v1/analytics/summary")


# Custom scenarios for specific testing

class DatabaseStressTest(TaskSet):
    """Stress test database operations."""

    @task(5)
    def complex_query(self):
        """Execute complex queries."""
        params = {
            "limit": 100,
            "skip": 0,
            "sort": "transaction_date",
            "order": "desc",
            "min_amount": 100000
        }
        self.client.get("/api/v1/trades/", params=params, name="Complex Query")

    @task(3)
    def aggregation_query(self):
        """Test aggregation endpoints."""
        self.client.get("/api/v1/analytics/aggregated", name="Aggregation Query")

    @task(2)
    def join_heavy_query(self):
        """Test queries with joins."""
        self.client.get("/api/v1/politicians/?include_trades=true", name="Join Query")


class CacheStressTest(TaskSet):
    """Test caching behavior under load."""

    @task(10)
    def cached_endpoint(self):
        """Hit frequently cached endpoint."""
        self.client.get("/api/v1/stats/overview", name="Cached Stats")

    @task(5)
    def cache_busting_query(self):
        """Query with unique parameters to test cache misses."""
        random_skip = random.randint(0, 10000)
        self.client.get(f"/api/v1/trades/?skip={random_skip}", name="Cache Miss")


class RateLimitTest(TaskSet):
    """Test rate limiting under load."""

    def on_start(self):
        """Login to get token."""
        self.email = f"ratetest{random.randint(1000, 9999)}@test.com"
        self.password = "testpass123"

        # Register
        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": self.email,
                "username": f"rate{random.randint(1000, 9999)}",
                "password": self.password,
                "password_confirm": self.password
            }
        )

        # Login
        login_response = self.client.post(
            "/api/v1/auth/login",
            json={"email": self.email, "password": self.password}
        )

        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def rapid_fire_requests(self):
        """Make rapid requests to trigger rate limiting."""
        for _ in range(20):
            self.client.get(
                "/api/v1/trades/",
                headers=self.headers,
                name="Rate Limit Test"
            )


class DatabaseStressUser(HttpUser):
    """User for database stress testing."""
    tasks = [DatabaseStressTest]
    wait_time = between(0.1, 0.5)


class CacheStressUser(HttpUser):
    """User for cache stress testing."""
    tasks = [CacheStressTest]
    wait_time = between(0.1, 0.3)


class RateLimitUser(HttpUser):
    """User for rate limit testing."""
    tasks = [RateLimitTest]
    wait_time = between(0.01, 0.1)  # Very fast to hit rate limits
