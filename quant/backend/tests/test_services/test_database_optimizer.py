"""Tests for Database Optimizer service."""

import pytest
from datetime import datetime

from app.services.database_optimizer import (
    QueryAnalyzer,
    QueryStats,
    SlowQuery,
    IndexRecommendation,
)


class TestQueryAnalyzer:
    """Test cases for QueryAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create query analyzer instance."""
        return QueryAnalyzer()

    async def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.query_stats == {}
        assert analyzer.slow_queries == []
        assert analyzer.slow_query_threshold == 1.0

    async def test_normalize_query_whitespace(self, analyzer):
        """Test query normalization removes extra whitespace."""
        query = "SELECT  *  FROM   trades   WHERE  id  =  1"
        normalized = analyzer.normalize_query(query)
        assert normalized == "SELECT * FROM trades WHERE id = ?"

    async def test_normalize_query_numbers(self, analyzer):
        """Test query normalization replaces numbers."""
        query = "SELECT * FROM trades WHERE amount > 10000 AND id = 123"
        normalized = analyzer.normalize_query(query)
        assert "10000" not in normalized
        assert "123" not in normalized
        assert "?" in normalized

    async def test_normalize_query_strings(self, analyzer):
        """Test query normalization replaces string literals."""
        query = "SELECT * FROM politicians WHERE name = 'John Doe'"
        normalized = analyzer.normalize_query(query)
        assert "'John Doe'" not in normalized
        assert "?" in normalized

    async def test_normalize_query_uuids(self, analyzer):
        """Test query normalization replaces UUIDs."""
        query = "SELECT * FROM trades WHERE id = '550e8400-e29b-41d4-a716-446655440000'"
        normalized = analyzer.normalize_query(query)
        assert "550e8400-e29b-41d4-a716-446655440000" not in normalized
        assert "?" in normalized

    async def test_normalize_query_multiple_values(self, analyzer):
        """Test normalization with multiple different values."""
        query = """
            SELECT * FROM trades
            WHERE politician_id = '550e8400-e29b-41d4-a716-446655440000'
            AND amount > 50000
            AND ticker = 'AAPL'
        """
        normalized = analyzer.normalize_query(query)
        # All values should be replaced with ?
        assert "550e8400" not in normalized
        assert "50000" not in normalized
        assert "AAPL" not in normalized

    async def test_get_query_hash_consistency(self, analyzer):
        """Test that same query produces same hash."""
        query = "SELECT * FROM trades WHERE id = 1"
        hash1 = analyzer.get_query_hash(query)
        hash2 = analyzer.get_query_hash(query)
        assert hash1 == hash2

    async def test_get_query_hash_normalization(self, analyzer):
        """Test that similar queries produce same hash."""
        query1 = "SELECT * FROM trades WHERE id = 1"
        query2 = "SELECT * FROM trades WHERE id = 999"
        hash1 = analyzer.get_query_hash(query1)
        hash2 = analyzer.get_query_hash(query2)
        # Should be same after normalization (both become id = ?)
        assert hash1 == hash2

    async def test_get_query_hash_different_queries(self, analyzer):
        """Test that different queries produce different hashes."""
        query1 = "SELECT * FROM trades WHERE id = 1"
        query2 = "SELECT * FROM politicians WHERE id = 1"
        hash1 = analyzer.get_query_hash(query1)
        hash2 = analyzer.get_query_hash(query2)
        assert hash1 != hash2

    async def test_get_query_hash_length(self, analyzer):
        """Test that hash is 12 characters."""
        query = "SELECT * FROM trades"
        hash_value = analyzer.get_query_hash(query)
        assert len(hash_value) == 12

    async def test_record_query_first_time(self, analyzer):
        """Test recording a query for the first time."""
        query = "SELECT * FROM trades WHERE id = 1"
        execution_time = 0.5

        analyzer.record_query(query, execution_time)

        assert len(analyzer.query_stats) == 1
        query_hash = analyzer.get_query_hash(query)
        stats = analyzer.query_stats[query_hash]

        assert stats['execution_count'] == 1
        assert stats['total_time'] == 0.5
        assert stats['avg_time'] == 0.5
        assert stats['max_time'] == 0.5
        assert stats['min_time'] == 0.5

    async def test_record_query_multiple_times(self, analyzer):
        """Test recording same query multiple times."""
        query = "SELECT * FROM trades WHERE id = 1"

        analyzer.record_query(query, 0.1)
        analyzer.record_query(query, 0.3)
        analyzer.record_query(query, 0.2)

        query_hash = analyzer.get_query_hash(query)
        stats = analyzer.query_stats[query_hash]

        assert stats['execution_count'] == 3
        assert stats['total_time'] == 0.6
        assert stats['avg_time'] == 0.2
        assert stats['max_time'] == 0.3
        assert stats['min_time'] == 0.1

    async def test_record_query_slow_query_detection(self, analyzer):
        """Test slow query detection."""
        query = "SELECT * FROM trades WHERE id = 1"
        slow_time = 2.5  # Above 1.0 threshold

        analyzer.record_query(query, slow_time)

        assert len(analyzer.slow_queries) == 1
        slow_query = analyzer.slow_queries[0]
        assert slow_query['execution_time'] == 2.5
        assert query in slow_query['query_text']

    async def test_record_query_fast_query_not_recorded(self, analyzer):
        """Test that fast queries are not recorded as slow."""
        query = "SELECT * FROM trades WHERE id = 1"
        fast_time = 0.5  # Below 1.0 threshold

        analyzer.record_query(query, fast_time)

        assert len(analyzer.slow_queries) == 0

    async def test_record_query_threshold_boundary(self, analyzer):
        """Test query at exactly the threshold."""
        query = "SELECT * FROM trades WHERE id = 1"
        threshold_time = 1.0

        analyzer.record_query(query, threshold_time)

        # Exactly at threshold should not be recorded
        assert len(analyzer.slow_queries) == 0

        # Slightly above should be recorded
        analyzer.record_query(query, 1.001)
        assert len(analyzer.slow_queries) == 1

    async def test_record_multiple_different_queries(self, analyzer):
        """Test recording multiple different queries."""
        query1 = "SELECT * FROM trades"
        query2 = "SELECT * FROM politicians"
        query3 = "SELECT * FROM users"

        analyzer.record_query(query1, 0.1)
        analyzer.record_query(query2, 0.2)
        analyzer.record_query(query3, 0.3)

        assert len(analyzer.query_stats) == 3

    async def test_record_query_with_params(self, analyzer):
        """Test recording query with parameters."""
        query = "SELECT * FROM trades WHERE id = ?"
        params = {"id": 123}

        analyzer.record_query(query, 0.5, params)

        assert len(analyzer.query_stats) == 1

    async def test_slow_query_with_traceback(self, analyzer):
        """Test slow query recording includes timestamp."""
        query = "SELECT * FROM trades"
        analyzer.record_query(query, 2.0)

        slow_query = analyzer.slow_queries[0]
        assert 'executed_at' in slow_query
        # Check that timestamp is ISO format
        datetime.fromisoformat(slow_query['executed_at'])

    async def test_query_stats_last_executed(self, analyzer):
        """Test that last_executed is updated."""
        query = "SELECT * FROM trades WHERE id = 1"

        analyzer.record_query(query, 0.1)
        query_hash = analyzer.get_query_hash(query)
        first_time = analyzer.query_stats[query_hash]['last_executed']

        import time
        time.sleep(0.01)

        analyzer.record_query(query, 0.2)
        second_time = analyzer.query_stats[query_hash]['last_executed']

        # Timestamps should be different
        assert second_time >= first_time

    async def test_custom_slow_query_threshold(self):
        """Test creating analyzer with custom threshold."""
        analyzer = QueryAnalyzer()
        analyzer.slow_query_threshold = 0.5

        query = "SELECT * FROM trades"
        analyzer.record_query(query, 0.6)  # Above custom threshold

        assert len(analyzer.slow_queries) == 1


class TestQueryStats:
    """Test cases for QueryStats dataclass."""

    async def test_query_stats_creation(self):
        """Test creating QueryStats instance."""
        stats = QueryStats(
            query_hash="abc123",
            query_text="SELECT * FROM trades",
            execution_count=10,
            total_time=5.0,
            avg_time=0.5,
            max_time=1.2,
            min_time=0.1,
            last_executed="2024-01-01T00:00:00"
        )

        assert stats.query_hash == "abc123"
        assert stats.execution_count == 10
        assert stats.avg_time == 0.5

    async def test_query_stats_to_dict(self):
        """Test converting QueryStats to dict."""
        stats = QueryStats(
            query_hash="abc123",
            query_text="SELECT * FROM trades",
            execution_count=5,
            total_time=2.5,
            avg_time=0.5,
            max_time=1.0,
            min_time=0.2,
            last_executed="2024-01-01T00:00:00"
        )

        stats_dict = stats.to_dict()

        assert isinstance(stats_dict, dict)
        assert stats_dict['query_hash'] == "abc123"
        assert stats_dict['execution_count'] == 5
        assert stats_dict['avg_time'] == 0.5


class TestSlowQuery:
    """Test cases for SlowQuery dataclass."""

    async def test_slow_query_creation(self):
        """Test creating SlowQuery instance."""
        slow_query = SlowQuery(
            query_text="SELECT * FROM large_table",
            execution_time=3.5,
            executed_at="2024-01-01T00:00:00",
            params={"limit": 1000},
            traceback="..."
        )

        assert slow_query.query_text == "SELECT * FROM large_table"
        assert slow_query.execution_time == 3.5
        assert slow_query.params == {"limit": 1000}

    async def test_slow_query_optional_fields(self):
        """Test SlowQuery with optional fields."""
        slow_query = SlowQuery(
            query_text="SELECT * FROM trades",
            execution_time=2.0,
            executed_at="2024-01-01T00:00:00"
        )

        assert slow_query.params is None
        assert slow_query.traceback is None

    async def test_slow_query_to_dict(self):
        """Test converting SlowQuery to dict."""
        slow_query = SlowQuery(
            query_text="SELECT * FROM trades",
            execution_time=2.5,
            executed_at="2024-01-01T00:00:00"
        )

        slow_dict = slow_query.to_dict()

        assert isinstance(slow_dict, dict)
        assert slow_dict['query_text'] == "SELECT * FROM trades"
        assert slow_dict['execution_time'] == 2.5


class TestIndexRecommendation:
    """Test cases for IndexRecommendation dataclass."""

    async def test_index_recommendation_creation(self):
        """Test creating IndexRecommendation instance."""
        rec = IndexRecommendation(
            table_name="trades",
            columns=["politician_id", "transaction_date"],
            reason="Frequently queried together in WHERE clause",
            estimated_impact="high",
            create_statement="CREATE INDEX idx_trades_politician_date ON trades(politician_id, transaction_date)"
        )

        assert rec.table_name == "trades"
        assert rec.columns == ["politician_id", "transaction_date"]
        assert rec.estimated_impact == "high"

    async def test_index_recommendation_to_dict(self):
        """Test converting IndexRecommendation to dict."""
        rec = IndexRecommendation(
            table_name="politicians",
            columns=["state", "party"],
            reason="Filtering by state and party",
            estimated_impact="medium",
            create_statement="CREATE INDEX idx_politicians_state_party ON politicians(state, party)"
        )

        rec_dict = rec.to_dict()

        assert isinstance(rec_dict, dict)
        assert rec_dict['table_name'] == "politicians"
        assert rec_dict['estimated_impact'] == "medium"
        assert len(rec_dict['columns']) == 2

    async def test_index_recommendation_impact_levels(self):
        """Test different impact levels."""
        impacts = ["high", "medium", "low"]

        for impact in impacts:
            rec = IndexRecommendation(
                table_name="test",
                columns=["col1"],
                reason="test",
                estimated_impact=impact,
                create_statement="CREATE INDEX..."
            )
            assert rec.estimated_impact == impact
