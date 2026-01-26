"""
Alerting System
Sends alerts for critical events via multiple channels
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"


class Alert:
    """Alert data model"""

    def __init__(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.message = message
        self.severity = severity
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class AlertingService:
    """Centralized alerting service"""

    def __init__(self):
        self.enabled = getattr(settings, 'ALERTS_ENABLED', False)
        self.channels: Dict[AlertChannel, bool] = {
            AlertChannel.EMAIL: getattr(settings, 'ALERT_EMAIL_ENABLED', False),
            AlertChannel.SLACK: getattr(settings, 'ALERT_SLACK_ENABLED', False),
            AlertChannel.WEBHOOK: getattr(settings, 'ALERT_WEBHOOK_ENABLED', False),
        }

    async def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        channels: Optional[List[AlertChannel]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send alert through specified channels
        """
        if not self.enabled:
            logger.debug(f"Alerts disabled, skipping: {title}")
            return

        alert = Alert(title, message, severity, metadata)

        # Use all enabled channels if none specified
        if channels is None:
            channels = [ch for ch, enabled in self.channels.items() if enabled]

        # Send to each channel
        tasks = []
        for channel in channels:
            if channel == AlertChannel.EMAIL:
                tasks.append(self._send_email(alert))
            elif channel == AlertChannel.SLACK:
                tasks.append(self._send_slack(alert))
            elif channel == AlertChannel.WEBHOOK:
                tasks.append(self._send_webhook(alert))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_email(self, alert: Alert):
        """Send alert via email"""
        try:
            # TODO: Implement email sending
            # This would use the email service to send alerts
            logger.info(f"Email alert: {alert.title}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    async def _send_slack(self, alert: Alert):
        """Send alert via Slack"""
        slack_webhook = getattr(settings, 'SLACK_WEBHOOK_URL', None)
        if not slack_webhook:
            logger.warning("Slack webhook URL not configured")
            return

        try:
            # Color based on severity
            color_map = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff9900",
                AlertSeverity.ERROR: "#ff0000",
                AlertSeverity.CRITICAL: "#880000"
            }

            payload = {
                "attachments": [{
                    "color": color_map.get(alert.severity, "#36a64f"),
                    "title": alert.title,
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.severity.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "short": True
                        }
                    ],
                    "footer": "Quant Trading Platform",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }

            # Add metadata fields
            if alert.metadata:
                for key, value in alert.metadata.items():
                    payload["attachments"][0]["fields"].append({
                        "title": key,
                        "value": str(value),
                        "short": True
                    })

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    slack_webhook,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()

            logger.info(f"Slack alert sent: {alert.title}")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    async def _send_webhook(self, alert: Alert):
        """Send alert via webhook"""
        webhook_url = getattr(settings, 'ALERT_WEBHOOK_URL', None)
        if not webhook_url:
            logger.warning("Alert webhook URL not configured")
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=alert.to_dict(),
                    timeout=10.0
                )
                response.raise_for_status()

            logger.info(f"Webhook alert sent: {alert.title}")

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

    # Convenience methods for common alerts
    async def alert_high_error_rate(self, error_rate: float, endpoint: str):
        """Alert for high error rate"""
        await self.send_alert(
            title="High Error Rate Detected",
            message=f"Error rate of {error_rate:.1%} detected on {endpoint}",
            severity=AlertSeverity.ERROR,
            metadata={
                'error_rate': error_rate,
                'endpoint': endpoint
            }
        )

    async def alert_slow_response(self, endpoint: str, duration: float):
        """Alert for slow response time"""
        await self.send_alert(
            title="Slow Response Time",
            message=f"{endpoint} took {duration:.2f}s to respond",
            severity=AlertSeverity.WARNING,
            metadata={
                'endpoint': endpoint,
                'duration_seconds': duration
            }
        )

    async def alert_high_memory(self, memory_percent: float):
        """Alert for high memory usage"""
        await self.send_alert(
            title="High Memory Usage",
            message=f"Memory usage at {memory_percent:.1f}%",
            severity=AlertSeverity.WARNING,
            metadata={
                'memory_percent': memory_percent
            }
        )

    async def alert_database_error(self, error: str):
        """Alert for database errors"""
        await self.send_alert(
            title="Database Error",
            message=f"Database operation failed: {error}",
            severity=AlertSeverity.CRITICAL,
            metadata={
                'error': error
            }
        )

    async def alert_deployment(self, version: str, status: str):
        """Alert for deployment events"""
        severity = AlertSeverity.INFO if status == "success" else AlertSeverity.ERROR
        await self.send_alert(
            title=f"Deployment {status.title()}",
            message=f"Version {version} deployment {status}",
            severity=severity,
            metadata={
                'version': version,
                'status': status
            }
        )


# Global alerting service
alerting = AlertingService()
