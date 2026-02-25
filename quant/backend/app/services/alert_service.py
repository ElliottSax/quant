"""
Alert Service for managing real-time trade alerts.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.alert import Alert, AlertType, AlertStatus, NotificationChannel
from app.models.trade import Trade
from app.core.logging import get_logger

logger = get_logger(__name__)


class AlertMatchingEngine:
    """Engine for matching trades against alert conditions."""

    @staticmethod
    async def check_trade_alerts(
        db: AsyncSession,
        trade: Trade
    ) -> List[Alert]:
        """
        Check if a new trade matches any active alerts.

        Args:
            db: Database session
            trade: New trade to check

        Returns:
            List of triggered alerts
        """
        # Get all active trade alerts
        query = select(Alert).where(
            and_(
                Alert.alert_type == AlertType.TRADE,
                Alert.status == AlertStatus.ACTIVE,
                Alert.is_active == True
            )
        )

        result = await db.execute(query)
        alerts = result.scalars().all()

        triggered_alerts = []

        for alert in alerts:
            conditions = alert.conditions

            # Check if trade matches conditions
            if await AlertMatchingEngine._match_trade_conditions(trade, conditions):
                triggered_alerts.append(alert)

                # Update alert statistics
                alert.last_triggered_at = datetime.utcnow()
                alert.trigger_count = int(alert.trigger_count) + 1

                logger.info(f"Alert {alert.id} triggered by trade {trade.id}")

        await db.commit()

        return triggered_alerts

    @staticmethod
    async def _match_trade_conditions(trade: Trade, conditions: dict) -> bool:
        """
        Check if a trade matches alert conditions.

        Conditions can include:
        - politician_id: Specific politician
        - ticker: Specific stock symbol
        - min_amount: Minimum trade amount
        - transaction_type: buy or sell
        """
        # Check politician_id
        if "politician_id" in conditions:
            if str(trade.politician_id) != str(conditions["politician_id"]):
                return False

        # Check ticker
        if "ticker" in conditions:
            if trade.ticker != conditions["ticker"]:
                return False

        # Check minimum amount
        if "min_amount" in conditions:
            trade_amount = (trade.amount_min or 0) + (trade.amount_max or 0)
            trade_amount = trade_amount / 2 if trade.amount_max else trade_amount

            if trade_amount < conditions["min_amount"]:
                return False

        # Check transaction type
        if "transaction_type" in conditions:
            if trade.transaction_type != conditions["transaction_type"]:
                return False

        return True

    @staticmethod
    async def check_price_alerts(
        db: AsyncSession,
        ticker: str,
        current_price: float
    ) -> List[Alert]:
        """
        Check if current price triggers any price alerts.

        Args:
            db: Database session
            ticker: Stock ticker
            current_price: Current stock price

        Returns:
            List of triggered alerts
        """
        # Get all active price alerts for this ticker
        query = select(Alert).where(
            and_(
                Alert.alert_type == AlertType.PRICE,
                Alert.status == AlertStatus.ACTIVE,
                Alert.is_active == True
            )
        )

        result = await db.execute(query)
        alerts = result.scalars().all()

        triggered_alerts = []

        for alert in alerts:
            conditions = alert.conditions

            # Check if this alert is for the ticker
            if conditions.get("ticker") != ticker:
                continue

            target_price = conditions.get("target_price")
            condition = conditions.get("condition", "above")

            triggered = False

            if condition == "above" and current_price >= target_price:
                triggered = True
            elif condition == "below" and current_price <= target_price:
                triggered = True

            if triggered:
                triggered_alerts.append(alert)

                # Update alert
                alert.last_triggered_at = datetime.utcnow()
                alert.trigger_count = int(alert.trigger_count) + 1
                alert.status = AlertStatus.TRIGGERED  # Mark as triggered

                logger.info(f"Price alert {alert.id} triggered for {ticker} at ${current_price}")

        await db.commit()

        return triggered_alerts


class NotificationService:
    """Service for delivering alert notifications."""

    @staticmethod
    async def send_notifications(
        alert: Alert,
        context: Dict[str, Any]
    ):
        """
        Send notifications through configured channels.

        Args:
            alert: Alert to send notification for
            context: Context data for notification (trade info, price info, etc.)
        """
        channels = alert.notification_channels

        if not isinstance(channels, list):
            channels = []

        for channel in channels:
            if channel == NotificationChannel.EMAIL.value:
                await NotificationService._send_email(alert, context)
            elif channel == NotificationChannel.WEBHOOK.value:
                await NotificationService._send_webhook(alert, context)
            elif channel == NotificationChannel.PUSH.value:
                await NotificationService._send_push(alert, context)

    @staticmethod
    def _format_alert_message(alert: Alert, context: Dict[str, Any]) -> str:
        """Format a human-readable alert message from context."""
        alert_type = alert.alert_type
        if alert_type == AlertType.TRADE:
            ticker = context.get("ticker", "unknown")
            tx_type = context.get("transaction_type", "trade")
            amount_min = context.get("amount_min")
            amount_max = context.get("amount_max")
            amount_str = ""
            if amount_min and amount_max:
                amount_str = f" (${amount_min:,.0f} - ${amount_max:,.0f})"
            elif amount_min:
                amount_str = f" (${amount_min:,.0f}+)"
            return f"A new {tx_type} trade for {ticker}{amount_str} matched your alert '{alert.name}'."
        elif alert_type == AlertType.PRICE:
            ticker = context.get("ticker", "unknown")
            price = context.get("current_price", context.get("price", "N/A"))
            return f"Price alert for {ticker} triggered at ${price}."
        else:
            return f"Alert '{alert.name}' has been triggered."

    @staticmethod
    async def _send_email(alert: Alert, context: Dict[str, Any]):
        """Send email notification via the email service."""
        email = alert.notification_email

        if not email:
            logger.warning(f"No email configured for alert {alert.id}")
            return

        try:
            from app.services.email_service import email_service

            title = f"Alert Triggered: {alert.name}"
            message = NotificationService._format_alert_message(alert, context)
            severity = "warning" if alert.alert_type == AlertType.PRICE else "info"

            await email_service.send_alert_email(
                to_email=email,
                title=title,
                message=message,
                severity=severity,
                metadata=context,
            )
            logger.info(f"Email notification sent to {email} for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send email for alert {alert.id}: {e}", exc_info=True)

    @staticmethod
    async def _send_webhook(alert: Alert, context: Dict[str, Any]):
        """Send webhook notification via HTTP POST."""
        webhook_url = alert.webhook_url

        if not webhook_url:
            logger.warning(f"No webhook URL configured for alert {alert.id}")
            return

        try:
            import httpx

            payload = {
                "alert_id": str(alert.id),
                "alert_name": alert.name,
                "alert_type": alert.alert_type.value if hasattr(alert.alert_type, "value") else str(alert.alert_type),
                "triggered_at": datetime.utcnow().isoformat(),
                **context,
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook_url, json=payload)
                if response.status_code < 300:
                    logger.info(f"Webhook sent to {webhook_url} for alert {alert.id}")
                else:
                    logger.warning(
                        f"Webhook to {webhook_url} returned status {response.status_code} for alert {alert.id}"
                    )
        except httpx.TimeoutException:
            logger.error(f"Webhook timed out for alert {alert.id}: {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to send webhook for alert {alert.id}: {e}", exc_info=True)

    @staticmethod
    async def _send_push(alert: Alert, context: Dict[str, Any]):
        """Send push notification to user's registered devices."""
        try:
            from app.services.push_notifications import push_notification_service
            from app.models.device import MobileDevice
            from app.core.database import AsyncSessionLocal
            from sqlalchemy import select as sa_select

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    sa_select(MobileDevice.device_token).where(
                        MobileDevice.user_id == alert.user_id
                    )
                )
                tokens = [row[0] for row in result.all()]

            if not tokens:
                logger.debug(f"No registered devices for user {alert.user_id}, skipping push")
                return

            title = f"Alert: {alert.name}"
            body = NotificationService._format_alert_message(alert, context)
            data = {k: str(v) for k, v in context.items() if v is not None}

            result = await push_notification_service.send_notification(
                device_tokens=tokens,
                title=title,
                body=body,
                data=data,
            )
            logger.info(f"Push notification sent to {len(tokens)} device(s) for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send push for alert {alert.id}: {e}", exc_info=True)


class AlertService:
    """Main service for alert management."""

    def __init__(self):
        self.matcher = AlertMatchingEngine()
        self.notifier = NotificationService()

    async def create_alert(
        self,
        db: AsyncSession,
        user_id: str,
        name: str,
        alert_type: AlertType,
        conditions: dict,
        notification_channels: List[str],
        webhook_url: Optional[str] = None,
        notification_email: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> Alert:
        """
        Create a new alert.

        Args:
            db: Database session
            user_id: User ID
            name: Alert name
            alert_type: Type of alert
            conditions: Alert conditions
            notification_channels: Notification channels to use
            webhook_url: Webhook URL (optional)
            notification_email: Email override (optional)
            expires_at: Expiration date (optional)

        Returns:
            Created alert
        """
        alert = Alert(
            user_id=user_id,
            name=name,
            alert_type=alert_type,
            conditions=conditions,
            notification_channels=notification_channels,
            webhook_url=webhook_url,
            notification_email=notification_email,
            expires_at=expires_at,
            status=AlertStatus.ACTIVE,
            is_active=True,
        )

        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        logger.info(f"Created alert {alert.id} for user {user_id}")

        return alert

    async def get_user_alerts(
        self,
        db: AsyncSession,
        user_id: str,
        alert_type: Optional[AlertType] = None,
        status: Optional[AlertStatus] = None
    ) -> List[Alert]:
        """
        Get all alerts for a user.

        Args:
            db: Database session
            user_id: User ID
            alert_type: Filter by alert type (optional)
            status: Filter by status (optional)

        Returns:
            List of alerts
        """
        query = select(Alert).where(Alert.user_id == user_id)

        if alert_type:
            query = query.where(Alert.alert_type == alert_type)

        if status:
            query = query.where(Alert.status == status)

        query = query.order_by(Alert.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()

    async def delete_alert(
        self,
        db: AsyncSession,
        alert_id: str,
        user_id: str
    ) -> bool:
        """
        Delete an alert.

        Args:
            db: Database session
            alert_id: Alert ID
            user_id: User ID (for authorization)

        Returns:
            True if deleted, False if not found
        """
        query = select(Alert).where(
            and_(
                Alert.id == alert_id,
                Alert.user_id == user_id
            )
        )

        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            return False

        await db.delete(alert)
        await db.commit()

        logger.info(f"Deleted alert {alert_id}")

        return True

    async def update_alert(
        self,
        db: AsyncSession,
        alert_id: str,
        user_id: str,
        **updates
    ) -> Optional[Alert]:
        """
        Update an alert.

        Args:
            db: Database session
            alert_id: Alert ID
            user_id: User ID (for authorization)
            **updates: Fields to update

        Returns:
            Updated alert or None if not found
        """
        query = select(Alert).where(
            and_(
                Alert.id == alert_id,
                Alert.user_id == user_id
            )
        )

        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(alert, key):
                setattr(alert, key, value)

        await db.commit()
        await db.refresh(alert)

        logger.info(f"Updated alert {alert_id}")

        return alert

    async def process_new_trade(
        self,
        db: AsyncSession,
        trade: Trade
    ):
        """
        Process a new trade and trigger any matching alerts.

        Args:
            db: Database session
            trade: New trade
        """
        # Check for matching alerts
        triggered_alerts = await self.matcher.check_trade_alerts(db, trade)

        # Send notifications
        for alert in triggered_alerts:
            context = {
                "trade_id": str(trade.id),
                "politician_id": str(trade.politician_id),
                "ticker": trade.ticker,
                "transaction_type": trade.transaction_type,
                "amount_min": float(trade.amount_min) if trade.amount_min else None,
                "amount_max": float(trade.amount_max) if trade.amount_max else None,
                "transaction_date": trade.transaction_date.isoformat(),
            }

            await self.notifier.send_notifications(alert, context)


# Global service instance
alert_service = AlertService()
