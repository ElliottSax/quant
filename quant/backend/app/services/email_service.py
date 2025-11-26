"""
Email Delivery Service

Send automated reports via email.
"""

from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


class EmailProvider(str, Enum):
    """Email service providers"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"
    MAILGUN = "mailgun"


class EmailMessage(BaseModel):
    """Email message"""
    to: List[EmailStr]
    subject: str
    body_text: str
    body_html: Optional[str] = None
    attachments: List[Dict] = []
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []


class EmailService:
    """
    Email delivery service

    Supports multiple providers:
    - SMTP (Gmail, Outlook, etc.)
    - SendGrid
    - AWS SES
    - Mailgun
    """

    def __init__(
        self,
        provider: EmailProvider = EmailProvider.SMTP,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: str = "Quant Analytics Platform"
    ):
        self.provider = provider
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or self.smtp_user
        self.from_name = from_name

    async def send_email(self, message: EmailMessage) -> bool:
        """
        Send email

        Args:
            message: Email message to send

        Returns:
            True if sent successfully
        """
        if self.provider == EmailProvider.SMTP:
            return await self._send_smtp(message)
        elif self.provider == EmailProvider.SENDGRID:
            return await self._send_sendgrid(message)
        elif self.provider == EmailProvider.AWS_SES:
            return await self._send_ses(message)
        elif self.provider == EmailProvider.MAILGUN:
            return await self._send_mailgun(message)
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")

    async def _send_smtp(self, message: EmailMessage) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(message.to)
            msg['Subject'] = message.subject

            if message.cc:
                msg['Cc'] = ', '.join(message.cc)

            # Add body
            msg.attach(MIMEText(message.body_text, 'plain'))
            if message.body_html:
                msg.attach(MIMEText(message.body_html, 'html'))

            # Add attachments
            for attachment in message.attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f"attachment; filename= {attachment['filename']}"
                )
                msg.attach(part)

            # Send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                recipients = message.to + message.cc + message.bcc
                server.send_message(msg, to_addrs=recipients)

            return True

        except Exception as e:
            print(f"SMTP send failed: {e}")
            return False

    async def _send_sendgrid(self, message: EmailMessage) -> bool:
        """Send email via SendGrid API"""
        try:
            # Import SendGrid
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content

            # Get API key
            api_key = os.getenv('SENDGRID_API_KEY')
            if not api_key:
                print("SendGrid API key not found")
                return False

            # Create message
            sg_message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=[To(email) for email in message.to],
                subject=message.subject,
                plain_text_content=Content('text/plain', message.body_text)
            )

            if message.body_html:
                sg_message.content = [
                    Content('text/plain', message.body_text),
                    Content('text/html', message.body_html)
                ]

            # Send
            sg = SendGridAPIClient(api_key)
            response = sg.send(sg_message)

            return response.status_code in [200, 201, 202]

        except ImportError:
            print("SendGrid not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            print(f"SendGrid send failed: {e}")
            return False

    async def _send_ses(self, message: EmailMessage) -> bool:
        """Send email via AWS SES"""
        try:
            import boto3

            # Get SES client
            ses = boto3.client('ses', region_name=os.getenv('AWS_REGION', 'us-east-1'))

            # Prepare email
            email_data = {
                'Source': f"{self.from_name} <{self.from_email}>",
                'Destination': {
                    'ToAddresses': message.to,
                },
                'Message': {
                    'Subject': {'Data': message.subject},
                    'Body': {}
                }
            }

            if message.cc:
                email_data['Destination']['CcAddresses'] = message.cc
            if message.bcc:
                email_data['Destination']['BccAddresses'] = message.bcc

            # Add body
            if message.body_html:
                email_data['Message']['Body']['Html'] = {'Data': message.body_html}
            else:
                email_data['Message']['Body']['Text'] = {'Data': message.body_text}

            # Send
            response = ses.send_email(**email_data)
            return 'MessageId' in response

        except ImportError:
            print("boto3 not installed. Install with: pip install boto3")
            return False
        except Exception as e:
            print(f"SES send failed: {e}")
            return False

    async def _send_mailgun(self, message: EmailMessage) -> bool:
        """Send email via Mailgun API"""
        try:
            import httpx

            api_key = os.getenv('MAILGUN_API_KEY')
            domain = os.getenv('MAILGUN_DOMAIN')

            if not api_key or not domain:
                print("Mailgun credentials not found")
                return False

            # Prepare data
            data = {
                'from': f"{self.from_name} <{self.from_email}>",
                'to': message.to,
                'subject': message.subject,
                'text': message.body_text
            }

            if message.body_html:
                data['html'] = message.body_html
            if message.cc:
                data['cc'] = message.cc
            if message.bcc:
                data['bcc'] = message.bcc

            # Send
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.mailgun.net/v3/{domain}/messages",
                    auth=("api", api_key),
                    data=data
                )
                return response.status_code == 200

        except Exception as e:
            print(f"Mailgun send failed: {e}")
            return False

    async def send_report(
        self,
        to: List[str],
        report_html: str,
        report_title: str,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send report via email

        Args:
            to: List of recipient emails
            report_html: HTML content of report
            report_title: Subject line
            attachments: Optional file attachments

        Returns:
            True if sent successfully
        """
        message = EmailMessage(
            to=to,
            subject=f"{report_title} - {datetime.utcnow().strftime('%Y-%m-%d')}",
            body_text="Please view this email in HTML format to see the report.",
            body_html=report_html,
            attachments=attachments or []
        )

        return await self.send_email(message)


# Global instance
_email_service: Optional[EmailService] = None


def get_email_service(
    provider: EmailProvider = EmailProvider.SMTP,
    **kwargs
) -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService(provider=provider, **kwargs)
    return _email_service


# Configuration examples
"""
# Gmail SMTP:
EMAIL_SERVICE = get_email_service(
    provider=EmailProvider.SMTP,
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    smtp_user='your-email@gmail.com',
    smtp_password='your-app-password',  # Use App Password, not regular password
    from_email='your-email@gmail.com',
    from_name='Quant Platform'
)

# SendGrid:
EMAIL_SERVICE = get_email_service(
    provider=EmailProvider.SENDGRID,
    from_email='noreply@yourplatform.com',
    from_name='Quant Platform'
)
# Requires: SENDGRID_API_KEY environment variable

# AWS SES:
EMAIL_SERVICE = get_email_service(
    provider=EmailProvider.AWS_SES,
    from_email='noreply@yourplatform.com',
    from_name='Quant Platform'
)
# Requires: AWS credentials configured

# Mailgun:
EMAIL_SERVICE = get_email_service(
    provider=EmailProvider.MAILGUN,
    from_email='noreply@yourplatform.com',
    from_name='Quant Platform'
)
# Requires: MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables
"""
