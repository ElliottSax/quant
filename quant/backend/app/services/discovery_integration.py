"""
Discovery Integration Service

Pulls data from the discovery project for use in quant analytics.
Reads predictions, analysis, and alerts from discovery's data files.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Path to discovery project (relative to quant)
DISCOVERY_BASE_PATH = Path("/mnt/e/projects/discovery")
DISCOVERY_DATA_PATH = DISCOVERY_BASE_PATH / "data"


class DiscoveryIntegration:
    """
    Integration layer for pulling data from the discovery project.

    Discovery project contains:
    - ML predictions for stocks based on politician trading
    - Cycle analysis with sentiment, volume, patterns
    - Real-time alerts for trading activity
    """

    def __init__(self, discovery_path: Optional[str] = None):
        self.base_path = Path(discovery_path) if discovery_path else DISCOVERY_DATA_PATH
        self.predictions_path = self.base_path / "predictions"
        self.analysis_path = self.base_path / "analysis"
        self.pipeline_path = self.base_path / "pipeline"
        self.alerts_path = self.base_path / "alerts"

    def is_available(self) -> bool:
        """Check if discovery data is available."""
        return self.base_path.exists()

    def get_latest_predictions(self) -> List[Dict[str, Any]]:
        """
        Get latest ML predictions from discovery.

        Returns predictions with:
        - ticker: Stock symbol
        - prediction: UP/DOWN
        - confidence: Confidence score
        - signals: Cyclical, regime, pattern, ML signals
        - regime: Current trading regime
        """
        try:
            latest_file = self.predictions_path / "predictions_latest.json"
            if not latest_file.exists():
                # Try to find most recent predictions file
                files = list(self.predictions_path.glob("predictions_*.json"))
                if not files:
                    logger.warning("No prediction files found")
                    return []
                latest_file = max(files, key=lambda p: p.stat().st_mtime)

            with open(latest_file) as f:
                predictions = json.load(f)

            # Enhance predictions with metadata
            for pred in predictions:
                pred['source'] = 'discovery'
                pred['data_timestamp'] = datetime.fromtimestamp(
                    latest_file.stat().st_mtime
                ).isoformat()

            logger.info(f"Loaded {len(predictions)} predictions from discovery")
            return predictions

        except Exception as e:
            logger.error(f"Error loading predictions: {e}")
            return []

    def get_stock_prediction(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get prediction for a specific stock."""
        predictions = self.get_latest_predictions()
        for pred in predictions:
            if pred.get('ticker', '').upper() == ticker.upper():
                return pred
        return None

    def get_multi_horizon_predictions(self) -> Dict[str, Any]:
        """Get multi-horizon predictions (7d, 14d, 30d)."""
        try:
            file_path = self.predictions_path / "multi_horizon_predictions.json"
            if not file_path.exists():
                return {}

            with open(file_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading multi-horizon predictions: {e}")
            return {}

    def get_cycle_analysis(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent 24x7 cycle analysis results.

        Returns analysis with:
        - sentiment: Positive/negative/neutral counts
        - volume: Volume statistics
        - patterns: Detected patterns
        """
        try:
            cycle_path = self.analysis_path / "24x7"
            if not cycle_path.exists():
                return []

            files = list(cycle_path.glob("cycle_*.json"))
            if not files:
                return []

            # Get most recent files
            files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            analyses = []
            for file_path in files[:limit]:
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        data['filename'] = file_path.name
                        data['timestamp'] = datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat()
                        analyses.append(data)
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")

            return analyses

        except Exception as e:
            logger.error(f"Error loading cycle analysis: {e}")
            return []

    def get_pipeline_analytics(self) -> List[Dict[str, Any]]:
        """Get pipeline analytics (top stocks, sector distribution, etc.)."""
        try:
            files = list(self.pipeline_path.glob("analytics_*.json"))
            if not files:
                return []

            latest_file = max(files, key=lambda p: p.stat().st_mtime)

            with open(latest_file) as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error loading pipeline analytics: {e}")
            return []

    def get_pipeline_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades from discovery pipeline."""
        try:
            files = list(self.pipeline_path.glob("trades_*.json"))
            if not files:
                return []

            latest_file = max(files, key=lambda p: p.stat().st_mtime)

            with open(latest_file) as f:
                trades = json.load(f)

            # Sort by transaction date and limit
            trades.sort(
                key=lambda t: t.get('transaction_date', ''),
                reverse=True
            )
            return trades[:limit]

        except Exception as e:
            logger.error(f"Error loading pipeline trades: {e}")
            return []

    def get_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts from discovery."""
        try:
            summary_file = self.alerts_path / "alert_summary.json"
            if not summary_file.exists():
                return []

            with open(summary_file) as f:
                data = json.load(f)

            alerts = data.get('alerts', []) if isinstance(data, dict) else data
            return alerts[:limit]

        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
            return []

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of available discovery data."""
        predictions = self.get_latest_predictions()
        analyses = self.get_cycle_analysis(limit=1)

        return {
            'available': self.is_available(),
            'predictions_count': len(predictions),
            'top_predictions': [
                {
                    'ticker': p.get('ticker'),
                    'prediction': p.get('prediction'),
                    'confidence': p.get('confidence')
                }
                for p in sorted(
                    predictions,
                    key=lambda x: x.get('confidence', 0),
                    reverse=True
                )[:5]
            ],
            'latest_analysis_timestamp': analyses[0].get('timestamp') if analyses else None,
            'data_path': str(self.base_path)
        }


# Singleton instance
discovery_service = DiscoveryIntegration()
