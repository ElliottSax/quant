"""
Email Service

Handles email sending via Resend API or SMTP.
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """
    Email service for sending transactional emails.

    Supports:
    - Resend API (recommended)
    - SMTP fallback
    """

    def __init__(self):
        self.resend_api_key = settings.RESEND_API_KEY
        self.smtp_configured = bool(settings.SMTP_HOST and settings.SMTP_USER)
        self.from_email = f"alerts@{settings.EMAIL_DOMAIN}"

    async def send_email(
        self,
        to_email: str | List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Send email via Resend or SMTP.

        Args:
            to_email: Recipient email(s)
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)
            from_email: Sender email (defaults to configured)
            reply_to: Reply-to email
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachments

        Returns:
            True if sent successfully, False otherwise
        """
        # Normalize to_email to list
        if isinstance(to_email, str):
            to_email = [to_email]

        from_email = from_email or self.from_email

        # Try Resend first if configured
        if self.resend_api_key:
            try:
                success = await self._send_via_resend(
                    to_email=to_email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                    from_email=from_email,
                    reply_to=reply_to,
                    cc=cc,
                    bcc=bcc,
                    attachments=attachments,
                )
                if success:
                    logger.info(
                        f"Email sent successfully via Resend to {to_email}",
                        extra={"subject": subject, "recipients": to_email}
                    )
                    return True
            except Exception as e:
                logger.error(f"Failed to send email via Resend: {e}", exc_info=True)

        # Fallback to SMTP if configured
        if self.smtp_configured:
            try:
                success = await self._send_via_smtp(
                    to_email=to_email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                    from_email=from_email,
                    reply_to=reply_to,
                    cc=cc,
                    bcc=bcc,
                )
                if success:
                    logger.info(
                        f"Email sent successfully via SMTP to {to_email}",
                        extra={"subject": subject, "recipients": to_email}
                    )
                    return True
            except Exception as e:
                logger.error(f"Failed to send email via SMTP: {e}", exc_info=True)

        logger.error(
            f"Failed to send email to {to_email} - no email service configured",
            extra={"subject": subject}
        )
        return False

    async def _send_via_resend(
        self,
        to_email: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send email via Resend API."""
        payload = {
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "html": html_body,
        }

        if text_body:
            payload["text"] = text_body
        if reply_to:
            payload["reply_to"] = reply_to
        if cc:
            payload["cc"] = cc
        if bcc:
            payload["bcc"] = bcc
        if attachments:
            payload["attachments"] = attachments

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.resend_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                return True
            else:
                logger.error(
                    f"Resend API error: {response.status_code} - {response.text}",
                    extra={"status_code": response.status_code, "response": response.text}
                )
                return False

    async def _send_via_smtp(
        self,
        to_email: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """Send email via SMTP."""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = ", ".join(to_email)

        if reply_to:
            msg["Reply-To"] = reply_to
        if cc:
            msg["Cc"] = ", ".join(cc)

        # Add plain text and HTML parts
        if text_body:
            part1 = MIMEText(text_body, "plain")
            msg.attach(part1)

        part2 = MIMEText(html_body, "html")
        msg.attach(part2)

        # Combine all recipients
        all_recipients = to_email.copy()
        if cc:
            all_recipients.extend(cc)
        if bcc:
            all_recipients.extend(bcc)

        # Send via SMTP
        try:
            if settings.SMTP_TLS:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(from_email, all_recipients, msg.as_string())
            else:
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(from_email, all_recipients, msg.as_string())

            return True
        except Exception as e:
            logger.error(f"SMTP send failed: {e}", exc_info=True)
            return False

    async def send_alert_email(
        self,
        to_email: str | List[str],
        title: str,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send alert email with formatted template.

        Args:
            to_email: Recipient email(s)
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, critical)
            metadata: Additional alert metadata

        Returns:
            True if sent successfully
        """
        # Color based on severity
        color_map = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "critical": "#ff0000",
            "error": "#ff0000",
        }
        color = color_map.get(severity.lower(), "#36a64f")

        # Build HTML email
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; }}
        .severity {{ display: inline-block; padding: 5px 10px; background-color: {color}; color: white; border-radius: 3px; font-weight: bold; text-transform: uppercase; }}
        .metadata {{ background-color: #fff; padding: 15px; margin-top: 15px; border-left: 3px solid {color}; }}
        .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">🚨 {title}</h1>
        </div>
        <div class="content">
            <p><span class="severity">{severity}</span></p>
            <p style="font-size: 16px; margin-top: 15px;">{message}</p>
"""

        # Add metadata if present
        if metadata:
            html_body += """
            <div class="metadata">
                <h3 style="margin-top: 0;">Additional Information:</h3>
                <ul>
"""
            for key, value in metadata.items():
                html_body += f"                    <li><strong>{key}:</strong> {value}</li>\n"

            html_body += """
                </ul>
            </div>
"""

        html_body += f"""
            <p style="margin-top: 20px; color: #666; font-size: 14px;">
                <em>Alert generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</em>
            </p>
        </div>
        <div class="footer">
            <p>Quant Trading Platform - Automated Alert System</p>
            <p>To manage your alert settings, visit your dashboard.</p>
        </div>
    </div>
</body>
</html>
"""

        # Plain text version
        text_body = f"""
{title}
{'=' * len(title)}

Severity: {severity.upper()}

{message}
"""

        if metadata:
            text_body += "\n\nAdditional Information:\n"
            for key, value in metadata.items():
                text_body += f"- {key}: {value}\n"

        text_body += f"\n\nAlert generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        text_body += "\n---\nQuant Trading Platform - Automated Alert System\n"

        return await self.send_email(
            to_email=to_email,
            subject=f"[{severity.upper()}] {title}",
            html_body=html_body,
            text_body=text_body,
        )


# Global email service instance
email_service = EmailService()
