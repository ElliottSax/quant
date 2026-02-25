"""
Database Optimization Service

Provides comprehensive database optimization features:
- Query analysis and profiling
- Slow query detection
- Index recommendations
- Connection pool monitoring
- Database statistics
- Query plan analysis
"""

import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict

from sqlalchemy import text, inspect, Table, MetaData, Index
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine

from app.core.logging import get_logger
from app.core.cache import cache_manager

logger = get_logger(__name__)


@dataclass
class QueryStats:
    """Statistics for a query"""
    query_hash: str
    query_text: str
    execution_count: int
    total_time: float
    avg_time: float
    max_time: float
    min_time: float
    last_executed: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SlowQuery:
    """Slow query information"""
    query_text: str
    execution_time: float
    executed_at: str
    params: Optional[dict] = None
    traceback: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IndexRecommendation:
    """Index recommendation"""
    table_name: str
    columns: List[str]
    reason: str
    estimated_impact: str  # "high", "medium", "low"
    create_statement: str

    def to_dict(self) -> dict:
        return asdict(self)


class QueryAnalyzer:
    """
    Analyzes SQL queries for performance optimization.
    """

    def __init__(self):
        # Query statistics: {query_hash: QueryStats}
        self.query_stats: Dict[str, Dict] = {}
        # Slow queries: List[SlowQuery]
        self.slow_queries: List[Dict] = []
        self.slow_query_threshold = 1.0  # 1 second

    def normalize_query(self, query: str) -> str:
        """
        Normalize query for pattern matching.

        Replaces literal values with placeholders to group similar queries.
        """
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query.strip())

        # Replace numbers with ?
        query = re.sub(r'\b\d+\b', '?', query)

        # Replace string literals
        query = re.sub(r"'[^']*'", '?', query)

        # Replace UUID patterns
        query = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '?',
            query,
            flags=re.IGNORECASE
        )

        return query

    def get_query_hash(self, query: str) -> str:
        """Generate hash for query"""
        import hashlib
        normalized = self.normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    def record_query(
        self,
        query: str,
        execution_time: float,
        params: Optional[dict] = None
    ):
        """Record query execution"""
        query_hash = self.get_query_hash(query)

        # Update statistics
        if query_hash in self.query_stats:
            stats = self.query_stats[query_hash]
            stats['execution_count'] += 1
            stats['total_time'] += execution_time
            stats['avg_time'] = stats['total_time'] / stats['execution_count']
            stats['max_time'] = max(stats['max_time'], execution_time)
            stats['min_time'] = min(stats['min_time'], execution_time)
            stats['last_executed'] = datetime.utcnow().isoformat()
        else:
            normalized = self.normalize_query(query)
            self.query_stats[query_hash] = {
                'query_hash': query_hash,
                'query_text': normalized,
                'execution_count': 1,
                'total_time': execution_time,
                'avg_time': execution_time,
                'max_time': execution_time,
                'min_time': execution_time,
                'last_executed': datetime.utcnow().isoformat()
            }

        # Record slow queries
        if execution_time > self.slow_query_threshold:
            self.slow_queries.append({
                'query_text': query,
                'execution_time': execution_time,
                'executed_at': datetime.utcnow().isoformat(),
                'params': params
            })

            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]

            logger.warning(
                f"Slow query detected ({execution_time:.3f}s): {query[:100]}..."
            )

    def get_slowest_queries(self, limit: int = 10) -> List[Dict]:
        """Get slowest queries by average time"""
        sorted_stats = sorted(
            self.query_stats.values(),
            key=lambda x: x['avg_time'],
            reverse=True
        )
        return sorted_stats[:limit]

    def get_most_frequent_queries(self, limit: int = 10) -> List[Dict]:
        """Get most frequently executed queries"""
        sorted_stats = sorted(
            self.query_stats.values(),
            key=lambda x: x['execution_count'],
            reverse=True
        )
        return sorted_stats[:limit]

    def get_stats_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.query_stats:
            return {
                'total_queries': 0,
                'unique_queries': 0,
                'slow_queries': 0,
                'avg_execution_time': 0
            }

        total_count = sum(s['execution_count'] for s in self.query_stats.values())
        total_time = sum(s['total_time'] for s in self.query_stats.values())

        return {
            'total_queries': total_count,
            'unique_queries': len(self.query_stats),
            'slow_queries': len(self.slow_queries),
            'avg_execution_time': total_time / total_count if total_count > 0 else 0
        }


class IndexRecommender:
    """
    Recommends indexes based on query patterns.
    """

    def __init__(self):
        # Track columns used in WHERE clauses: {table: {column: count}}
        self.where_columns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # Track columns used in JOIN clauses
        self.join_columns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # Track columns used in ORDER BY clauses
        self.order_columns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def analyze_query(self, query: str):
        """Analyze query for index opportunities"""
        query_upper = query.upper()

        # Extract WHERE clauses
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)', query_upper, re.IGNORECASE)
        if where_match:
            where_clause = where_match.group(1)
            self._extract_columns(where_clause, self.where_columns)

        # Extract JOIN clauses
        join_matches = re.findall(r'JOIN\s+(\w+)\s+ON\s+(.+?)(?:WHERE|JOIN|ORDER|GROUP|LIMIT|$)', query_upper, re.IGNORECASE)
        for table, join_clause in join_matches:
            self._extract_columns(join_clause, self.join_columns, table.lower())

        # Extract ORDER BY clauses
        order_match = re.search(r'ORDER\s+BY\s+(.+?)(?:LIMIT|$)', query_upper, re.IGNORECASE)
        if order_match:
            order_clause = order_match.group(1)
            self._extract_columns(order_clause, self.order_columns)

    def _extract_columns(self, clause: str, storage: Dict, table: Optional[str] = None):
        """Extract column references from SQL clause"""
        # Match table.column or just column
        column_pattern = r'(?:(\w+)\.)?(\w+)'
        matches = re.findall(column_pattern, clause)

        for table_name, column_name in matches:
            if column_name.upper() in ('AND', 'OR', 'ON', 'IN', 'IS', 'NULL', 'NOT'):
                continue

            tbl = table_name.lower() if table_name else (table or 'unknown')
            col = column_name.lower()
            storage[tbl][col] += 1

    async def get_recommendations(
        self,
        db: AsyncSession,
        min_usage_count: int = 5
    ) -> List[IndexRecommendation]:
        """Generate index recommendations"""
        recommendations = []

        # Get existing indexes
        existing_indexes = await self._get_existing_indexes(db)

        # Recommend indexes for WHERE columns
        for table, columns in self.where_columns.items():
            for column, count in columns.items():
                if count >= min_usage_count:
                    if not self._has_index(existing_indexes, table, [column]):
                        recommendations.append(IndexRecommendation(
                            table_name=table,
                            columns=[column],
                            reason=f"Column used in WHERE clause {count} times",
                            estimated_impact="high" if count > 20 else "medium",
                            create_statement=f"CREATE INDEX idx_{table}_{column} ON {table}({column});"
                        ))

        # Recommend composite indexes for JOINs
        for table, columns in self.join_columns.items():
            if len(columns) >= 2:
                cols = sorted(columns.keys())
                if not self._has_index(existing_indexes, table, cols):
                    recommendations.append(IndexRecommendation(
                        table_name=table,
                        columns=cols,
                        reason=f"Columns used in JOIN operations",
                        estimated_impact="high",
                        create_statement=f"CREATE INDEX idx_{table}_{'_'.join(cols)} ON {table}({', '.join(cols)});"
                    ))

        # Recommend indexes for ORDER BY
        for table, columns in self.order_columns.items():
            for column, count in columns.items():
                if count >= min_usage_count:
                    if not self._has_index(existing_indexes, table, [column]):
                        recommendations.append(IndexRecommendation(
                            table_name=table,
                            columns=[column],
                            reason=f"Column used in ORDER BY {count} times",
                            estimated_impact="medium",
                            create_statement=f"CREATE INDEX idx_{table}_{column} ON {table}({column});"
                        ))

        return recommendations

    async def _get_existing_indexes(self, db: AsyncSession) -> Dict[str, List[List[str]]]:
        """Get existing indexes from database"""
        # This would need to be implemented based on database type
        # For now, return empty dict
        return {}

    def _has_index(
        self,
        existing_indexes: Dict[str, List[List[str]]],
        table: str,
        columns: List[str]
    ) -> bool:
        """Check if index exists"""
        if table not in existing_indexes:
            return False

        for idx_cols in existing_indexes[table]:
            # Check if columns match or are prefix of existing index
            if columns == idx_cols[:len(columns)]:
                return True

        return False


class ConnectionPoolMonitor:
    """
    Monitor database connection pool health.
    """

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        pool = self.engine.pool

        stats = {
            'pool_size': 0,
            'checked_out': 0,
            'overflow': 0,
            'checked_in': 0,
            'total_connections': 0
        }

        if isinstance(pool, QueuePool):
            stats.update({
                'pool_size': pool.size(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'checked_in': pool.size() - pool.checkedout(),
                'total_connections': pool.size() + pool.overflow()
            })

        return stats

    def check_pool_health(self) -> Dict[str, Any]:
        """Check connection pool health"""
        stats = self.get_pool_stats()

        health = {
            'status': 'healthy',
            'warnings': [],
            'stats': stats
        }

        # Check for high utilization
        if stats['total_connections'] > 0:
            utilization = stats['checked_out'] / stats['total_connections']

            if utilization > 0.9:
                health['status'] = 'critical'
                health['warnings'].append(
                    f"Connection pool is {utilization*100:.1f}% utilized"
                )
            elif utilization > 0.7:
                health['status'] = 'warning'
                health['warnings'].append(
                    f"Connection pool is {utilization*100:.1f}% utilized"
                )

        # Check for overflow
        if stats['overflow'] > 0:
            health['warnings'].append(
                f"Connection pool overflow active: {stats['overflow']} connections"
            )

        return health


class DatabaseOptimizer:
    """
    Main database optimization service.

    Coordinates query analysis, index recommendations, and monitoring.
    """

    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.query_analyzer = QueryAnalyzer()
        self.index_recommender = IndexRecommender()
        self.pool_monitor = ConnectionPoolMonitor(engine)

    async def analyze_query(self, query: str, execution_time: float, params: Optional[dict] = None):
        """Analyze executed query"""
        self.query_analyzer.record_query(query, execution_time, params)
        self.index_recommender.analyze_query(query)

    async def get_optimization_report(self, db: AsyncSession) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        return {
            'generated_at': datetime.utcnow().isoformat(),
            'query_stats': self.query_analyzer.get_stats_summary(),
            'slowest_queries': self.query_analyzer.get_slowest_queries(10),
            'most_frequent_queries': self.query_analyzer.get_most_frequent_queries(10),
            'recent_slow_queries': self.query_analyzer.slow_queries[-10:],
            'index_recommendations': [
                rec.to_dict()
                for rec in await self.index_recommender.get_recommendations(db)
            ],
            'connection_pool': self.pool_monitor.check_pool_health()
        }

    async def get_table_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get database table statistics"""
        try:
            # Get table sizes (PostgreSQL specific)
            result = await db.execute(text("""
                SELECT
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                    pg_total_relation_size(schemaname||'.'||tablename) AS bytes
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """))

            tables = []
            for row in result:
                tables.append({
                    'schema': row[0],
                    'table': row[1],
                    'size': row[2],
                    'bytes': row[3]
                })

            return {
                'tables': tables,
                'total_tables': len(tables)
            }

        except Exception as e:
            logger.error(f"Failed to get table statistics: {e}")
            return {'error': str(e)}

    async def get_query_plan(self, db: AsyncSession, query: str) -> Dict[str, Any]:
        """Get query execution plan"""
        try:
            # EXPLAIN ANALYZE
            result = await db.execute(text(f"EXPLAIN ANALYZE {query}"))
            plan_lines = [row[0] for row in result]

            return {
                'query': query,
                'plan': '\n'.join(plan_lines),
                'formatted': plan_lines
            }

        except Exception as e:
            logger.error(f"Failed to get query plan: {e}")
            return {'error': str(e)}


# Global instance
_optimizer: Optional[DatabaseOptimizer] = None


def init_database_optimizer(engine: AsyncEngine):
    """Initialize database optimizer"""
    global _optimizer
    _optimizer = DatabaseOptimizer(engine)
    logger.info("Database optimizer initialized")


def get_database_optimizer() -> DatabaseOptimizer:
    """Get database optimizer instance"""
    if _optimizer is None:
        raise RuntimeError("Database optimizer not initialized")
    return _optimizer
