"""Pattern detection service."""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.patterns import (
    CalendarEffectsDetector,
    Pattern,
    PatternOccurrence as PatternOccurrenceData,
    SARIMADetector,
)
from app.models.pattern import PatternModel
from app.models.pattern_occurrence import PatternOccurrence


class PatternDetectionService:
    """
    Service for detecting and managing cyclical patterns.

    Orchestrates pattern detection algorithms, stores results in database,
    and manages pattern lifecycle (validation, deactivation, updates).
    """

    def __init__(self):
        """Initialize pattern detection service."""
        # Initialize detectors with default parameters
        self.sarima_detector = SARIMADetector(
            min_seasonal_strength=0.3,
            min_occurrences=5,
            min_years=3.0,
            min_p_value=0.05,
            min_wfe=0.5,
        )

        self.calendar_detector = CalendarEffectsDetector(
            effects_to_test=['january', 'monday', 'turn_of_month'],
            min_occurrences=5,
            min_years=3.0,
            min_p_value=0.05,
            min_wfe=0.5,
        )

    async def detect_patterns_for_ticker(
        self,
        ticker: str,
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        run_sarima: bool = True,
        run_calendar: bool = True,
    ) -> dict:
        """
        Detect all patterns for a given ticker.

        Args:
            ticker: Stock ticker symbol
            db: Database session
            start_date: Start date for analysis (None = 10 years ago)
            end_date: End date for analysis (None = today)
            run_sarima: Whether to run SARIMA detector
            run_calendar: Whether to run calendar effects detector

        Returns:
            Dict with detection results and statistics
        """
        detected_patterns = []
        errors = []

        # Run SARIMA detection
        if run_sarima:
            try:
                sarima_patterns = await self.sarima_detector.detect(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                )
                detected_patterns.extend(sarima_patterns)
            except Exception as e:
                errors.append({
                    'detector': 'SARIMA',
                    'error': str(e),
                })

        # Run Calendar Effects detection
        if run_calendar:
            try:
                calendar_patterns = await self.calendar_detector.detect(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                )
                detected_patterns.extend(calendar_patterns)
            except Exception as e:
                errors.append({
                    'detector': 'CalendarEffects',
                    'error': str(e),
                })

        # Store patterns in database
        stored_count = 0
        updated_count = 0

        for pattern in detected_patterns:
            try:
                # Check if pattern already exists
                existing = await self._get_existing_pattern(
                    db=db,
                    pattern_id=pattern.pattern_id,
                )

                if existing:
                    # Update existing pattern
                    await self._update_pattern(db=db, existing=existing, new_data=pattern)
                    updated_count += 1
                else:
                    # Store new pattern
                    await self._store_pattern(db=db, pattern=pattern)
                    stored_count += 1

            except Exception as e:
                errors.append({
                    'detector': pattern.pattern_type.value,
                    'pattern_id': pattern.pattern_id,
                    'error': str(e),
                })

        await db.commit()

        return {
            'ticker': ticker,
            'detected': len(detected_patterns),
            'stored_new': stored_count,
            'updated': updated_count,
            'errors': errors,
        }

    async def _get_existing_pattern(
        self,
        db: AsyncSession,
        pattern_id: str,
    ) -> Optional[PatternModel]:
        """Get existing pattern from database."""
        query = select(PatternModel).where(PatternModel.pattern_id == pattern_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _store_pattern(
        self,
        db: AsyncSession,
        pattern: Pattern,
    ) -> PatternModel:
        """
        Store detected pattern in database.

        Args:
            db: Database session
            pattern: Detected pattern

        Returns:
            Stored pattern model
        """
        # Create pattern model
        pattern_model = PatternModel(
            id=uuid.uuid4(),
            pattern_id=pattern.pattern_id,
            pattern_type=pattern.pattern_type.value,
            name=pattern.name,
            description=pattern.description,
            ticker=pattern.ticker,
            sector=pattern.sector,
            market_cap=pattern.market_cap,
            cycle_length_days=pattern.cycle_length_days,
            frequency=pattern.frequency.value if pattern.frequency else None,
            next_occurrence=pattern.next_occurrence,
            window_start_day=pattern.window_start_day,
            window_end_day=pattern.window_end_day,
            validation_metrics=self._serialize_validation_metrics(
                pattern.validation_metrics
            ),
            reliability_score=pattern.reliability_score,
            confidence=pattern.confidence,
            first_detected=pattern.first_detected,
            last_validated=pattern.last_validated,
            economic_rationale=pattern.economic_rationale,
            risk_factors=pattern.risk_factors,
            politician_correlation=pattern.politician_correlation,
            recent_politician_activity=pattern.recent_politician_activity,
            detected_at=pattern.detected_at,
            detector_version=pattern.detector_version,
            parameters=pattern.parameters,
            is_active=True,
        )

        db.add(pattern_model)
        await db.flush()

        # Store occurrences
        for occurrence in pattern.historical_occurrences:
            occurrence_model = self._create_occurrence_model(
                pattern_id=pattern_model.id,
                occurrence=occurrence,
            )
            db.add(occurrence_model)

        return pattern_model

    async def _update_pattern(
        self,
        db: AsyncSession,
        existing: PatternModel,
        new_data: Pattern,
    ) -> PatternModel:
        """
        Update existing pattern with new validation data.

        Args:
            db: Database session
            existing: Existing pattern model
            new_data: New pattern data

        Returns:
            Updated pattern model
        """
        # Update metrics
        existing.validation_metrics = self._serialize_validation_metrics(
            new_data.validation_metrics
        )
        existing.reliability_score = new_data.reliability_score
        existing.confidence = new_data.confidence
        existing.last_validated = date.today()
        existing.next_occurrence = new_data.next_occurrence
        existing.updated_at = datetime.utcnow()

        # Update politician correlation if available
        if new_data.politician_correlation is not None:
            existing.politician_correlation = new_data.politician_correlation
            existing.recent_politician_activity = new_data.recent_politician_activity

        # Check if pattern should be deactivated
        if new_data.reliability_score < 50 or (
            new_data.validation_metrics
            and new_data.validation_metrics.walk_forward_efficiency < 0.3
        ):
            existing.is_active = False

        return existing

    def _serialize_validation_metrics(
        self,
        metrics: Optional[any],
    ) -> dict:
        """Serialize validation metrics to dict."""
        if metrics is None:
            return {}

        return {
            'p_value': metrics.p_value,
            'effect_size': metrics.effect_size,
            'statistical_power': metrics.statistical_power,
            'walk_forward_efficiency': metrics.walk_forward_efficiency,
            'in_sample_return': metrics.in_sample_return,
            'out_sample_return': metrics.out_sample_return,
            'consistency_score': metrics.consistency_score,
            'sample_size': metrics.sample_size,
            'years_of_data': metrics.years_of_data,
            'recent_performance': metrics.recent_performance,
            'last_occurrence_date': metrics.last_occurrence_date.isoformat()
            if metrics.last_occurrence_date
            else None,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'win_rate': metrics.win_rate,
        }

    def _create_occurrence_model(
        self,
        pattern_id: uuid.UUID,
        occurrence: PatternOccurrenceData,
    ) -> PatternOccurrence:
        """Create occurrence model from occurrence data."""
        return PatternOccurrence(
            id=uuid.uuid4(),
            pattern_id=pattern_id,
            start_date=occurrence.start_date,
            end_date=occurrence.end_date,
            return_pct=occurrence.return_pct,
            confidence=occurrence.confidence,
            volume_change=occurrence.volume_change,
            notes=occurrence.notes,
        )

    async def revalidate_pattern(
        self,
        pattern_id: str,
        db: AsyncSession,
    ) -> dict:
        """
        Revalidate an existing pattern with latest data.

        Args:
            pattern_id: Pattern ID to revalidate
            db: Database session

        Returns:
            Dict with revalidation results
        """
        # Get existing pattern
        existing = await self._get_existing_pattern(db=db, pattern_id=pattern_id)

        if not existing:
            return {
                'success': False,
                'error': 'Pattern not found',
            }

        # Re-run detection for this pattern's ticker
        ticker = existing.ticker
        if not ticker:
            return {
                'success': False,
                'error': 'Pattern has no ticker',
            }

        # Determine which detector to use
        run_sarima = existing.pattern_type == 'seasonal'
        run_calendar = existing.pattern_type == 'calendar'

        result = await self.detect_patterns_for_ticker(
            ticker=ticker,
            db=db,
            run_sarima=run_sarima,
            run_calendar=run_calendar,
        )

        return {
            'success': True,
            'pattern_id': pattern_id,
            'result': result,
        }

    async def deactivate_pattern(
        self,
        pattern_id: str,
        db: AsyncSession,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Deactivate a pattern (e.g., if it's no longer valid).

        Args:
            pattern_id: Pattern ID to deactivate
            db: Database session
            reason: Reason for deactivation

        Returns:
            Dict with deactivation result
        """
        existing = await self._get_existing_pattern(db=db, pattern_id=pattern_id)

        if not existing:
            return {
                'success': False,
                'error': 'Pattern not found',
            }

        existing.is_active = False
        existing.updated_at = datetime.utcnow()

        await db.commit()

        return {
            'success': True,
            'pattern_id': pattern_id,
            'reason': reason,
        }

    async def get_tickers_for_detection(
        self,
        db: AsyncSession,
        limit: int = 50,
    ) -> list[str]:
        """
        Get list of tickers that should have pattern detection run.

        Returns tickers from the most actively traded stocks by politicians.

        Args:
            db: Database session
            limit: Maximum number of tickers to return

        Returns:
            List of ticker symbols
        """
        from sqlalchemy import func
        from app.models.trade import Trade

        # Get most traded tickers
        query = (
            select(Trade.ticker, func.count(Trade.id).label('trade_count'))
            .group_by(Trade.ticker)
            .order_by(func.count(Trade.id).desc())
            .limit(limit)
        )

        result = await db.execute(query)
        tickers = [row[0] for row in result]

        return tickers
