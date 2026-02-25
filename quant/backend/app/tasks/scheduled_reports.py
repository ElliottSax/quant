"""
Celery Tasks for Scheduled Reports

Background tasks for automated report generation and delivery.
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Celery setup
try:
    from celery import Celery
    from app.core.config import settings

    celery_app = Celery(
        'quant_tasks',
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL
    )

    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("Celery not installed. Install with: pip install celery")
    celery_app = None


if CELERY_AVAILABLE:
    @celery_app.task(name='generate_daily_report')
    def generate_daily_report_task(user_emails: List[str]):
        """
        Generate and email daily report

        Args:
            user_emails: List of emails to send to
        """
        import asyncio
        from app.services.reporting import get_report_generator, ReportFormat
        from app.services.email_service import get_email_service

        async def _generate_and_send():
            # Generate report
            generator = get_report_generator()
            report = await generator.generate_daily_summary()

            # Convert to HTML
            html_content = generator.to_html(report)

            # Send email
            email_service = get_email_service()
            success = await email_service.send_report(
                to=user_emails,
                report_html=html_content,
                report_title="Daily Trading Summary"
            )

            return success

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_generate_and_send())


    @celery_app.task(name='generate_weekly_report')
    def generate_weekly_report_task(user_emails: List[str]):
        """
        Generate and email weekly performance report

        Args:
            user_emails: List of emails to send to
        """
        import asyncio
        from app.services.reporting import get_report_generator
        from app.services.email_service import get_email_service

        async def _generate_and_send():
            generator = get_report_generator()
            report = await generator.generate_weekly_performance()
            html_content = generator.to_html(report)

            email_service = get_email_service()
            return await email_service.send_report(
                to=user_emails,
                report_html=html_content,
                report_title="Weekly Performance Report"
            )

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_generate_and_send())


    @celery_app.task(name='generate_monthly_report')
    def generate_monthly_report_task(user_emails: List[str]):
        """
        Generate and email monthly analysis report

        Args:
            user_emails: List of emails to send to
        """
        import asyncio
        from app.services.reporting import get_report_generator
        from app.services.email_service import get_email_service

        async def _generate_and_send():
            generator = get_report_generator()
            # Use weekly report as template for monthly
            report = await generator.generate_weekly_performance()
            html_content = generator.to_html(report)

            email_service = get_email_service()
            return await email_service.send_report(
                to=user_emails,
                report_html=html_content,
                report_title="Monthly Analysis Report"
            )

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_generate_and_send())


    @celery_app.task(name='send_signal_alert')
    def send_signal_alert_task(
        user_emails: List[str],
        signal: Dict,
        symbol: str
    ):
        """
        Send alert for new trading signal

        Args:
            user_emails: List of emails
            signal: Signal data
            symbol: Stock symbol
        """
        import asyncio
        from app.services.email_service import get_email_service, EmailMessage

        async def _send():
            # Create alert email
            html = f"""
            <html>
            <head><style>
                body {{ font-family: Arial, sans-serif; }}
                .signal {{ padding: 20px; background: #f5f5f5; border-radius: 8px; }}
                .buy {{ color: #10b981; }}
                .sell {{ color: #ef4444; }}
            </style></head>
            <body>
                <div class="signal">
                    <h2>New Trading Signal: {symbol}</h2>
                    <p class="{signal['signal_type']}">
                        <strong>Signal:</strong> {signal['signal_type'].upper()}
                    </p>
                    <p><strong>Confidence:</strong> {signal['confidence_score']*100:.1f}%</p>
                    <p><strong>Price:</strong> ${signal['price']:.2f}</p>
                    <p><strong>Reasoning:</strong> {signal['reasoning']}</p>
                </div>
            </body>
            </html>
            """

            message = EmailMessage(
                to=user_emails,
                subject=f"🔔 {signal['signal_type'].upper()} Signal: {symbol}",
                body_text=f"New {signal['signal_type']} signal for {symbol}",
                body_html=html
            )

            email_service = get_email_service()
            return await email_service.send_email(message)

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_send())


# Celery Beat schedule for periodic tasks
if CELERY_AVAILABLE:
    celery_app.conf.beat_schedule = {
        'daily-report-morning': {
            'task': 'generate_daily_report',
            'schedule': timedelta(days=1),  # Every day
            'args': (['admin@example.com'],)  # Configure recipient emails
        },
        'weekly-report-monday': {
            'task': 'generate_weekly_report',
            'schedule': timedelta(weeks=1),  # Every week
            'args': (['admin@example.com'],)
        }
    }


# Helper functions for manual task triggering
def schedule_daily_report(emails: List[str], delay_seconds: int = 0):
    """Schedule daily report generation"""
    if not CELERY_AVAILABLE:
        logger.warning("Celery not available")
        return None

    if delay_seconds > 0:
        return generate_daily_report_task.apply_async(args=[emails], countdown=delay_seconds)
    else:
        return generate_daily_report_task.delay(emails)


def schedule_weekly_report(emails: List[str], delay_seconds: int = 0):
    """Schedule weekly report generation"""
    if not CELERY_AVAILABLE:
        logger.warning("Celery not available")
        return None

    if delay_seconds > 0:
        return generate_weekly_report_task.apply_async(args=[emails], countdown=delay_seconds)
    else:
        return generate_weekly_report_task.delay(emails)


# Usage examples
"""
# Start Celery worker:
celery -A app.tasks.scheduled_reports worker --loglevel=info

# Start Celery beat scheduler:
celery -A app.tasks.scheduled_reports beat --loglevel=info

# Trigger tasks manually:
from app.tasks.scheduled_reports import schedule_daily_report
schedule_daily_report(['user@example.com'])

# Schedule for later (in 1 hour):
schedule_daily_report(['user@example.com'], delay_seconds=3600)
"""
