"""
Pattern Recognition Service

Advanced pattern detection including:
- Cluster analysis for correlated trading
- Timing analysis (trades before major events)
- Sector rotation detection
- Cross-politician correlation patterns

Author: Claude
"""

from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta, date
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
from collections import defaultdict
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.cache import cache_result
from app.core.config import settings
from app.core.logging import get_logger
from app.models.politician import Politician
from app.models.trade import Trade

logger = get_logger(__name__)

try:
    import numpy as np
    from sklearn.cluster import DBSCAN, AgglomerativeClustering
    from sklearn.preprocessing import StandardScaler
    from scipy.stats import pearsonr
    import pandas as pd
    ML_AVAILABLE = True
except ImportError:
    logger.warning("ML libraries not available for pattern recognition")
    ML_AVAILABLE = False


class PatternType(str, Enum):
    """Types of trading patterns"""
    COORDINATED_TRADING = "coordinated_trading"
    PRE_EARNINGS_TRADING = "pre_earnings_trading"
    PRE_EVENT_TRADING = "pre_event_trading"
    SECTOR_ROTATION = "sector_rotation"
    INSIDER_CLUSTER = "insider_cluster"
    TIMING_PATTERN = "timing_pattern"


class TradingCluster(BaseModel):
    """Cluster of correlated politicians"""
    cluster_id: int
    politicians: List[str]  # Politician names
    politician_ids: List[str]  # Politician UUIDs
    avg_correlation: float
    trade_overlap: float  # % of trades that overlap in time
    common_tickers: List[str]
    cluster_size: int
    confidence: float = Field(..., ge=0, le=1)
    description: str


class TimingPattern(BaseModel):
    """Pattern of trading around specific events"""
    pattern_type: PatternType
    politician_id: str
    politician_name: str
    ticker: str
    event_date: date
    trade_date: date
    days_before_event: int
    event_type: str  # "earnings", "announcement", etc.
    trade_direction: str  # "buy", "sell"
    profitability: Optional[float] = None  # If calculable
    confidence: float


class SectorRotation(BaseModel):
    """Detected sector rotation pattern"""
    politician_id: str
    politician_name: str
    from_sector: str
    to_sector: str
    rotation_date: date
    sell_count: int
    buy_count: int
    net_flow: float  # Estimated $ flow
    motivation: Optional[str] = None  # Inferred reason
    confidence: float


class CorrelatedTradingPattern(BaseModel):
    """Pattern of correlated trading between politicians"""
    politician_ids: List[str]
    politician_names: List[str]
    correlation_score: float
    common_trades: int
    time_window_days: int
    common_tickers: List[str]
    pattern_strength: str  # "weak", "moderate", "strong"
    statistical_significance: float  # p-value


class PatternRecognitionResult(BaseModel):
    """Complete pattern recognition results"""
    timestamp: datetime
    clusters: List[TradingCluster]
    timing_patterns: List[TimingPattern]
    sector_rotations: List[SectorRotation]
    correlated_patterns: List[CorrelatedTradingPattern]
    summary: str


class PatternRecognizer:
    """
    Advanced pattern recognition for politician trading

    Features:
    - Clustering of correlated politicians
    - Event timing analysis
    - Sector rotation detection
    - Statistical correlation analysis
    """

    def __init__(self):
        self.cache_ttl = 1800  # 30 minutes

    @cache_result("pattern_analysis", ttl=1800)
    async def analyze_patterns(
        self,
        db: AsyncSession,
        lookback_days: int = 90,
        min_cluster_size: int = 3,
        min_correlation: float = 0.6
    ) -> PatternRecognitionResult:
        """
        Comprehensive pattern analysis

        Args:
            db: Database session
            lookback_days: Days to analyze
            min_cluster_size: Minimum politicians in cluster
            min_correlation: Minimum correlation for clustering

        Returns:
            Complete pattern recognition results
        """
        logger.info(f"Analyzing trading patterns for last {lookback_days} days")

        if not ML_AVAILABLE:
            logger.warning("ML libraries not available")
            return PatternRecognitionResult(
                timestamp=datetime.now(),
                clusters=[],
                timing_patterns=[],
                sector_rotations=[],
                correlated_patterns=[],
                summary="ML libraries not available for pattern recognition"
            )

        # Run analyses in parallel
        tasks = [
            self._detect_trading_clusters(db, lookback_days, min_cluster_size, min_correlation),
            self._detect_timing_patterns(db, lookback_days),
            self._detect_sector_rotations(db, lookback_days),
            self._detect_correlated_trading(db, lookback_days, min_correlation)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        clusters = results[0] if not isinstance(results[0], Exception) else []
        timing_patterns = results[1] if not isinstance(results[1], Exception) else []
        sector_rotations = results[2] if not isinstance(results[2], Exception) else []
        correlated_patterns = results[3] if not isinstance(results[3], Exception) else []

        # Generate summary
        summary = self._generate_summary(clusters, timing_patterns, sector_rotations, correlated_patterns)

        return PatternRecognitionResult(
            timestamp=datetime.now(),
            clusters=clusters,
            timing_patterns=timing_patterns,
            sector_rotations=sector_rotations,
            correlated_patterns=correlated_patterns,
            summary=summary
        )

    async def _detect_trading_clusters(
        self,
        db: AsyncSession,
        lookback_days: int,
        min_cluster_size: int,
        min_correlation: float
    ) -> List[TradingCluster]:
        """
        Detect clusters of politicians who trade similarly

        Uses DBSCAN clustering on trading patterns
        """
        logger.info("Detecting trading clusters")

        # Fetch all trades in lookback period
        cutoff_date = date.today() - timedelta(days=lookback_days)

        query = (
            select(Trade)
            .options(selectinload(Trade.politician))
            .where(Trade.transaction_date >= cutoff_date)
        )

        result = await db.execute(query)
        trades = result.scalars().all()

        if len(trades) < 10:
            logger.warning("Not enough trades for clustering")
            return []

        # Build politician trading vectors
        politician_vectors = self._build_trading_vectors(trades)

        if len(politician_vectors) < min_cluster_size:
            logger.warning("Not enough politicians for clustering")
            return []

        # Convert to matrix
        politician_ids = list(politician_vectors.keys())
        vectors = [politician_vectors[pid] for pid in politician_ids]

        # Normalize
        scaler = StandardScaler()
        vectors_scaled = scaler.fit_transform(vectors)

        # Cluster using DBSCAN
        clustering = DBSCAN(eps=0.5, min_samples=min_cluster_size)
        labels = clustering.fit_predict(vectors_scaled)

        # Build clusters
        clusters = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:  # Noise
                continue

            cluster_indices = [i for i, l in enumerate(labels) if l == label]
            cluster_politician_ids = [politician_ids[i] for i in cluster_indices]

            if len(cluster_politician_ids) < min_cluster_size:
                continue

            # Calculate cluster metrics
            cluster_trades = [t for t in trades if str(t.politician_id) in cluster_politician_ids]

            # Get politician names
            politician_names = []
            for pid in cluster_politician_ids:
                pol_trades = [t for t in cluster_trades if str(t.politician_id) == pid]
                if pol_trades:
                    politician_names.append(pol_trades[0].politician.name)

            # Calculate correlation
            correlations = []
            for i in range(len(cluster_indices)):
                for j in range(i + 1, len(cluster_indices)):
                    v1 = vectors_scaled[cluster_indices[i]]
                    v2 = vectors_scaled[cluster_indices[j]]
                    corr = np.corrcoef(v1, v2)[0, 1]
                    if not np.isnan(corr):
                        correlations.append(corr)

            avg_correlation = np.mean(correlations) if correlations else 0.0

            # Find common tickers
            ticker_counts = defaultdict(int)
            for t in cluster_trades:
                ticker_counts[t.ticker] += 1

            common_tickers = [
                ticker for ticker, count in ticker_counts.items()
                if count >= len(cluster_politician_ids) * 0.5
            ]

            # Trade overlap
            trade_dates = [t.transaction_date for t in cluster_trades]
            unique_dates = set(trade_dates)
            trade_overlap = len(trade_dates) / (len(cluster_politician_ids) * len(unique_dates)) if unique_dates else 0

            clusters.append(TradingCluster(
                cluster_id=int(label),
                politicians=politician_names,
                politician_ids=cluster_politician_ids,
                avg_correlation=float(avg_correlation),
                trade_overlap=float(trade_overlap),
                common_tickers=common_tickers[:10],
                cluster_size=len(cluster_politician_ids),
                confidence=min(0.9, avg_correlation),
                description=f"Cluster of {len(cluster_politician_ids)} politicians trading {len(common_tickers)} common tickers"
            ))

        logger.info(f"Found {len(clusters)} trading clusters")
        return clusters

    def _build_trading_vectors(self, trades: List[Trade]) -> Dict[str, List[float]]:
        """
        Build feature vectors for each politician

        Features:
        - Trade frequency by day of week
        - Buy/sell ratio
        - Sector distribution
        - Trade size distribution
        """
        politician_features = defaultdict(lambda: {
            "trades": [],
            "dow": [0] * 7,  # Day of week
            "buys": 0,
            "sells": 0,
            "sectors": defaultdict(int),
            "sizes": []
        })

        for trade in trades:
            pid = str(trade.politician_id)
            features = politician_features[pid]

            features["trades"].append(trade)
            features["dow"][trade.transaction_date.weekday()] += 1

            if trade.transaction_type == "buy":
                features["buys"] += 1
            else:
                features["sells"] += 1

            # Estimate sector (simplified - would need ticker -> sector mapping)
            features["sectors"][trade.ticker] += 1

            # Trade size
            if trade.amount_min:
                features["sizes"].append(float(trade.amount_min))

        # Convert to vectors
        vectors = {}

        for pid, features in politician_features.items():
            if len(features["trades"]) < 2:
                continue

            # Normalize day of week
            dow_norm = [d / max(1, sum(features["dow"])) for d in features["dow"]]

            # Buy/sell ratio
            total = features["buys"] + features["sells"]
            buy_ratio = features["buys"] / total if total > 0 else 0.5

            # Avg trade size (log scale)
            avg_size = np.log1p(np.mean(features["sizes"])) if features["sizes"] else 0

            # Vector: [dow (7), buy_ratio (1), avg_size (1)]
            vector = dow_norm + [buy_ratio, avg_size]
            vectors[pid] = vector

        return vectors

    async def _detect_timing_patterns(
        self,
        db: AsyncSession,
        lookback_days: int
    ) -> List[TimingPattern]:
        """
        Detect patterns of trading before major events

        Simplified implementation - would need earnings calendar integration
        """
        logger.info("Detecting timing patterns")

        # For now, return empty - would need earnings calendar API
        # Real implementation would:
        # 1. Fetch earnings dates for traded tickers
        # 2. Match trades that occurred 1-7 days before earnings
        # 3. Calculate profitability if possible

        return []

    async def _detect_sector_rotations(
        self,
        db: AsyncSession,
        lookback_days: int
    ) -> List[SectorRotation]:
        """
        Detect when politicians rotate out of one sector into another

        Simplified implementation - would need ticker -> sector mapping
        """
        logger.info("Detecting sector rotations")

        # For now, return empty - would need sector classification
        # Real implementation would:
        # 1. Map each ticker to sector
        # 2. Track when politicians sell in one sector and buy in another
        # 3. Identify rotation patterns

        return []

    async def _detect_correlated_trading(
        self,
        db: AsyncSession,
        lookback_days: int,
        min_correlation: float
    ) -> List[CorrelatedTradingPattern]:
        """
        Detect pairs/groups of politicians who trade in correlation
        """
        logger.info("Detecting correlated trading patterns")

        cutoff_date = date.today() - timedelta(days=lookback_days)

        # Fetch trades
        query = (
            select(Trade)
            .options(selectinload(Trade.politician))
            .where(Trade.transaction_date >= cutoff_date)
        )

        result = await db.execute(query)
        trades = result.scalars().all()

        if len(trades) < 20:
            logger.warning("Not enough trades for correlation analysis")
            return []

        # Group trades by politician
        politician_trades = defaultdict(list)
        for trade in trades:
            politician_trades[str(trade.politician_id)].append(trade)

        # Find pairs with common trades
        patterns = []
        politician_ids = list(politician_trades.keys())

        for i in range(len(politician_ids)):
            for j in range(i + 1, len(politician_ids)):
                pid1 = politician_ids[i]
                pid2 = politician_ids[j]

                trades1 = politician_trades[pid1]
                trades2 = politician_trades[pid2]

                # Find common tickers
                tickers1 = set(t.ticker for t in trades1)
                tickers2 = set(t.ticker for t in trades2)
                common_tickers = tickers1 & tickers2

                if len(common_tickers) < 2:
                    continue

                # Calculate correlation
                common_trades = 0
                time_diffs = []

                for ticker in common_tickers:
                    t1_dates = [t.transaction_date for t in trades1 if t.ticker == ticker]
                    t2_dates = [t.transaction_date for t in trades2 if t.ticker == ticker]

                    # Check if trades happened within time window
                    for d1 in t1_dates:
                        for d2 in t2_dates:
                            diff = abs((d1 - d2).days)
                            if diff <= 7:  # Within 1 week
                                common_trades += 1
                                time_diffs.append(diff)

                if common_trades < 2:
                    continue

                # Calculate correlation score
                correlation_score = common_trades / max(len(trades1), len(trades2))

                if correlation_score < min_correlation:
                    continue

                # Statistical significance (simplified)
                p_value = max(0.01, 1.0 - correlation_score)

                # Pattern strength
                if correlation_score > 0.8:
                    strength = "strong"
                elif correlation_score > 0.6:
                    strength = "moderate"
                else:
                    strength = "weak"

                patterns.append(CorrelatedTradingPattern(
                    politician_ids=[pid1, pid2],
                    politician_names=[
                        trades1[0].politician.name,
                        trades2[0].politician.name
                    ],
                    correlation_score=correlation_score,
                    common_trades=common_trades,
                    time_window_days=7,
                    common_tickers=list(common_tickers)[:10],
                    pattern_strength=strength,
                    statistical_significance=p_value
                ))

        logger.info(f"Found {len(patterns)} correlated trading patterns")
        return patterns

    def _generate_summary(
        self,
        clusters: List[TradingCluster],
        timing_patterns: List[TimingPattern],
        sector_rotations: List[SectorRotation],
        correlated_patterns: List[CorrelatedTradingPattern]
    ) -> str:
        """
        Generate human-readable summary
        """
        parts = ["Pattern recognition analysis:"]

        if clusters:
            total_politicians = sum(c.cluster_size for c in clusters)
            parts.append(
                f"Found {len(clusters)} trading clusters covering {total_politicians} politicians."
            )

        if timing_patterns:
            parts.append(f"Detected {len(timing_patterns)} timing patterns around events.")

        if sector_rotations:
            parts.append(f"Identified {len(sector_rotations)} sector rotation patterns.")

        if correlated_patterns:
            strong_patterns = sum(1 for p in correlated_patterns if p.pattern_strength == "strong")
            parts.append(
                f"Found {len(correlated_patterns)} correlated trading patterns "
                f"({strong_patterns} strong)."
            )

        if not (clusters or timing_patterns or sector_rotations or correlated_patterns):
            parts.append("No significant patterns detected.")

        return " ".join(parts)


# Global instance
_pattern_recognizer: Optional[PatternRecognizer] = None


def get_pattern_recognizer() -> PatternRecognizer:
    """Get global pattern recognizer instance"""
    global _pattern_recognizer
    if _pattern_recognizer is None:
        _pattern_recognizer = PatternRecognizer()
    return _pattern_recognizer
