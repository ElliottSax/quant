"""
Alerting Service

Sends alerts via multiple channels (Email, Slack, Webhook).
"""

import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"


class AlertManager:
    """
    Manages alert delivery across multiple channels.
    """

    def __init__(self):
        self.alert_history: List[Dict] = []
        self.max_history = 100

    async def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        channels: Optional[List[AlertChannel]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send alert to specified channels.

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity level
            channels: List of channels to send to (default: all configured)
            metadata: Additional alert metadata
        """

        if channels is None:
            channels = self._get_default_channels()

        alert_data = {
            "title": title,
            "message": message,
            "severity": severity.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }

        # Record in history
        self.alert_history.append(alert_data)
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]

        # Send to each channel
        tasks = []
        for channel in channels:
            if channel == AlertChannel.EMAIL:
                tasks.append(self._send_email(alert_data))
            elif channel == AlertChannel.SLACK:
                tasks.append(self._send_slack(alert_data))
            elif channel == AlertChannel.WEBHOOK:
                tasks.append(self._send_webhook(alert_data))
            elif channel == AlertChannel.LOG:
                self._log_alert(alert_data)

        # Send alerts concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Log any failures
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Failed to send alert: {result}")

    def _get_default_channels(self) -> List[AlertChannel]:
        """Get default channels based on configuration"""
        channels = [AlertChannel.LOG]  # Always log

        if settings.SLACK_WEBHOOK_URL:
            channels.append(AlertChannel.SLACK)

        if settings.ALERT_WEBHOOK_URL:
            channels.append(AlertChannel.WEBHOOK)

        if settings.ALERT_EMAIL:
            channels.append(AlertChannel.EMAIL)

        return channels

    async def _send_email(self, alert_data: Dict):
        """Send alert via email"""
        from app.services.email_service import email_service

        if not settings.ALERT_EMAIL:
            logger.debug("No alert email configured, skipping email alert")
            return

        try:
            # Get email recipients (can be comma-separated list)
            recipients = [email.strip() for email in settings.ALERT_EMAIL.split(",")]

            # Send alert email
            success = await email_service.send_alert_email(
                to_email=recipients,
                title=alert_data["title"],
                message=alert_data["message"],
                severity=alert_data["severity"],
                metadata=alert_data.get("metadata"),
            )

            if success:
                logger.info(f"Alert email sent to {recipients}")
            else:
                logger.error(f"Failed to send alert email to {recipients}")

        except Exception as e:
            logger.error(f"Error sending alert email: {e}", exc_info=True)

    async def _send_slack(self, alert_data: Dict):
        """Send alert to Slack"""
        if not settings.SLACK_WEBHOOK_URL:
            return

        # Format Slack message
        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨"
        }

        severity_color = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "critical": "#ff0000"
        }

        severity = alert_data["severity"]

        payload = {
            "text": f"{severity_emoji.get(severity, '📢')} *{alert_data['title']}*",
            "attachments": [
                {
                    "color": severity_color.get(severity, "#cccccc"),
                    "fields": [
                        {
                            "title": "Severity",
                            "value": severity.upper(),
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert_data["timestamp"],
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": alert_data["message"],
                            "short": False
                        }
                    ]
                }
            ]
        }

        # Add metadata if present
        if alert_data.get("metadata"):
            for key, value in alert_data["metadata"].items():
                payload["attachments"][0]["fields"].append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.SLACK_WEBHOOK_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Slack alert failed: {response.status}")
                    else:
                        logger.info("Slack alert sent successfully")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    async def _send_webhook(self, alert_data: Dict):
        """Send alert to webhook"""
        if not settings.ALERT_WEBHOOK_URL:
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.ALERT_WEBHOOK_URL,
                    json=alert_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Webhook alert failed: {response.status}")
                    else:
                        logger.info("Webhook alert sent successfully")

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

    def _log_alert(self, alert_data: Dict):
        """Log alert"""
        severity = alert_data["severity"]

        log_message = f"ALERT [{severity.upper()}] {alert_data['title']}: {alert_data['message']}"

        if severity == "critical":
            logger.critical(log_message, extra=alert_data)
        elif severity == "warning":
            logger.warning(log_message, extra=alert_data)
        else:
            logger.info(log_message, extra=alert_data)

    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]


# Global alert manager
alert_manager = AlertManager()


# Convenience functions
async def send_critical_alert(title: str, message: str, **metadata):
    """Send critical alert"""
    await alert_manager.send_alert(
        title=title,
        message=message,
        severity=AlertSeverity.CRITICAL,
        metadata=metadata
    )


async def send_warning_alert(title: str, message: str, **metadata):
    """Send warning alert"""
    await alert_manager.send_alert(
        title=title,
        message=message,
        severity=AlertSeverity.WARNING,
        metadata=metadata
    )


async def send_info_alert(title: str, message: str, **metadata):
    """Send info alert"""
    await alert_manager.send_alert(
        title=title,
        message=message,
        severity=AlertSeverity.INFO,
        metadata=metadata
    )
