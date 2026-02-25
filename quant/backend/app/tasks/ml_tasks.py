"""Celery tasks for ML training and inference."""

from celery import Celery, Task
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pickle
import os

from app.core.config import settings
from app.core.ml_config import ml_settings
from app.ml.utils.mlflow_tracker import MLFlowTracker
from app.ml.utils.model_registry import ModelRegistry
from app.ml.cyclical import FourierCyclicalDetector, RegimeDetector, DynamicTimeWarpingMatcher
from app.ml.ensemble import EnsemblePredictor, MetaLearner
from app.ml.features.engineering import AdvancedFeatureEngineering
from app.ml.insights import InsightGenerator

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'ml_tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 4,  # 4 hours max
    task_soft_time_limit=3600 * 3,  # 3 hours soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
)


class MLTask(Task):
    """Base class for ML tasks with common functionality."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed: {exc}")
        # Could send alerts here

    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        logger.info(f"Task {task_id} completed successfully")


@celery_app.task(
    base=MLTask,
    name='ml_tasks.train_ensemble_model',
    bind=True
)
def train_ensemble_model(
    self,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    force_retrain: bool = False
) -> Dict[str, Any]:
    """
    Train the full ensemble model.

    Args:
        start_date: Start date for training data
        end_date: End date for training data
        force_retrain: Force retraining even if recent model exists

    Returns:
        Training results and metrics
    """
    logger.info("Starting ensemble model training")

    tracker = MLFlowTracker()
    registry = ModelRegistry()

    try:
        with tracker.start_run(f"ensemble_training_{datetime.now():%Y%m%d_%H%M%S}"):
            # Log parameters
            tracker.log_params({
                "start_date": start_date or "auto",
                "end_date": end_date or "auto",
                "force_retrain": force_retrain,
                "n_models": len(ml_settings.ENSEMBLE_MODELS),
            })

            # Load trade data
            trades_df = _load_trade_data(start_date, end_date)

            if trades_df.empty:
                logger.warning("No trade data available for training")
                return {
                    "status": "skipped",
                    "reason": "No trade data available",
                    "timestamp": datetime.now().isoformat()
                }

            # Get unique politicians
            politicians = trades_df['politician_id'].unique()
            logger.info(f"Training on {len(politicians)} politicians")

            # Initialize models
            fourier_detector = FourierCyclicalDetector(
                min_strength=0.1,
                min_confidence=ml_settings.FOURIER_MIN_PERIOD / 100
            )

            regime_detector = RegimeDetector(
                n_states=ml_settings.HMM_N_STATES,
                n_iter=ml_settings.HMM_N_ITERATIONS
            )

            dtw_matcher = DynamicTimeWarpingMatcher(
                similarity_threshold=ml_settings.DTW_MIN_SIMILARITY
            )

            ensemble_predictor = EnsemblePredictor()
            meta_learner = MetaLearner()

            # Train on each politician's data
            model_metrics = {
                "fourier": {"patterns_detected": 0, "avg_confidence": []},
                "hmm": {"regimes_detected": 0, "avg_duration": []},
                "dtw": {"matches_found": 0, "avg_similarity": []},
            }

            trained_count = 0

            for politician_id in politicians:
                try:
                    # Create trade frequency time series
                    trade_series = _create_trade_frequency_series(
                        trades_df, str(politician_id)
                    )

                    if len(trade_series) < 60:  # Need at least 60 days of data
                        continue

                    # Train Fourier detector
                    fourier_result = fourier_detector.detect_cycles(
                        trade_series.values,
                        sampling_rate='daily'
                    )

                    if fourier_result.get('dominant_cycles'):
                        model_metrics["fourier"]["patterns_detected"] += len(
                            fourier_result['dominant_cycles']
                        )
                        model_metrics["fourier"]["avg_confidence"].extend([
                            c['confidence'] for c in fourier_result['dominant_cycles']
                        ])

                    # Train HMM regime detector
                    returns = trade_series.pct_change().dropna()
                    if len(returns) >= 30:
                        hmm_result = regime_detector.fit_and_predict(returns.values)
                        model_metrics["hmm"]["regimes_detected"] += len(
                            hmm_result.get('regime_characteristics', {})
                        )
                        if hmm_result.get('expected_duration'):
                            model_metrics["hmm"]["avg_duration"].extend(
                                hmm_result['expected_duration']
                            )

                    # DTW pattern matching
                    if len(trade_series) >= 120:
                        dtw_matches = dtw_matcher.find_similar_patterns(
                            trade_series.values,
                            trade_series.values,
                            window_size=ml_settings.DTW_WINDOW_SIZE,
                            top_k=ml_settings.DTW_TOP_K
                        )
                        model_metrics["dtw"]["matches_found"] += len(dtw_matches)
                        if dtw_matches:
                            model_metrics["dtw"]["avg_similarity"].extend([
                                m['similarity_score'] for m in dtw_matches
                            ])

                    trained_count += 1

                except Exception as e:
                    logger.warning(f"Failed to train on politician {politician_id}: {e}")
                    continue

            # Aggregate metrics
            final_metrics = {
                "politicians_trained": trained_count,
                "fourier_patterns_total": model_metrics["fourier"]["patterns_detected"],
                "fourier_avg_confidence": (
                    np.mean(model_metrics["fourier"]["avg_confidence"])
                    if model_metrics["fourier"]["avg_confidence"] else 0
                ),
                "hmm_regimes_total": model_metrics["hmm"]["regimes_detected"],
                "hmm_avg_duration": (
                    np.mean(model_metrics["hmm"]["avg_duration"])
                    if model_metrics["hmm"]["avg_duration"] else 0
                ),
                "dtw_matches_total": model_metrics["dtw"]["matches_found"],
                "dtw_avg_similarity": (
                    np.mean(model_metrics["dtw"]["avg_similarity"])
                    if model_metrics["dtw"]["avg_similarity"] else 0
                ),
            }

            # Save trained models
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            _save_model(fourier_detector, "fourier_detector", version)
            _save_model(regime_detector, "regime_detector", version)
            _save_model(dtw_matcher, "dtw_matcher", version)
            _save_model(ensemble_predictor, "ensemble_predictor", version)
            _save_model(meta_learner, "meta_learner", version)

            # Register models in registry
            registry.register_model(
                "ensemble_model",
                version,
                final_metrics,
                ml_settings.MODEL_CACHE_DIR
            )

            # Log metrics to MLFlow
            tracker.log_metrics(final_metrics)

            results = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "models_trained": ml_settings.ENSEMBLE_MODELS,
                "version": version,
                "metrics": final_metrics
            }

            logger.info(f"Ensemble training completed: {trained_count} politicians trained")
            return results

    except Exception as e:
        logger.error(f"Ensemble training failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(
    base=MLTask,
    name='ml_tasks.train_cyclical_detector',
    bind=True
)
def train_cyclical_detector(
    self,
    politician_ids: Optional[list] = None
) -> Dict[str, Any]:
    """
    Train cyclical pattern detection model.

    Args:
        politician_ids: Optional list of politician IDs to train on

    Returns:
        Training results
    """
    logger.info("Training cyclical pattern detector")

    tracker = MLFlowTracker()

    try:
        with tracker.start_run("cyclical_detector_training"):
            # Load trade data
            trades_df = _load_trade_data(politician_ids=politician_ids)

            if trades_df.empty:
                return {
                    "status": "skipped",
                    "reason": "No trade data available",
                    "timestamp": datetime.now().isoformat()
                }

            # Initialize detector
            fourier_detector = FourierCyclicalDetector(
                min_strength=0.1,
                min_confidence=0.6
            )

            # Get politicians to process
            politicians = (
                politician_ids if politician_ids
                else trades_df['politician_id'].unique().tolist()
            )

            # Results storage
            all_cycles = {}
            cycle_summary = {
                "weekly": 0,
                "monthly": 0,
                "quarterly": 0,
                "annual": 0,
                "election_cycle": 0,
                "other": 0
            }

            for politician_id in politicians:
                try:
                    trade_series = _create_trade_frequency_series(
                        trades_df, str(politician_id)
                    )

                    if len(trade_series) < 30:
                        continue

                    result = fourier_detector.detect_cycles(
                        trade_series.values,
                        sampling_rate='daily',
                        return_details=True
                    )

                    if result.get('dominant_cycles'):
                        all_cycles[str(politician_id)] = result['dominant_cycles']

                        # Count by category
                        for cycle in result['dominant_cycles']:
                            category = cycle.get('category', 'other')
                            if category in cycle_summary:
                                cycle_summary[category] += 1

                except Exception as e:
                    logger.warning(f"Cyclical detection failed for {politician_id}: {e}")
                    continue

            # Save detector
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            _save_model(fourier_detector, "cyclical_detector", version)
            _save_model(all_cycles, "cyclical_patterns", version)

            # Log metrics
            tracker.log_params({"politicians_analyzed": len(politicians)})
            tracker.log_metrics(cycle_summary)

            results = {
                "status": "success",
                "model": "cyclical_detector",
                "version": version,
                "politicians_analyzed": len(politicians),
                "patterns_found": len(all_cycles),
                "cycle_summary": cycle_summary,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Cyclical detector trained: {len(all_cycles)} politicians with patterns")
            return results

    except Exception as e:
        logger.error(f"Cyclical detector training failed: {e}")
        return {"status": "failed", "error": str(e), "timestamp": datetime.now().isoformat()}


@celery_app.task(
    base=MLTask,
    name='ml_tasks.train_regime_detector',
    bind=True
)
def train_regime_detector(self) -> Dict[str, Any]:
    """
    Train HMM regime detection model.

    Returns:
        Training results
    """
    logger.info("Training regime detector")

    tracker = MLFlowTracker()

    try:
        with tracker.start_run("regime_detector_training"):
            # Load trade data
            trades_df = _load_trade_data()

            if trades_df.empty:
                return {
                    "status": "skipped",
                    "reason": "No trade data available",
                    "timestamp": datetime.now().isoformat()
                }

            # Initialize detector
            regime_detector = RegimeDetector(
                n_states=ml_settings.HMM_N_STATES,
                n_iter=ml_settings.HMM_N_ITERATIONS
            )

            politicians = trades_df['politician_id'].unique()

            # Store regime info for each politician
            all_regimes = {}
            regime_stats = {
                "bull_market": 0,
                "bear_market": 0,
                "high_volatility": 0,
                "low_volatility": 0
            }

            for politician_id in politicians:
                try:
                    trade_series = _create_trade_frequency_series(
                        trades_df, str(politician_id)
                    )

                    if len(trade_series) < 60:
                        continue

                    # Calculate returns from trade frequency
                    returns = trade_series.pct_change().fillna(0).values

                    # Fit HMM
                    result = regime_detector.fit_and_predict(returns)

                    if result.get('regime_characteristics'):
                        all_regimes[str(politician_id)] = {
                            "current_regime": result['current_regime'],
                            "current_regime_name": result['current_regime_name'],
                            "regime_probabilities": result['regime_probabilities'],
                            "expected_duration": result['expected_duration'],
                            "regime_characteristics": result['regime_characteristics']
                        }

                        # Count regime types
                        for regime_id, chars in result['regime_characteristics'].items():
                            regime_name = chars.get('name', '').lower().replace(' ', '_')
                            if regime_name in regime_stats:
                                regime_stats[regime_name] += 1

                except Exception as e:
                    logger.warning(f"Regime detection failed for {politician_id}: {e}")
                    continue

            # Save detector and regimes
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            _save_model(regime_detector, "regime_detector", version)
            _save_model(all_regimes, "politician_regimes", version)

            # Log metrics
            tracker.log_params({
                "n_states": ml_settings.HMM_N_STATES,
                "politicians_analyzed": len(politicians)
            })
            tracker.log_metrics({
                "politicians_with_regimes": len(all_regimes),
                **regime_stats
            })

            results = {
                "status": "success",
                "model": "regime_detector",
                "version": version,
                "politicians_analyzed": len(politicians),
                "politicians_with_regimes": len(all_regimes),
                "regime_stats": regime_stats,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Regime detector trained: {len(all_regimes)} politicians analyzed")
            return results

    except Exception as e:
        logger.error(f"Regime detector training failed: {e}")
        return {"status": "failed", "error": str(e), "timestamp": datetime.now().isoformat()}


@celery_app.task(
    base=MLTask,
    name='ml_tasks.update_features',
    bind=True
)
def update_features(
    self,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update feature engineering for all trades.

    Args:
        start_date: Start date for feature update
        end_date: End date for feature update

    Returns:
        Update results
    """
    logger.info("Updating features")

    try:
        # Load trade data
        trades_df = _load_trade_data(start_date, end_date)

        if trades_df.empty:
            return {
                "status": "skipped",
                "reason": "No trade data available",
                "timestamp": datetime.now().isoformat()
            }

        # Get unique tickers for market data
        tickers = trades_df['ticker'].unique().tolist()

        # Determine date range
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Load market data
        market_data = _load_market_data(tickers, start_date, end_date)

        # Initialize feature engineering
        feature_engineer = AdvancedFeatureEngineering()

        # Prepare trades DataFrame with proper index
        trades_df['transaction_date'] = pd.to_datetime(trades_df['transaction_date'])
        trades_indexed = trades_df.set_index('transaction_date').sort_index()

        # Combine market data into single DataFrame
        combined_market = pd.DataFrame()
        for ticker, data in market_data.items():
            if 'date' in data.columns:
                data = data.set_index('date')
            data['ticker'] = ticker
            combined_market = pd.concat([combined_market, data])

        if combined_market.empty:
            combined_market = pd.DataFrame(
                index=trades_indexed.index,
                columns=['close', 'volume', 'high', 'low']
            ).fillna(0)

        # Extract features
        features = feature_engineer.extract_all_features(
            trades_indexed,
            combined_market,
            politician_network=None,
            macro_data=None
        )

        # Handle NaN values
        features = features.fillna(0)

        # Save features
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        feature_path = os.path.join(ml_settings.MODEL_CACHE_DIR, f"features_{version}.parquet")
        os.makedirs(ml_settings.MODEL_CACHE_DIR, exist_ok=True)

        features.to_parquet(feature_path)

        # Feature statistics
        feature_stats = {
            "total_features": len(features.columns),
            "total_samples": len(features),
            "temporal_features": len([c for c in features.columns if 'day_' in c or 'month' in c or 'quarter' in c]),
            "return_features": len([c for c in features.columns if 'return' in c]),
            "volume_features": len([c for c in features.columns if 'volume' in c]),
            "technical_features": len([c for c in features.columns if any(x in c for x in ['sma', 'ema', 'rsi', 'macd', 'bb_'])]),
        }

        results = {
            "status": "success",
            "features_updated": len(features.columns),
            "samples_processed": len(features),
            "feature_path": feature_path,
            "version": version,
            "feature_stats": feature_stats,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Feature update completed: {len(features.columns)} features for {len(features)} samples")
        return results

    except Exception as e:
        logger.error(f"Feature update failed: {e}", exc_info=True)
        return {"status": "failed", "error": str(e), "timestamp": datetime.now().isoformat()}


@celery_app.task(
    base=MLTask,
    name='ml_tasks.generate_predictions',
    bind=True
)
def generate_predictions(
    self,
    tickers: Optional[list] = None
) -> Dict[str, Any]:
    """
    Generate predictions for tickers.

    Args:
        tickers: List of tickers to predict (None = all active)

    Returns:
        Prediction results
    """
    logger.info(f"Generating predictions for {len(tickers) if tickers else 'all'} tickers")

    try:
        # Load trained models
        fourier_detector = _load_model("fourier_detector") or FourierCyclicalDetector()
        regime_detector = _load_model("regime_detector") or RegimeDetector()
        dtw_matcher = _load_model("dtw_matcher") or DynamicTimeWarpingMatcher()
        ensemble_predictor = _load_model("ensemble_predictor") or EnsemblePredictor()

        # Load trade data
        trades_df = _load_trade_data()

        if trades_df.empty:
            return {
                "status": "skipped",
                "reason": "No trade data available",
                "timestamp": datetime.now().isoformat()
            }

        # Filter by tickers if specified
        if tickers:
            trades_df = trades_df[trades_df['ticker'].isin(tickers)]

        # Get unique politicians
        politicians = trades_df['politician_id'].unique()

        predictions = []
        insight_generator = InsightGenerator(confidence_threshold=0.6)

        for politician_id in politicians:
            try:
                trade_series = _create_trade_frequency_series(
                    trades_df, str(politician_id)
                )

                if len(trade_series) < 60:
                    continue

                # Run each model
                fourier_result = {}
                hmm_result = {}
                dtw_result = {}

                # Fourier analysis
                try:
                    fourier_result = fourier_detector.detect_cycles(
                        trade_series.values,
                        sampling_rate='daily'
                    )
                except Exception as e:
                    logger.warning(f"Fourier failed for {politician_id}: {e}")

                # HMM regime detection
                try:
                    returns = trade_series.pct_change().fillna(0).values
                    if len(returns) >= 30:
                        hmm_result = regime_detector.fit_and_predict(returns)
                except Exception as e:
                    logger.warning(f"HMM failed for {politician_id}: {e}")

                # DTW pattern matching
                try:
                    if len(trade_series) >= 120:
                        dtw_matches = dtw_matcher.find_similar_patterns(
                            trade_series.values,
                            trade_series.values,
                            window_size=30,
                            top_k=5
                        )
                        dtw_result = {
                            "matches_found": len(dtw_matches),
                            "top_matches": dtw_matches,
                            "prediction": dtw_matcher.predict_from_matches(dtw_matches)
                        }
                except Exception as e:
                    logger.warning(f"DTW failed for {politician_id}: {e}")

                # Generate ensemble prediction
                ensemble_pred = ensemble_predictor.predict(
                    fourier_result,
                    hmm_result,
                    dtw_result,
                    trade_series
                )

                # Generate insights
                insights = insight_generator.generate_comprehensive_insights(
                    fourier_result,
                    hmm_result,
                    dtw_result,
                    ensemble_pred
                )

                # Store prediction
                prediction_record = {
                    "politician_id": str(politician_id),
                    "prediction_type": ensemble_pred.prediction_type.value,
                    "predicted_value": ensemble_pred.value,
                    "confidence": ensemble_pred.confidence,
                    "model_agreement": ensemble_pred.model_agreement,
                    "anomaly_score": ensemble_pred.anomaly_score,
                    "insights": [
                        {"type": i.type.value, "severity": i.severity.value, "title": i.title}
                        for i in insights[:5]
                    ],
                    "generated_at": datetime.now().isoformat()
                }

                predictions.append(prediction_record)

            except Exception as e:
                logger.warning(f"Prediction failed for {politician_id}: {e}")
                continue

        # Save predictions
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        _save_model(predictions, "predictions", version)

        # Summary statistics
        high_confidence = len([p for p in predictions if p['confidence'] > 0.7])
        anomalies = len([p for p in predictions if p['anomaly_score'] > 0.7])

        results = {
            "status": "success",
            "predictions_generated": len(predictions),
            "high_confidence_predictions": high_confidence,
            "anomalies_detected": anomalies,
            "version": version,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Predictions generated: {len(predictions)} politicians")
        return results

    except Exception as e:
        logger.error(f"Prediction generation failed: {e}", exc_info=True)
        return {"status": "failed", "error": str(e), "timestamp": datetime.now().isoformat()}


@celery_app.task(
    base=MLTask,
    name='ml_tasks.detect_anomalies',
    bind=True
)
def detect_anomalies(
    self,
    lookback_days: int = 30
) -> Dict[str, Any]:
    """
    Detect anomalous trading activity.

    Args:
        lookback_days: Number of days to analyze

    Returns:
        Detected anomalies
    """
    logger.info(f"Detecting anomalies in last {lookback_days} days")

    try:
        # Load trade data for lookback period
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

        trades_df = _load_trade_data(start_date, end_date)

        if trades_df.empty:
            return {
                "status": "skipped",
                "reason": "No trade data available",
                "timestamp": datetime.now().isoformat()
            }

        # Load models
        dtw_matcher = _load_model("dtw_matcher") or DynamicTimeWarpingMatcher()
        regime_detector = _load_model("regime_detector") or RegimeDetector()

        # Historical data for comparison (need longer history)
        historical_start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        historical_df = _load_trade_data(historical_start, end_date)

        politicians = trades_df['politician_id'].unique()
        anomalies = []

        for politician_id in politicians:
            try:
                # Recent trade series
                recent_series = _create_trade_frequency_series(
                    trades_df, str(politician_id)
                )

                # Historical trade series
                historical_series = _create_trade_frequency_series(
                    historical_df, str(politician_id)
                )

                if len(recent_series) < 7 or len(historical_series) < 90:
                    continue

                anomaly_scores = []
                anomaly_reasons = []

                # Anomaly 1: Volume spike detection
                recent_avg = recent_series[-lookback_days:].mean()
                historical_avg = historical_series[:-lookback_days].mean()
                historical_std = historical_series[:-lookback_days].std()

                if historical_std > 0:
                    z_score = (recent_avg - historical_avg) / historical_std
                    if abs(z_score) > 2.5:
                        anomaly_scores.append(min(abs(z_score) / 5, 1.0))
                        direction = "increase" if z_score > 0 else "decrease"
                        anomaly_reasons.append(f"Unusual trading volume {direction} (z={z_score:.2f})")

                # Anomaly 2: Pattern novelty (DTW)
                if len(historical_series) >= 120:
                    try:
                        matches = dtw_matcher.find_similar_patterns(
                            recent_series.values,
                            historical_series.values,
                            window_size=min(30, len(recent_series)),
                            top_k=5
                        )

                        if not matches:
                            anomaly_scores.append(0.9)
                            anomaly_reasons.append("No similar historical patterns found")
                        elif matches[0]['similarity_score'] < 0.5:
                            anomaly_scores.append(1.0 - matches[0]['similarity_score'])
                            anomaly_reasons.append(f"Low pattern similarity ({matches[0]['similarity_score']:.1%})")
                    except Exception:
                        pass

                # Anomaly 3: Regime instability
                try:
                    returns = recent_series.pct_change().fillna(0).values
                    if len(returns) >= 14:
                        hmm_result = regime_detector.fit_and_predict(returns)

                        if hmm_result.get('expected_duration'):
                            current_regime = hmm_result.get('current_regime', 0)
                            expected_dur = hmm_result['expected_duration'][current_regime]

                            if expected_dur < 3:
                                anomaly_scores.append(0.7)
                                anomaly_reasons.append(f"Unstable regime (duration={expected_dur:.1f}d)")
                except Exception:
                    pass

                # Anomaly 4: Timing anomaly (trades around unusual times)
                politician_trades = trades_df[trades_df['politician_id'] == politician_id]
                if len(politician_trades) > 0:
                    # Check disclosure delay
                    politician_trades = politician_trades.copy()
                    politician_trades['disclosure_delay'] = (
                        pd.to_datetime(politician_trades['disclosure_date']) -
                        pd.to_datetime(politician_trades['transaction_date'])
                    ).dt.days

                    avg_delay = politician_trades['disclosure_delay'].mean()
                    if avg_delay > 30:  # More than 30 days delay
                        anomaly_scores.append(0.6)
                        anomaly_reasons.append(f"Late disclosure pattern (avg={avg_delay:.0f}d)")

                # Calculate overall anomaly score
                if anomaly_scores:
                    overall_score = np.mean(anomaly_scores)

                    if overall_score > 0.5:  # Threshold for reporting
                        politician_name = trades_df[
                            trades_df['politician_id'] == politician_id
                        ]['politician_name'].iloc[0] if 'politician_name' in trades_df.columns else str(politician_id)

                        anomaly_record = {
                            "politician_id": str(politician_id),
                            "politician_name": politician_name,
                            "anomaly_score": float(overall_score),
                            "severity": "critical" if overall_score > 0.8 else "high" if overall_score > 0.6 else "medium",
                            "reasons": anomaly_reasons,
                            "recent_trade_count": len(politician_trades),
                            "detected_at": datetime.now().isoformat()
                        }
                        anomalies.append(anomaly_record)

            except Exception as e:
                logger.warning(f"Anomaly detection failed for {politician_id}: {e}")
                continue

        # Sort by anomaly score
        anomalies.sort(key=lambda x: x['anomaly_score'], reverse=True)

        # Save anomalies
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        _save_model(anomalies, "anomalies", version)

        # Summary
        critical = len([a for a in anomalies if a['severity'] == 'critical'])
        high = len([a for a in anomalies if a['severity'] == 'high'])

        results = {
            "status": "success",
            "anomalies_detected": len(anomalies),
            "critical_anomalies": critical,
            "high_anomalies": high,
            "lookback_days": lookback_days,
            "politicians_analyzed": len(politicians),
            "top_anomalies": anomalies[:10],
            "version": version,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Anomaly detection completed: {len(anomalies)} anomalies found")
        return results

    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}", exc_info=True)
        return {"status": "failed", "error": str(e), "timestamp": datetime.now().isoformat()}


@celery_app.task(
    base=MLTask,
    name='ml_tasks.backtest_strategy',
    bind=True
)
def backtest_strategy(
    self,
    strategy_name: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Backtest a trading strategy.

    Args:
        strategy_name: Name of strategy to backtest
        start_date: Start date
        end_date: End date

    Returns:
        Backtest results
    """
    logger.info(f"Backtesting strategy: {strategy_name}")

    tracker = MLFlowTracker()

    try:
        with tracker.start_run(f"backtest_{strategy_name}"):
            # Log parameters
            tracker.log_params({
                "strategy": strategy_name,
                "start_date": start_date,
                "end_date": end_date
            })

            # Load trade data
            trades_df = _load_trade_data(start_date, end_date)

            if trades_df.empty:
                return {
                    "status": "skipped",
                    "reason": "No trade data available",
                    "timestamp": datetime.now().isoformat()
                }

            # Get unique tickers
            tickers = trades_df['ticker'].unique().tolist()[:20]  # Limit for performance

            # Load market data
            market_data = _load_market_data(tickers, start_date, end_date)

            if not market_data:
                return {
                    "status": "skipped",
                    "reason": "No market data available",
                    "timestamp": datetime.now().isoformat()
                }

            # Define strategy functions
            def copy_trade_strategy(trades_df: pd.DataFrame, market_df: pd.DataFrame, ticker: str) -> List[Dict]:
                """
                Copy politician trades strategy.
                Buy when politicians buy, sell when they sell.
                """
                signals = []
                ticker_trades = trades_df[trades_df['ticker'] == ticker].copy()

                for _, trade in ticker_trades.iterrows():
                    trade_date = pd.to_datetime(trade['transaction_date'])

                    # Find market price on trade date
                    if 'date' in market_df.columns:
                        market_df = market_df.set_index('date')

                    try:
                        price = market_df.loc[trade_date, 'close'] if trade_date in market_df.index else None
                    except:
                        price = None

                    if price:
                        signal = {
                            'date': trade_date,
                            'type': 'buy' if trade['transaction_type'] == 'buy' else 'sell',
                            'price': float(price),
                            'quantity': 100,  # Fixed position size
                            'politician': trade.get('politician_name', 'Unknown')
                        }
                        signals.append(signal)

                return signals

            def momentum_following_strategy(trades_df: pd.DataFrame, market_df: pd.DataFrame, ticker: str) -> List[Dict]:
                """
                Follow trades only when market momentum aligns.
                """
                signals = []
                ticker_trades = trades_df[trades_df['ticker'] == ticker].copy()

                if 'date' in market_df.columns:
                    market_df = market_df.set_index('date')

                # Calculate momentum (20-day SMA)
                if len(market_df) >= 20:
                    market_df['sma_20'] = market_df['close'].rolling(20).mean()

                    for _, trade in ticker_trades.iterrows():
                        trade_date = pd.to_datetime(trade['transaction_date'])

                        try:
                            if trade_date in market_df.index:
                                price = market_df.loc[trade_date, 'close']
                                sma = market_df.loc[trade_date, 'sma_20']

                                # Only follow buy if price > SMA (uptrend)
                                # Only follow sell if price < SMA (downtrend)
                                if trade['transaction_type'] == 'buy' and price > sma:
                                    signals.append({
                                        'date': trade_date,
                                        'type': 'buy',
                                        'price': float(price),
                                        'quantity': 100
                                    })
                                elif trade['transaction_type'] == 'sell' and price < sma:
                                    signals.append({
                                        'date': trade_date,
                                        'type': 'sell',
                                        'price': float(price),
                                        'quantity': 100
                                    })
                        except:
                            continue

                return signals

            def delayed_copy_strategy(trades_df: pd.DataFrame, market_df: pd.DataFrame, ticker: str, delay_days: int = 2) -> List[Dict]:
                """
                Copy trades with a delay (simulating disclosure delay).
                """
                signals = []
                ticker_trades = trades_df[trades_df['ticker'] == ticker].copy()

                if 'date' in market_df.columns:
                    market_df = market_df.set_index('date')

                for _, trade in ticker_trades.iterrows():
                    trade_date = pd.to_datetime(trade['transaction_date']) + timedelta(days=delay_days)

                    try:
                        # Find nearest valid trading day
                        for offset in range(5):
                            check_date = trade_date + timedelta(days=offset)
                            if check_date in market_df.index:
                                price = market_df.loc[check_date, 'close']
                                signals.append({
                                    'date': check_date,
                                    'type': 'buy' if trade['transaction_type'] == 'buy' else 'sell',
                                    'price': float(price),
                                    'quantity': 100
                                })
                                break
                    except:
                        continue

                return signals

            # Select strategy
            strategies = {
                'copy_trade': copy_trade_strategy,
                'momentum_following': momentum_following_strategy,
                'delayed_copy': delayed_copy_strategy
            }

            strategy_func = strategies.get(strategy_name, copy_trade_strategy)

            # Run backtest for each ticker
            all_results = []
            total_return = 0
            total_trades = 0

            for ticker in tickers:
                if ticker not in market_data:
                    continue

                market_df = market_data[ticker].copy()

                # Generate signals
                signals = strategy_func(trades_df, market_df, ticker)

                if not signals:
                    continue

                # Simple backtest calculation
                initial_capital = 10000
                capital = initial_capital
                position = 0
                entry_price = 0
                trades_executed = []

                for signal in sorted(signals, key=lambda x: x['date']):
                    if signal['type'] == 'buy' and position == 0:
                        # Buy
                        shares = int(capital * 0.95 / signal['price'])  # Use 95% of capital
                        if shares > 0:
                            cost = shares * signal['price']
                            capital -= cost
                            position = shares
                            entry_price = signal['price']
                            trades_executed.append({
                                'date': signal['date'],
                                'type': 'buy',
                                'price': signal['price'],
                                'shares': shares
                            })

                    elif signal['type'] == 'sell' and position > 0:
                        # Sell
                        proceeds = position * signal['price']
                        pnl = (signal['price'] - entry_price) * position
                        capital += proceeds
                        trades_executed.append({
                            'date': signal['date'],
                            'type': 'sell',
                            'price': signal['price'],
                            'shares': position,
                            'pnl': pnl
                        })
                        position = 0

                # Close any open position at last price
                if position > 0 and len(market_df) > 0:
                    last_price = market_df['close'].iloc[-1]
                    capital += position * last_price

                # Calculate return
                ticker_return = (capital - initial_capital) / initial_capital * 100

                ticker_result = {
                    'ticker': ticker,
                    'return_pct': ticker_return,
                    'trades': len(trades_executed),
                    'final_capital': capital
                }
                all_results.append(ticker_result)

                total_return += ticker_return
                total_trades += len(trades_executed)

            # Aggregate metrics
            avg_return = total_return / len(all_results) if all_results else 0
            winning_tickers = len([r for r in all_results if r['return_pct'] > 0])
            losing_tickers = len([r for r in all_results if r['return_pct'] < 0])

            # Calculate Sharpe-like ratio
            returns = [r['return_pct'] for r in all_results]
            sharpe = np.mean(returns) / np.std(returns) if returns and np.std(returns) > 0 else 0

            metrics = {
                "total_return_pct": round(total_return, 2),
                "average_return_pct": round(avg_return, 2),
                "total_trades": total_trades,
                "tickers_traded": len(all_results),
                "winning_tickers": winning_tickers,
                "losing_tickers": losing_tickers,
                "win_rate_pct": round(winning_tickers / len(all_results) * 100, 2) if all_results else 0,
                "sharpe_ratio": round(sharpe, 2),
                "best_ticker": max(all_results, key=lambda x: x['return_pct'])['ticker'] if all_results else None,
                "worst_ticker": min(all_results, key=lambda x: x['return_pct'])['ticker'] if all_results else None,
            }

            # Log metrics
            tracker.log_metrics(metrics)

            # Save results
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            backtest_results = {
                "strategy": strategy_name,
                "period": f"{start_date} to {end_date}",
                "metrics": metrics,
                "ticker_results": all_results
            }
            _save_model(backtest_results, f"backtest_{strategy_name}", version)

            results = {
                "status": "success",
                "strategy": strategy_name,
                "period": f"{start_date} to {end_date}",
                "metrics": metrics,
                "version": version,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Backtest completed: {strategy_name} returned {avg_return:.2f}% avg")
            return results

    except Exception as e:
        logger.error(f"Backtesting failed: {e}", exc_info=True)
        return {"status": "failed", "error": str(e), "timestamp": datetime.now().isoformat()}


# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Retrain models weekly
    'retrain-models-weekly': {
        'task': 'ml_tasks.train_ensemble_model',
        'schedule': 60 * 60 * 24 * 7,  # 7 days
        'options': {'queue': 'ml-training'}
    },

    # Update features daily
    'update-features-daily': {
        'task': 'ml_tasks.update_features',
        'schedule': 60 * 60 * 24,  # 1 day
        'options': {'queue': 'ml-training'}
    },

    # Generate predictions every 4 hours
    'generate-predictions-4h': {
        'task': 'ml_tasks.generate_predictions',
        'schedule': 60 * 60 * 4,  # 4 hours
        'options': {'queue': 'ml-training'}
    },

    # Detect anomalies daily
    'detect-anomalies-daily': {
        'task': 'ml_tasks.detect_anomalies',
        'schedule': 60 * 60 * 24,  # 1 day
        'options': {'queue': 'ml-training'}
    },
}

celery_app.conf.task_routes = {
    'ml_tasks.*': {'queue': 'ml-training'},
}


# ============================================================================
# Helper Functions
# ============================================================================

def _load_trade_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    politician_ids: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Load trade data from database for ML processing.

    Returns DataFrame with columns: politician_id, ticker, transaction_type,
    amount_min, amount_max, transaction_date, disclosure_date
    """
    from sqlalchemy import create_engine, text

    engine = create_engine(settings.DATABASE_URL)

    query = """
    SELECT
        t.politician_id,
        t.ticker,
        t.transaction_type,
        t.amount_min,
        t.amount_max,
        t.transaction_date,
        t.disclosure_date,
        p.name as politician_name,
        p.party,
        p.chamber
    FROM trades t
    JOIN politicians p ON t.politician_id = p.id
    WHERE 1=1
    """

    params = {}

    if start_date:
        query += " AND t.transaction_date >= :start_date"
        params['start_date'] = start_date

    if end_date:
        query += " AND t.transaction_date <= :end_date"
        params['end_date'] = end_date

    if politician_ids:
        query += " AND t.politician_id = ANY(:politician_ids)"
        params['politician_ids'] = politician_ids

    query += " ORDER BY t.transaction_date"

    try:
        df = pd.read_sql(text(query), engine, params=params)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        logger.info(f"Loaded {len(df)} trades from database")
        return df
    except Exception as e:
        logger.error(f"Failed to load trade data: {e}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            'politician_id', 'ticker', 'transaction_type',
            'amount_min', 'amount_max', 'transaction_date',
            'disclosure_date', 'politician_name', 'party', 'chamber'
        ])


def _create_trade_frequency_series(
    trades_df: pd.DataFrame,
    politician_id: Optional[str] = None,
    freq: str = 'D'
) -> pd.Series:
    """
    Create a time series of trade frequency.

    Args:
        trades_df: DataFrame of trades
        politician_id: Filter by politician (None = all)
        freq: Frequency ('D'=daily, 'W'=weekly, 'M'=monthly)

    Returns:
        pd.Series indexed by date with trade counts
    """
    df = trades_df.copy()

    if politician_id:
        df = df[df['politician_id'] == politician_id]

    if df.empty:
        return pd.Series(dtype=float)

    # Group by date and count trades
    df['date'] = pd.to_datetime(df['transaction_date']).dt.date
    trade_counts = df.groupby('date').size()

    # Create complete date range and fill missing with 0
    date_range = pd.date_range(
        start=trade_counts.index.min(),
        end=trade_counts.index.max(),
        freq=freq
    )

    trade_series = pd.Series(index=date_range, data=0.0)

    for date, count in trade_counts.items():
        if date in trade_series.index:
            trade_series[date] = count

    return trade_series


def _load_market_data(
    tickers: List[str],
    start_date: str,
    end_date: str
) -> Dict[str, pd.DataFrame]:
    """
    Load market data for given tickers.

    Returns dict mapping ticker -> DataFrame with OHLCV data.
    """
    import yfinance as yf

    market_data = {}

    for ticker in tickers[:50]:  # Limit to 50 tickers
        try:
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )

            if not data.empty:
                data = data.reset_index()
                data.columns = [c.lower() for c in data.columns]
                market_data[ticker] = data

        except Exception as e:
            logger.warning(f"Failed to load market data for {ticker}: {e}")

    logger.info(f"Loaded market data for {len(market_data)} tickers")
    return market_data


def _save_model(model: Any, model_name: str, version: str) -> str:
    """Save model to disk and return path."""
    model_dir = ml_settings.MODEL_CACHE_DIR
    os.makedirs(model_dir, exist_ok=True)

    path = os.path.join(model_dir, f"{model_name}_{version}.pkl")

    with open(path, 'wb') as f:
        pickle.dump(model, f)

    logger.info(f"Saved model to {path}")
    return path


def _load_model(model_name: str, version: str = "latest") -> Optional[Any]:
    """Load model from disk."""
    model_dir = ml_settings.MODEL_CACHE_DIR

    if version == "latest":
        # Find most recent model
        import glob
        pattern = os.path.join(model_dir, f"{model_name}_*.pkl")
        files = glob.glob(pattern)
        if not files:
            return None
        path = max(files, key=os.path.getctime)
    else:
        path = os.path.join(model_dir, f"{model_name}_{version}.pkl")

    if not os.path.exists(path):
        return None

    with open(path, 'rb') as f:
        model = pickle.load(f)

    logger.info(f"Loaded model from {path}")
    return model
