"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username is alphanumeric with underscores."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=100, description="User password")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )

        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: datetime | None
    email_verified: bool = False
    totp_enabled: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="Refresh token")


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: str  # Subject (user ID)
    exp: int  # Expiration timestamp
    type: str  # Token type (access or refresh)


class PasswordChange(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )

        return v


# Two-Factor Authentication Schemas
class TwoFactorSetupResponse(BaseModel):
    """Response for 2FA setup initialization."""

    secret: str = Field(..., description="TOTP secret (base32)")
    provisioning_uri: str = Field(..., description="otpauth:// URI for authenticator apps")
    qr_code: str = Field(..., description="Base64 encoded QR code PNG")


class TwoFactorVerify(BaseModel):
    """Schema for verifying 2FA code."""

    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")


class TwoFactorEnableResponse(BaseModel):
    """Response after enabling 2FA."""

    enabled: bool = True
    backup_codes: list[str] = Field(..., description="Backup codes for recovery")
    message: str = "Two-factor authentication enabled successfully"


class TwoFactorDisable(BaseModel):
    """Schema for disabling 2FA."""

    password: str = Field(..., description="Current password for verification")
    token: str = Field(..., min_length=6, max_length=6, description="Current 2FA code")


class TwoFactorLoginVerify(BaseModel):
    """Schema for 2FA verification during login."""

    user_id: str = Field(..., description="User ID from initial login")
    token: str = Field(..., description="6-digit TOTP code or backup code")


class TwoFactorStatus(BaseModel):
    """Schema for 2FA status check."""

    enabled: bool
    backup_codes_remaining: int = 0


# Email Verification Schemas
class EmailVerificationRequest(BaseModel):
    """Schema for requesting email verification."""

    pass  # No body needed, uses authenticated user


class EmailVerificationConfirm(BaseModel):
    """Schema for confirming email verification."""

    token: str = Field(..., description="Email verification token")


class EmailVerificationResponse(BaseModel):
    """Response for email verification operations."""

    message: str
    email_verified: bool = False
