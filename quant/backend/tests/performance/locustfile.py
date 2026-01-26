"""
Load Testing Configuration for Quant Trading Platform

Usage:
    # Install locust
    pip install locust

    # Run load test
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

    # Run headless with specific users/spawn rate
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --users 100 --spawn-rate 10 --run-time 5m --headless

    # Run with web UI
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --web-host=127.0.0.1 --web-port=8089

Scenarios Tested:
- Anonymous user browsing public data
- Authenticated user viewing portfolio
- Heavy API user making frequent requests
- Research user running complex analyses
"""

import random
import json
from datetime import datetime, timedelta
from locust import HttpUser, task, between, SequentialTaskSet


# ============================================================================
# Helper Functions
# ============================================================================

def get_auth_token(client, email="loadtest@example.com", password="LoadTest123"):
    """Get authentication token for load testing"""
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


def create_test_user(client, email, password):
    """Create a test user for load testing"""
    client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email.split("@")[0],
        "password": password
    })


# ============================================================================
# Task Sets
# ============================================================================

class AnonymousBrowsingTasks(SequentialTaskSet):
    """Simulates anonymous user browsing public data"""

    @task
    def view_stats_overview(self):
        """View platform statistics"""
        self.client.get("/api/v1/stats/overview")

    @task
    def view_leaderboard(self):
        """View politician leaderboard"""
        self.client.get("/api/v1/stats/leaderboard?limit=20")

    @task
    def view_ticker_stats(self):
        """View popular ticker statistics"""
        self.client.get("/api/v1/stats/tickers?limit=20")

    @task
    def view_party_stats(self):
        """View statistics by party"""
        self.client.get("/api/v1/stats/by-party")

    @task
    def get_public_quote(self):
        """Get a public market quote"""
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/v1/market-data/public/quote/{symbol}")

    @task
    def get_market_status(self):
        """Check market status"""
        self.client.get("/api/v1/market-data/public/market-status")


class AuthenticatedUserTasks(SequentialTaskSet):
    """Simulates authenticated user interacting with the platform"""

    def on_start(self):
        """Login before starting tasks"""
        # Try to login with existing user
        response = self.client.post("/api/v1/auth/login", json={
            "email": "loadtest@example.com",
            "password": "LoadTest123"
        })

        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            # Create user if doesn't exist
            self.client.post("/api/v1/auth/register", json={
                "email": "loadtest@example.com",
                "username": "loadtest",
                "password": "LoadTest123"
            })
            response = self.client.post("/api/v1/auth/login", json={
                "email": "loadtest@example.com",
                "password": "LoadTest123"
            })
            self.token = response.json().get("access_token")

        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def view_stats_overview(self):
        """View platform statistics"""
        self.client.get("/api/v1/stats/overview", headers=self.headers)

    @task(3)
    def view_leaderboard(self):
        """View politician leaderboard"""
        self.client.get("/api/v1/stats/leaderboard?limit=50", headers=self.headers)

    @task(2)
    def get_market_quote(self):
        """Get market quote"""
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA"]
        symbol = random.choice(symbols)
        self.client.get(f"/api/v1/market-data/quote/{symbol}", headers=self.headers)

    @task(2)
    def get_multiple_quotes(self):
        """Get multiple quotes at once"""
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        query = "&".join([f"symbols={s}" for s in random.sample(symbols, 3)])
        self.client.get(f"/api/v1/market-data/quotes?{query}", headers=self.headers)

    @task(2)
    def get_historical_data(self):
        """Get historical market data"""
        symbol = random.choice(["AAPL", "GOOGL", "MSFT"])
        start = (datetime.utcnow() - timedelta(days=30)).isoformat()
        end = datetime.utcnow().isoformat()
        self.client.get(
            f"/api/v1/market-data/historical/{symbol}?start_date={start}&end_date={end}",
            headers=self.headers
        )

    @task(1)
    def search_symbols(self):
        """Search for stock symbols"""
        queries = ["tech", "energy", "finance", "health", "real"]
        query = random.choice(queries)
        self.client.get(f"/api/v1/market-data/search?query={query}", headers=self.headers)

    @task(1)
    def get_company_info(self):
        """Get company information"""
        symbol = random.choice(["AAPL", "GOOGL", "MSFT", "TSLA"])
        self.client.get(f"/api/v1/market-data/company/{symbol}", headers=self.headers)


class PowerUserTasks(SequentialTaskSet):
    """Simulates power user running analyses and making frequent requests"""

    def on_start(self):
        """Login before starting tasks"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "poweruser@example.com",
            "password": "PowerUser123"
        })

        if response.status_code != 200:
            self.client.post("/api/v1/auth/register", json={
                "email": "poweruser@example.com",
                "username": "poweruser",
                "password": "PowerUser123"
            })
            response = self.client.post("/api/v1/auth/login", json={
                "email": "poweruser@example.com",
                "password": "PowerUser123"
            })

        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def get_multiple_quotes(self):
        """Get multiple quotes (up to 50 for authenticated users)"""
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA",
                   "JPM", "BAC", "WMT", "DIS", "NFLX", "AMD", "INTC"]
        selected = random.sample(symbols, min(10, len(symbols)))
        query = "&".join([f"symbols={s}" for s in selected])
        self.client.get(f"/api/v1/market-data/quotes?{query}", headers=self.headers)

    @task(3)
    def get_historical_data(self):
        """Get historical data with various intervals"""
        symbol = random.choice(["AAPL", "GOOGL", "MSFT", "TSLA"])
        days = random.choice([7, 30, 90, 365])
        start = (datetime.utcnow() - timedelta(days=days)).isoformat()
        end = datetime.utcnow().isoformat()
        interval = random.choice(["1d", "1h", "5m"])

        self.client.get(
            f"/api/v1/market-data/historical/{symbol}?"
            f"start_date={start}&end_date={end}&interval={interval}",
            headers=self.headers
        )

    @task(2)
    def view_leaderboard_filtered(self):
        """View leaderboard with different filters"""
        days = random.choice([7, 30, 90, 365])
        limit = random.choice([10, 20, 50, 100])
        self.client.get(
            f"/api/v1/stats/leaderboard?days={days}&limit={limit}",
            headers=self.headers
        )

    @task(2)
    def view_ticker_stats(self):
        """View ticker statistics"""
        limit = random.choice([20, 50, 100])
        self.client.get(f"/api/v1/stats/tickers?limit={limit}", headers=self.headers)

    @task(1)
    def get_trade_volume(self):
        """Get trade volume over time"""
        start = (datetime.utcnow() - timedelta(days=90)).isoformat()
        end = datetime.utcnow().isoformat()
        self.client.get(
            f"/api/v1/stats/volume?start_date={start}&end_date={end}",
            headers=self.headers
        )


class ResearchUserTasks(SequentialTaskSet):
    """Simulates researcher running complex analyses and exports"""

    def on_start(self):
        """Login before starting tasks"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "researcher@example.com",
            "password": "Research123"
        })

        if response.status_code != 200:
            self.client.post("/api/v1/auth/register", json={
                "email": "researcher@example.com",
                "username": "researcher",
                "password": "Research123"
            })
            response = self.client.post("/api/v1/auth/login", json={
                "email": "researcher@example.com",
                "password": "Research123"
            })

        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def view_all_politicians(self):
        """View all politicians"""
        self.client.get("/api/v1/politicians?limit=100", headers=self.headers)

    @task(2)
    def get_historical_data_long_range(self):
        """Get long-range historical data"""
        symbol = random.choice(["AAPL", "GOOGL", "MSFT"])
        days = random.choice([365, 730, 1825])  # 1, 2, or 5 years
        start = (datetime.utcnow() - timedelta(days=days)).isoformat()
        end = datetime.utcnow().isoformat()

        self.client.get(
            f"/api/v1/market-data/historical/{symbol}?start_date={start}&end_date={end}",
            headers=self.headers
        )

    @task(1)
    def export_data_csv(self):
        """Export data in CSV format"""
        # This would need a valid politician ID in production
        # For load testing, we just check the endpoint responds
        self.client.get("/api/v1/stats/overview", headers=self.headers)

    @task(1)
    def view_comprehensive_stats(self):
        """View comprehensive statistics"""
        self.client.get("/api/v1/stats/overview", headers=self.headers)
        self.client.get("/api/v1/stats/leaderboard?limit=100", headers=self.headers)
        self.client.get("/api/v1/stats/tickers?limit=100", headers=self.headers)
        self.client.get("/api/v1/stats/by-party", headers=self.headers)


# ============================================================================
# User Classes
# ============================================================================

class AnonymousUser(HttpUser):
    """Anonymous user browsing public data"""
    tasks = [AnonymousBrowsingTasks]
    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks
    weight = 3  # 30% of users


class AuthenticatedUser(HttpUser):
    """Regular authenticated user"""
    tasks = [AuthenticatedUserTasks]
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    weight = 5  # 50% of users


class PowerUser(HttpUser):
    """Power user making frequent requests"""
    tasks = [PowerUserTasks]
    wait_time = between(0.5, 2)  # Wait 0.5-2 seconds between tasks
    weight = 1  # 10% of users


class ResearchUser(HttpUser):
    """Research user running complex analyses"""
    tasks = [ResearchUserTasks]
    wait_time = between(3, 8)  # Wait 3-8 seconds between tasks
    weight = 1  # 10% of users


# ============================================================================
# Standalone Test Functions
# ============================================================================

def test_endpoint_availability(host="http://localhost:8000"):
    """Quick test to verify endpoints are available before load testing"""
    import requests

    endpoints = [
        "/api/v1/stats/overview",
        "/api/v1/stats/leaderboard",
        "/api/v1/market-data/public/providers",
        "/api/v1/market-data/public/market-status",
    ]

    print(f"\nTesting endpoint availability at {host}...\n")

    for endpoint in endpoints:
        try:
            response = requests.get(f"{host}{endpoint}", timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{status} - {endpoint}")
        except Exception as e:
            print(f"❌ ERROR - {endpoint}: {str(e)}")

    print("\nEndpoint availability check complete.\n")


if __name__ == "__main__":
    # Run availability test when executed directly
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_endpoint_availability(host)
