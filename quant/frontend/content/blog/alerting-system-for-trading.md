---
title: 'Alerting System for Trading: Multi-Tier Notifications'
slug: alerting-system-for-trading
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
quality_score: 90
seo_optimized: true
published_date: '2026-03-16'
last_updated: '2026-03-16'
---

# Alerting System for Trading: Multi-Tier Notifications

**Author:** Dr. James Chen
**Category:** Algo Trading
**Date:** 2026-03-16

## Introduction

Robust alerting systems are critical for trading operations, providing immediate notification of critical events, risk threshold breaches, and system failures. This guide covers building multi-tier alerting systems with smart aggregation to avoid alert fatigue while ensuring critical issues are not missed.

## Alerting Framework

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import smtplib
from email.mime.text import MIMEText
import json
import asyncio

class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = 1  # Immediate action required
    HIGH = 2      # Urgent, investigate soon
    MEDIUM = 3    # Monitor, not immediately urgent
    LOW = 4       # Informational
    INFO = 5      # Regular updates

class AlertChannel(Enum):
    """Alert delivery channels."""
    EMAIL = 'email'
    SMS = 'sms'
    SLACK = 'slack'
    PAGERDUTY = 'pagerduty'
    WEBHOOK = 'webhook'
    LOG = 'log'

@dataclass
class Alert:
    """Represents an alert."""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    source: str
    metadata: Dict = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class AlertRule:
    """Defines alert trigger conditions."""

    def __init__(self, name: str, condition: Callable, severity: AlertSeverity,
                 cooldown_minutes: int = 5):
        self.name = name
        self.condition = condition
        self.severity = severity
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None

    def should_trigger(self, metrics: Dict) -> bool:
        """Check if alert should trigger."""
        # Check cooldown
        if self.last_triggered:
            elapsed = datetime.utcnow() - self.last_triggered
            if elapsed < timedelta(minutes=self.cooldown_minutes):
                return False

        # Check condition
        return self.condition(metrics)

    def trigger(self):
        """Record trigger time."""
        self.last_triggered = datetime.utcnow()

class AlertingEngine:
    """Manages alert rules and delivery."""

    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alerts: List[Alert] = []
        self.channels: Dict[AlertChannel, Callable] = {}
        self.route_config: Dict[AlertSeverity, List[AlertChannel]] = {
            AlertSeverity.CRITICAL: [AlertChannel.PAGERDUTY, AlertChannel.SMS, AlertChannel.SLACK],
            AlertSeverity.HIGH: [AlertChannel.SLACK, AlertChannel.EMAIL],
            AlertSeverity.MEDIUM: [AlertChannel.SLACK, AlertChannel.EMAIL],
            AlertSeverity.LOW: [AlertChannel.EMAIL, AlertChannel.LOG],
            AlertSeverity.INFO: [AlertChannel.LOG]
        }

    def register_rule(self, rule: AlertRule):
        """Register alert rule."""
        self.rules.append(rule)

    def register_channel(self, channel: AlertChannel, handler: Callable):
        """Register alert channel handler."""
        self.channels[channel] = handler

    def check_rules(self, metrics: Dict):
        """Check all alert rules against metrics."""
        for rule in self.rules:
            if rule.should_trigger(metrics):
                alert = Alert(
                    id=f"ALERT_{len(self.alerts)}",
                    title=rule.name,
                    message=f"{rule.name} triggered",
                    severity=rule.severity,
                    timestamp=datetime.utcnow(),
                    source='rule_engine',
                    metadata=metrics
                )

                self.raise_alert(alert)
                rule.trigger()

    def raise_alert(self, alert: Alert):
        """Raise alert and deliver via configured channels."""
        self.alerts.append(alert)

        # Get channels for severity
        channels = self.route_config.get(alert.severity, [])

        # Deliver to each channel
        for channel in channels:
            if channel in self.channels:
                handler = self.channels[channel]
                asyncio.create_task(handler(alert))

    def resolve_alert(self, alert_id: str):
        """Resolve alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                break

    def get_active_alerts(self) -> List[Alert]:
        """Get unresolved alerts."""
        return [a for a in self.alerts if not a.resolved]

# Alert channel implementations

class EmailAlertHandler:
    """Send alerts via email."""

    def __init__(self, smtp_host: str, smtp_port: int,
                 from_address: str, to_addresses: List[str]):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_address = from_address
        self.to_addresses = to_addresses

    async def send(self, alert: Alert):
        """Send email alert."""
        subject = f"[{alert.severity.name}] {alert.title}"

        body = f"""
Alert: {alert.title}
Severity: {alert.severity.name}
Time: {alert.timestamp}
Source: {alert.source}

Message: {alert.message}

Metadata: {json.dumps(alert.metadata, indent=2)}
"""

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.from_address
        msg['To'] = ', '.join(self.to_addresses)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg)

        except Exception as e:
            print(f"Email send failed: {e}")

class SlackAlertHandler:
    """Send alerts via Slack."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, alert: Alert):
        """Send Slack alert."""
        import aiohttp

        color = {
            AlertSeverity.CRITICAL: '#FF0000',
            AlertSeverity.HIGH: '#FF6600',
            AlertSeverity.MEDIUM: '#FFAA00',
            AlertSeverity.LOW: '#00AA00',
            AlertSeverity.INFO: '#0000FF'
        }.get(alert.severity, '#808080')

        payload = {
            'attachments': [{
                'color': color,
                'title': alert.title,
                'text': alert.message,
                'fields': [
                    {'title': 'Severity', 'value': alert.severity.name, 'short': True},
                    {'title': 'Source', 'value': alert.source, 'short': True},
                    {'title': 'Time', 'value': str(alert.timestamp), 'short': False}
                ]
            }]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as resp:
                return await resp.text()

class PagerDutyAlertHandler:
    """Send alerts via PagerDuty."""

    def __init__(self, api_key: str, service_id: str):
        self.api_key = api_key
        self.service_id = service_id

    async def send(self, alert: Alert):
        """Send PagerDuty alert."""
        import aiohttp

        url = 'https://events.pagerduty.com/v2/enqueue'

        payload = {
            'routing_key': self.api_key,
            'event_action': 'trigger',
            'payload': {
                'summary': alert.title,
                'severity': alert.severity.name.lower(),
                'source': alert.source,
                'custom_details': {
                    'message': alert.message,
                    'metadata': alert.metadata
                }
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.text()

class LogAlertHandler:
    """Log alerts."""

    def __init__(self, logger):
        self.logger = logger

    async def send(self, alert: Alert):
        """Log alert."""
        level_map = {
            AlertSeverity.CRITICAL: 'CRITICAL',
            AlertSeverity.HIGH: 'ERROR',
            AlertSeverity.MEDIUM: 'WARNING',
            AlertSeverity.LOW: 'INFO',
            AlertSeverity.INFO: 'DEBUG'
        }

        level = level_map.get(alert.severity, 'INFO')

        self.logger.log(
            getattr(logging, level),
            f"[{alert.id}] {alert.title}: {alert.message}"
        )

# Alert aggregation for reducing noise

class AlertAggregator:
    """Aggregates similar alerts to reduce noise."""

    def __init__(self, window_minutes: int = 5):
        self.window_minutes = window_minutes
        self.alert_groups: Dict[str, List[Alert]] = {}

    def should_send(self, alert: Alert) -> bool:
        """Determine if alert should be sent or suppressed."""
        key = f"{alert.source}:{alert.title}"

        if key not in self.alert_groups:
            self.alert_groups[key] = []

        # Get recent alerts in same group
        recent = [a for a in self.alert_groups[key]
                 if (datetime.utcnow() - a.timestamp).seconds < self.window_minutes * 60]

        # Suppress if multiple identical alerts in window
        if len(recent) > 3:
            return False

        self.alert_groups[key].append(alert)

        return True

# Example usage
if __name__ == "__main__":
    import logging

    # Setup alerting
    engine = AlertingEngine()

    # Register handlers
    email_handler = EmailAlertHandler(
        smtp_host='smtp.gmail.com',
        smtp_port=587,
        from_address='trading-alerts@example.com',
        to_addresses=['trader@example.com']
    )

    slack_handler = SlackAlertHandler(
        webhook_url='https://hooks.slack.com/services/...'
    )

    logger = logging.getLogger('trading')
    log_handler = LogAlertHandler(logger)

    engine.register_channel(AlertChannel.EMAIL, email_handler.send)
    engine.register_channel(AlertChannel.SLACK, slack_handler.send)
    engine.register_channel(AlertChannel.LOG, log_handler.send)

    # Register alert rules
    def high_margin_rule(metrics):
        return metrics.get('margin_used', 0) > 0.8

    def large_drawdown_rule(metrics):
        return metrics.get('max_drawdown', 0) < -0.10

    engine.register_rule(AlertRule(
        'High Margin Usage',
        high_margin_rule,
        AlertSeverity.HIGH,
        cooldown_minutes=30
    ))

    engine.register_rule(AlertRule(
        'Large Drawdown',
        large_drawdown_rule,
        AlertSeverity.CRITICAL,
        cooldown_minutes=60
    ))

    # Check rules
    metrics = {
        'margin_used': 0.85,
        'max_drawdown': -0.15
    }

    engine.check_rules(metrics)

    # Get active alerts
    active = engine.get_active_alerts()
    print(f"Active alerts: {len(active)}")
```

## Best Practices

1. **Severity Levels**: Map thresholds to appropriate severities
2. **Smart Routing**: Send only relevant alerts to each channel
3. **Alert Aggregation**: Group similar alerts to reduce noise
4. **Acknowledgment**: Track alert acknowledgment and resolution
5. **Escalation**: Escalate unacknowledged critical alerts

## Conclusion

A well-designed alerting system ensures critical trading issues are communicated effectively while avoiding alert fatigue from non-critical notifications.
