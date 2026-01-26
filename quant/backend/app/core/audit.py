"""
Audit logging system for tracking sensitive operations.

Features:
- Automatic logging of sensitive operations
- User action tracking
- Data modification history
- Security event logging
- Compliance reporting
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
import json
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, JSON, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from fastapi import Request

from app.core.database import Base
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_CHANGE_FAILED = "password_change_failed"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_DELETED = "account_deleted"

    # Two-Factor Authentication events
    TWO_FACTOR_ENABLED = "two_factor_enabled"
    TWO_FACTOR_DISABLED = "two_factor_disabled"
    TWO_FACTOR_FAILED = "two_factor_failed"

    # Email verification events
    EMAIL_VERIFIED = "email_verified"
    EMAIL_VERIFICATION_SENT = "email_verification_sent"
    
    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"
    
    # Data events
    DATA_CREATED = "data_created"
    DATA_READ = "data_read"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    
    # Security events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    
    # Admin events
    CONFIG_CHANGED = "config_changed"
    SYSTEM_RESTART = "system_restart"
    BACKUP_CREATED = "backup_created"
    
    # ML/Analytics events
    ML_MODEL_TRAINED = "ml_model_trained"
    ML_PREDICTION_MADE = "ml_prediction_made"
    EXPENSIVE_QUERY = "expensive_query"


class AuditSeverity(str, Enum):
    """Severity levels for audit events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    """Audit log database model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default=AuditSeverity.INFO)
    
    # User information
    user_id = Column(String(36), index=True)  # UUID as string
    username = Column(String(100))
    user_email = Column(String(255))
    
    # Request information
    ip_address = Column(String(45))  # Supports IPv6
    user_agent = Column(String(500))
    request_method = Column(String(10))
    request_path = Column(String(500))
    request_id = Column(String(36))  # For request correlation
    
    # Event details
    resource_type = Column(String(50))  # e.g., "politician", "trade", "user"
    resource_id = Column(String(36))  # ID of affected resource
    action = Column(String(50))  # Specific action performed
    result = Column(String(20))  # "success", "failure", "partial"
    
    # Additional data
    event_metadata = Column("metadata", JSON)  # Flexible field for event-specific data
    error_message = Column(Text)
    
    # Compliance fields
    data_classification = Column(String(20))  # "public", "internal", "confidential", "restricted"
    compliance_tags = Column(JSON)  # ["GDPR", "SOC2", etc.]
    
    # Note: Add indexes via migrations for better control


class AuditEventSchema(BaseModel):
    """Schema for audit events"""
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.INFO
    user_id: Optional[str] = None
    username: Optional[str] = None
    user_email: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    result: str = "success"
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    data_classification: Optional[str] = "internal"
    compliance_tags: Optional[List[str]] = None


class AuditLogger:
    """
    Centralized audit logging service.
    
    Handles logging of all sensitive operations with
    automatic context capture and compliance features.
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize audit logger.
        
        Args:
            db_session: Database session for persisting logs
        """
        self.db = db_session
        self._request_context: Optional[Request] = None
    
    def set_request_context(self, request: Request):
        """Set request context for automatic capture."""
        self._request_context = request
    
    def _extract_request_info(self, request: Optional[Request] = None) -> Dict[str, Any]:
        """Extract information from request."""
        req = request or self._request_context
        
        if not req:
            return {}
        
        # Get IP address
        ip = req.client.host if req.client else "unknown"
        if "X-Forwarded-For" in req.headers:
            ip = req.headers["X-Forwarded-For"].split(",")[0].strip()
        elif "X-Real-IP" in req.headers:
            ip = req.headers["X-Real-IP"]
        
        # Hash IP for privacy (keep first two octets for geo)
        ip_parts = ip.split(".")
        if len(ip_parts) == 4:
            ip_hash = f"{ip_parts[0]}.{ip_parts[1]}.*.*"
        else:
            ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
        
        return {
            "ip_address": ip_hash,
            "user_agent": req.headers.get("User-Agent", "")[:500],
            "request_method": req.method,
            "request_path": str(req.url.path),
            "request_id": req.headers.get("X-Request-ID", "")
        }
    
    async def log_event(
        self,
        event: AuditEventSchema,
        request: Optional[Request] = None
    ) -> Optional[AuditLog]:
        """
        Log an audit event.
        
        Args:
            event: Audit event details
            request: Optional request context
            
        Returns:
            Created audit log entry
        """
        try:
            # Extract request information
            request_info = self._extract_request_info(request)
            
            # Create audit log entry
            audit_log = AuditLog(
                event_type=event.event_type,
                severity=event.severity,
                user_id=event.user_id,
                username=event.username,
                user_email=event.user_email,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                action=event.action,
                result=event.result,
                event_metadata=event.metadata,
                error_message=event.error_message,
                data_classification=event.data_classification,
                compliance_tags=event.compliance_tags,
                **request_info
            )
            
            # Persist to database if session available
            if self.db:
                self.db.add(audit_log)
                await self.db.commit()
                await self.db.refresh(audit_log)
            
            # Also log to application logs for redundancy
            log_data = {
                "event_type": event.event_type,
                "severity": event.severity,
                "user_id": event.user_id,
                "action": event.action,
                "result": event.result,
                "resource": f"{event.resource_type}:{event.resource_id}" if event.resource_type else None
            }
            
            if event.severity == AuditSeverity.CRITICAL:
                logger.critical(f"Audit Event: {json.dumps(log_data)}")
            elif event.severity == AuditSeverity.ERROR:
                logger.error(f"Audit Event: {json.dumps(log_data)}")
            elif event.severity == AuditSeverity.WARNING:
                logger.warning(f"Audit Event: {json.dumps(log_data)}")
            else:
                logger.info(f"Audit Event: {json.dumps(log_data)}")
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}", exc_info=True)
            return None
    
    async def log_login(
        self,
        user_id: str,
        username: str,
        success: bool,
        request: Optional[Request] = None,
        error_message: Optional[str] = None
    ):
        """Log login attempt."""
        await self.log_event(
            AuditEventSchema(
                event_type=AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILED,
                severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
                user_id=user_id if success else None,
                username=username,
                action="user_login",
                result="success" if success else "failure",
                error_message=error_message,
                compliance_tags=["AUTH"]
            ),
            request
        )
    
    async def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        request: Optional[Request] = None,
        data_classification: str = "internal"
    ):
        """Log data access event."""
        await self.log_event(
            AuditEventSchema(
                event_type=AuditEventType.DATA_READ,
                severity=AuditSeverity.INFO,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                data_classification=data_classification,
                compliance_tags=["DATA_ACCESS"]
            ),
            request
        )
    
    async def log_data_modification(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log data modification event."""
        event_type = {
            "create": AuditEventType.DATA_CREATED,
            "update": AuditEventType.DATA_UPDATED,
            "delete": AuditEventType.DATA_DELETED
        }.get(action, AuditEventType.DATA_UPDATED)
        
        await self.log_event(
            AuditEventSchema(
                event_type=event_type,
                severity=AuditSeverity.INFO,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                metadata={"changes": changes} if changes else None,
                compliance_tags=["DATA_MODIFICATION"]
            ),
            request
        )
    
    async def log_security_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        description: str,
        user_id: Optional[str] = None,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log security-related event."""
        await self.log_event(
            AuditEventSchema(
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                action=description,
                metadata=metadata,
                compliance_tags=["SECURITY"]
            ),
            request
        )
    
    async def log_ml_operation(
        self,
        user_id: str,
        operation: str,
        model: str,
        resource_id: Optional[str] = None,
        execution_time: Optional[float] = None,
        request: Optional[Request] = None
    ):
        """Log ML/Analytics operation."""
        await self.log_event(
            AuditEventSchema(
                event_type=AuditEventType.ML_PREDICTION_MADE,
                severity=AuditSeverity.INFO,
                user_id=user_id,
                resource_type="ml_model",
                resource_id=resource_id,
                action=operation,
                metadata={
                    "model": model,
                    "execution_time": execution_time
                },
                compliance_tags=["ML_OPERATION"]
            ),
            request
        )


# Global audit logger instance
audit_logger = AuditLogger()


# Decorator for automatic audit logging
def audit_log(
    event_type: AuditEventType,
    resource_type: Optional[str] = None,
    severity: AuditSeverity = AuditSeverity.INFO
):
    """
    Decorator for automatic audit logging of functions.
    
    Usage:
        @audit_log(AuditEventType.DATA_READ, "politician")
        async def get_politician(politician_id: str, user: User):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract relevant information
            user_id = None
            resource_id = None
            
            # Try to extract user from kwargs
            if "current_user" in kwargs:
                user_id = str(kwargs["current_user"].id)
            elif "user" in kwargs:
                user_id = str(kwargs["user"].id)
            
            # Try to extract resource ID
            for key in ["id", "politician_id", "trade_id", "resource_id"]:
                if key in kwargs:
                    resource_id = str(kwargs[key])
                    break
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Log success
                await audit_logger.log_event(
                    AuditEventSchema(
                        event_type=event_type,
                        severity=severity,
                        user_id=user_id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        action=func.__name__,
                        result="success"
                    )
                )
                
                return result
                
            except Exception as e:
                # Log failure
                await audit_logger.log_event(
                    AuditEventSchema(
                        event_type=event_type,
                        severity=AuditSeverity.ERROR,
                        user_id=user_id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        action=func.__name__,
                        result="failure",
                        error_message=str(e)
                    )
                )
                raise
        
        return wrapper
    return decorator