"""
Push Notification Service

Sends push notifications to mobile devices via FCM (Android) and APNS (iOS).
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional, Any
from enum import Enum

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class NotificationPriority(str, Enum):
    """Push notification priority"""
    HIGH = "high"
    NORMAL = "normal"


class PushNotificationService:
    """
    Service for sending push notifications to mobile devices.

    Supports:
    - Firebase Cloud Messaging (FCM) for Android
    - Apple Push Notification Service (APNS) for iOS
    """

    def __init__(self):
        self.fcm_server_key = settings.FCM_SERVER_KEY if hasattr(settings, 'FCM_SERVER_KEY') else None
        self.apns_cert_path = settings.APNS_CERT_PATH if hasattr(settings, 'APNS_CERT_PATH') else None
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"

    async def send_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        badge: Optional[int] = None,
        sound: str = "default"
    ) -> Dict[str, Any]:
        """
        Send push notification to device(s).

        Args:
            device_tokens: List of device tokens
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            priority: Notification priority
            badge: Badge count (iOS)
            sound: Sound to play

        Returns:
            Result dictionary with success/failure counts
        """
        if not device_tokens:
            return {"success": 0, "failure": 0, "message": "No device tokens"}

        # Send to FCM (handles both Android and iOS via FCM)
        return await self._send_fcm(
            device_tokens,
            title,
            body,
            data,
            priority,
            badge,
            sound
        )

    async def _send_fcm(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]],
        priority: NotificationPriority,
        badge: Optional[int],
        sound: str
    ) -> Dict[str, Any]:
        """Send notification via Firebase Cloud Messaging"""

        if not self.fcm_server_key:
            logger.warning("FCM server key not configured")
            return {
                "success": 0,
                "failure": len(device_tokens),
                "message": "FCM not configured"
            }

        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json"
        }

        # Build notification payload
        notification_payload = {
            "title": title,
            "body": body,
            "sound": sound
        }

        if badge is not None:
            notification_payload["badge"] = badge

        # Build complete payload
        payload = {
            "registration_ids": device_tokens,
            "notification": notification_payload,
            "priority": priority.value,
            "data": data or {}
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.fcm_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        success_count = result.get("success", 0)
                        failure_count = result.get("failure", 0)

                        logger.info(
                            f"Push notification sent: {success_count} success, {failure_count} failure",
                            extra={
                                "success": success_count,
                                "failure": failure_count,
                                "total": len(device_tokens)
                            }
                        )

                        return {
                            "success": success_count,
                            "failure": failure_count,
                            "results": result.get("results", [])
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"FCM push failed: {response.status} - {error_text}")
                        return {
                            "success": 0,
                            "failure": len(device_tokens),
                            "error": error_text
                        }

        except Exception as e:
            logger.error(f"Failed to send push notification: {e}", exc_info=True)
            return {
                "success": 0,
                "failure": len(device_tokens),
                "error": str(e)
            }

    async def send_trade_alert(
        self,
        device_tokens: List[str],
        politician_name: str,
        ticker: str,
        transaction_type: str,
        amount: str
    ) -> Dict[str, Any]:
        """
        Send trade alert notification.

        Args:
            device_tokens: Device tokens to notify
            politician_name: Politician name
            ticker: Stock ticker
            transaction_type: "buy" or "sell"
            amount: Transaction amount range

        Returns:
            Send result
        """
        title = f"New Trade: {politician_name}"
        body = f"{transaction_type.upper()} {ticker} - {amount}"

        data = {
            "type": "trade_alert",
            "politician": politician_name,
            "ticker": ticker,
            "transaction_type": transaction_type,
            "amount": amount
        }

        return await self.send_notification(
            device_tokens,
            title,
            body,
            data,
            priority=NotificationPriority.HIGH
        )

    async def send_price_alert(
        self,
        device_tokens: List[str],
        ticker: str,
        current_price: float,
        target_price: float,
        condition: str
    ) -> Dict[str, Any]:
        """
        Send price alert notification.

        Args:
            device_tokens: Device tokens to notify
            ticker: Stock ticker
            current_price: Current price
            target_price: Target price that was hit
            condition: Alert condition (above/below)

        Returns:
            Send result
        """
        title = f"Price Alert: {ticker}"
        body = f"{ticker} is now {condition} ${target_price:.2f} (${current_price:.2f})"

        data = {
            "type": "price_alert",
            "ticker": ticker,
            "current_price": current_price,
            "target_price": target_price,
            "condition": condition
        }

        return await self.send_notification(
            device_tokens,
            title,
            body,
            data,
            priority=NotificationPriority.HIGH
        )

    async def send_bulk_notifications(
        self,
        notifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Send multiple notifications in parallel.

        Args:
            notifications: List of notification dicts with keys:
                - device_tokens: List[str]
                - title: str
                - body: str
                - data: Optional[Dict]

        Returns:
            List of results for each notification
        """
        tasks = []
        for notif in notifications:
            tasks.append(
                self.send_notification(
                    device_tokens=notif["device_tokens"],
                    title=notif["title"],
                    body=notif["body"],
                    data=notif.get("data")
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            result if not isinstance(result, Exception) else {"error": str(result)}
            for result in results
        ]


# Global instance
push_notification_service = PushNotificationService()
