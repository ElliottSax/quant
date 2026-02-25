"""Email verification utilities."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.user import User

logger = get_logger(__name__)

# Token expiration time in hours
VERIFICATION_TOKEN_EXPIRE_HOURS = 24


def generate_verification_token() -> str:
    """Generate a secure verification token."""
    return secrets.token_urlsafe(32)


def is_token_expired(sent_at: datetime | None) -> bool:
    """
    Check if verification token has expired.

    Args:
        sent_at: When the token was sent

    Returns:
        True if expired, False otherwise
    """
    if sent_at is None:
        return True

    # Ensure timezone awareness
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)

    expiry = sent_at + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    return datetime.now(timezone.utc) > expiry


async def create_verification_token(user: "User", db: "AsyncSession") -> str:
    """
    Create and store a verification token for a user.

    Args:
        user: User to create token for
        db: Database session

    Returns:
        The verification token
    """
    token = generate_verification_token()
    user.email_verification_token = token
    user.email_verification_sent_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info(f"Verification token created for user: {user.username}")
    return token


def get_verification_url(token: str) -> str:
    """
    Get the full verification URL.

    Args:
        token: Verification token

    Returns:
        Full verification URL
    """
    # Use frontend URL from settings or default
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
    return f"{frontend_url}/verify-email?token={token}"


async def send_verification_email(
    email: str,
    username: str,
    token: str,
) -> bool:
    """
    Send verification email to user.

    Args:
        email: User's email address
        username: User's username
        token: Verification token

    Returns:
        True if email was sent successfully
    """
    verification_url = get_verification_url(token)

    # Try to use configured email service
    try:
        # Check for Resend (preferred for free tier)
        if hasattr(settings, "RESEND_API_KEY") and settings.RESEND_API_KEY:
            return await _send_with_resend(email, username, verification_url)

        # Check for SMTP
        if hasattr(settings, "SMTP_HOST") and settings.SMTP_HOST:
            return await _send_with_smtp(email, username, verification_url)

        # Development mode - log the URL
        logger.warning(
            f"No email service configured. Verification URL for {username}: {verification_url}"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False


async def _send_with_resend(email: str, username: str, verification_url: str) -> bool:
    """Send email using Resend API."""
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": f"{settings.PROJECT_NAME} <noreply@{getattr(settings, 'EMAIL_DOMAIN', 'example.com')}>",
                    "to": [email],
                    "subject": f"Verify your {settings.PROJECT_NAME} account",
                    "html": _get_verification_email_html(username, verification_url),
                },
            )

            if response.status_code == 200:
                logger.info(f"Verification email sent to {email} via Resend")
                return True
            else:
                logger.error(f"Resend API error: {response.status_code} - {response.text}")
                return False

    except ImportError:
        logger.error("httpx not installed for Resend email")
        return False
    except Exception as e:
        logger.error(f"Resend email error: {e}")
        return False


async def _send_with_smtp(email: str, username: str, verification_url: str) -> bool:
    """Send email using SMTP."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Verify your {settings.PROJECT_NAME} account"
        msg["From"] = f"{settings.PROJECT_NAME} <{settings.SMTP_USER}>"
        msg["To"] = email

        html = _get_verification_email_html(username, verification_url)
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, msg.as_string())

        logger.info(f"Verification email sent to {email} via SMTP")
        return True

    except Exception as e:
        logger.error(f"SMTP email error: {e}")
        return False


def _get_verification_email_html(username: str, verification_url: str) -> str:
    """Get the HTML content for verification email."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{settings.PROJECT_NAME}</h1>
            </div>
            <div class="content">
                <h2>Verify your email address</h2>
                <p>Hi {username},</p>
                <p>Thanks for signing up! Please verify your email address by clicking the button below:</p>
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #6b7280; font-size: 14px;">{verification_url}</p>
                <p>This link will expire in {VERIFICATION_TOKEN_EXPIRE_HOURS} hours.</p>
                <p>If you didn't create an account, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; {settings.PROJECT_NAME}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
