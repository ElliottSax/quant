"""Authentication API endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token,
    is_account_locked,
    get_lockout_time_remaining,
    handle_failed_login,
    reset_failed_login_attempts,
)
from app.core.deps import get_current_user, get_current_active_user
from app.core.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ConflictException,
)
from app.core.logging import get_logger
from app.core.audit import audit_logger, AuditEventType, AuditSeverity
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    TokenRefresh,
    PasswordChange,
    TwoFactorSetupResponse,
    TwoFactorVerify,
    TwoFactorEnableResponse,
    TwoFactorDisable,
    TwoFactorLoginVerify,
    TwoFactorStatus,
    EmailVerificationConfirm,
    EmailVerificationResponse,
)

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "username": "johndoe",
                        "is_active": True,
                        "is_superuser": False,
                        "created_at": "2025-01-15T10:30:00Z",
                        "last_login": None
                    }
                }
            }
        },
        409: {"description": "Username or email already exists"},
        422: {"description": "Validation error"}
    }
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user account.

    Creates a new user with the provided credentials. The password will be securely
    hashed before storage. Usernames must be unique and alphanumeric (underscores allowed).

    **Password Requirements:**
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user (password not included in response)

    Raises:
        ConflictException: If username or email already exists
    """
    logger.info(f"Attempting to register user: {user_data.username}")

    # Check if user already exists
    query = select(User).where(
        or_(User.username == user_data.username, User.email == user_data.email)
    )
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.username == user_data.username:
            logger.warning(f"Username already exists: {user_data.username}")
            raise ConflictException("Username already registered")
        else:
            logger.warning(f"Email already exists: {user_data.email}")
            raise ConflictException("Email already registered")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"User registered successfully: {new_user.username}")
    
    # Audit log registration
    from app.core.audit import AuditEventSchema
    await audit_logger.log_event(
        AuditEventSchema(
            event_type=AuditEventType.ACCOUNT_CREATED,
            severity=AuditSeverity.INFO,
            user_id=str(new_user.id),
            username=new_user.username,
            user_email=new_user.email,
            action="user_registration",
            result="success"
        )
    )
    
    return UserResponse.model_validate(new_user)


@router.post(
    "/login",
    responses={
        200: {
            "description": "Login successful or 2FA required",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Direct login (no 2FA)",
                            "value": {
                                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                "token_type": "bearer"
                            }
                        },
                        "2fa_required": {
                            "summary": "2FA verification required",
                            "value": {
                                "requires_2fa": True,
                                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                                "message": "Two-factor authentication required"
                            }
                        }
                    }
                }
            }
        },
        401: {"description": "Invalid credentials or inactive user"}
    }
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token | dict:
    """
    Authenticate user and return JWT tokens.

    Login with username or email. If 2FA is enabled, returns a user_id
    that must be used with /auth/2fa/verify to complete login.

    **Usage:**
    1. Call this endpoint with credentials
    2. If 2FA is enabled, call /auth/2fa/verify with user_id and TOTP code
    3. Use access token in Authorization header: `Bearer <access_token>`
    4. When access token expires, use refresh token to get new tokens

    Args:
        login_data: User login credentials (username or email + password)
        db: Database session

    Returns:
        Access and refresh tokens, or 2FA required response

    Raises:
        UnauthorizedException: If credentials are invalid
    """
    logger.info(f"Login attempt for: {login_data.username}")

    # Find user by username or email
    query = select(User).where(
        or_(User.username == login_data.username, User.email == login_data.username)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Login failed - user not found: {login_data.username}")
        raise UnauthorizedException("Incorrect username or password")

    # Check if account is locked
    if is_account_locked(user):
        remaining = get_lockout_time_remaining(user)
        minutes = remaining // 60
        logger.warning(f"Login attempt on locked account: {login_data.username}, {minutes}min remaining")
        raise UnauthorizedException(
            f"Account is locked due to too many failed login attempts. "
            f"Try again in {minutes} minutes."
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Login failed - incorrect password: {login_data.username}")
        # Track failed login attempt
        await handle_failed_login(user, db)
        raise UnauthorizedException("Incorrect username or password")

    if not user.is_active:
        logger.warning(f"Login failed - inactive user: {login_data.username}")
        raise UnauthorizedException("Inactive user")

    # Check if 2FA is enabled
    if user.totp_enabled:
        logger.info(f"2FA required for user: {user.username}")
        # Reset failed attempts on successful password verification
        user.failed_login_attempts = 0
        user.locked_until = None
        await db.commit()
        return {
            "requires_2fa": True,
            "user_id": str(user.id),
            "message": "Two-factor authentication required",
        }

    # Update last login and reset failed attempts
    user.last_login = datetime.now(timezone.utc)
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()

    # Create tokens with current version
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(
        subject=str(user.id),
        version=user.refresh_token_version
    )

    logger.info(f"User logged in successfully: {user.username}")

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Refresh access token using refresh token.

    Args:
        refresh_data: Refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        UnauthorizedException: If refresh token is invalid
    """
    from app.core.token_blacklist import token_blacklist

    logger.debug("Token refresh attempt")

    # Check if token is blacklisted before processing
    if await token_blacklist.is_blacklisted(refresh_data.refresh_token):
        logger.warning("Attempted refresh with blacklisted token")
        raise UnauthorizedException("Token has been revoked")

    # Verify refresh token
    user_id, token_version = verify_token(refresh_data.refresh_token, token_type="refresh")
    if not user_id:
        logger.warning("Invalid or expired refresh token")
        raise UnauthorizedException("Invalid or expired refresh token")

    # Get user from database
    from uuid import UUID

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise UnauthorizedException("Invalid refresh token")

    query = select(User).where(User.id == user_uuid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        logger.warning(f"Refresh failed - user not found or inactive: {user_id}")
        raise UnauthorizedException("User not found or inactive")

    # Verify token version matches (prevent token reuse after rotation)
    if token_version != user.refresh_token_version:
        logger.warning(f"Refresh token version mismatch for user {user_id}: {token_version} != {user.refresh_token_version}")
        raise UnauthorizedException("Refresh token has been revoked")

    # Rotate: increment version and issue new tokens
    user.refresh_token_version += 1
    await db.commit()

    # Create new tokens with new version
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(
        subject=str(user.id),
        version=user.refresh_token_version
    )

    logger.info(f"Token refreshed and rotated for user: {user.username}, new version: {user.refresh_token_version}")

    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    logger.debug(f"User info requested: {current_user.username}")
    return UserResponse.model_validate(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> None:
    """
    Logout user and invalidate current token.

    The access token will be blacklisted until it naturally expires.
    Client should also discard both access and refresh tokens.

    Args:
        current_user: Current authenticated user
        credentials: Authorization credentials with token

    Note:
        This blacklists only the current access token. Refresh tokens
        should not be reused after logout on the client side.
    """
    from app.core.token_blacklist import token_blacklist
    from app.core.audit import AuditEventSchema

    token = credentials.credentials

    # Blacklist the current token
    await token_blacklist.blacklist_token(token)

    logger.info(f"User logged out: {current_user.username}")

    # Audit log logout
    await audit_logger.log_event(
        AuditEventSchema(
            event_type=AuditEventType.LOGOUT,
            severity=AuditSeverity.INFO,
            user_id=str(current_user.id),
            username=current_user.username,
            user_email=current_user.email,
            action="user_logout",
            result="success"
        )
    )

    return None


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Change user password.

    This will:
    1. Verify the current password
    2. Update to new password
    3. Invalidate all existing sessions (user must re-login)

    Args:
        password_data: Current and new password
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        UnauthorizedException: If current password is incorrect
    """
    from app.core.token_blacklist import token_blacklist
    from app.core.audit import AuditEventSchema

    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        logger.warning(f"Password change failed - incorrect current password: {current_user.username}")
        await audit_logger.log_event(
            AuditEventSchema(
                event_type=AuditEventType.PASSWORD_CHANGE_FAILED,
                severity=AuditSeverity.WARNING,
                user_id=str(current_user.id),
                username=current_user.username,
                user_email=current_user.email,
                action="password_change_attempt",
                result="failed"
            )
        )
        raise UnauthorizedException("Incorrect current password")

    # Don't allow changing to same password
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise BadRequestException("New password must be different from current password")

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    # Invalidate all user sessions
    await token_blacklist.blacklist_user_tokens(str(current_user.id))

    logger.info(f"Password changed successfully: {current_user.username}")

    # Audit log password change
    await audit_logger.log_event(
        AuditEventSchema(
            event_type=AuditEventType.PASSWORD_CHANGED,
            severity=AuditSeverity.INFO,
            user_id=str(current_user.id),
            username=current_user.username,
            user_email=current_user.email,
            action="password_change",
            result="success"
        )
    )

    return {
        "message": "Password changed successfully. Please login again with your new password.",
        "sessions_invalidated": True
    }


# ============================================================================
# Two-Factor Authentication Endpoints
# ============================================================================


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> TwoFactorSetupResponse:
    """
    Initialize 2FA setup for the current user.

    Returns a TOTP secret, provisioning URI, and QR code for authenticator apps.
    The user must verify a code before 2FA is enabled.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Setup information including QR code

    Raises:
        BadRequestException: If 2FA is already enabled
    """
    from app.core.two_factor import (
        generate_totp_secret,
        generate_provisioning_uri,
        generate_qr_code_base64,
    )

    if current_user.totp_enabled:
        raise BadRequestException("Two-factor authentication is already enabled")

    # Generate new secret
    secret = generate_totp_secret()

    # Store temporarily (user must verify before it's active)
    current_user.totp_secret = secret
    await db.commit()

    # Generate provisioning URI and QR code
    provisioning_uri = generate_provisioning_uri(secret, current_user.email)
    qr_code = generate_qr_code_base64(provisioning_uri)

    logger.info(f"2FA setup initiated for user: {current_user.username}")

    return TwoFactorSetupResponse(
        secret=secret,
        provisioning_uri=provisioning_uri,
        qr_code=qr_code,
    )


@router.post("/2fa/enable", response_model=TwoFactorEnableResponse)
async def enable_two_factor(
    verify_data: TwoFactorVerify,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> TwoFactorEnableResponse:
    """
    Enable 2FA after verifying the initial code.

    User must have called /2fa/setup first and provide a valid TOTP code.

    Args:
        verify_data: TOTP code to verify
        current_user: Current authenticated user
        db: Database session

    Returns:
        Confirmation with backup codes

    Raises:
        BadRequestException: If 2FA setup not initiated or code invalid
    """
    from app.core.two_factor import verify_totp, generate_backup_codes, hash_backup_codes
    from app.core.audit import AuditEventSchema

    if current_user.totp_enabled:
        raise BadRequestException("Two-factor authentication is already enabled")

    if not current_user.totp_secret:
        raise BadRequestException("Please initiate 2FA setup first")

    # Verify the provided code
    if not verify_totp(current_user.totp_secret, verify_data.token):
        logger.warning(f"Invalid 2FA code during enable for user: {current_user.username}")
        raise BadRequestException("Invalid verification code")

    # Generate backup codes
    backup_codes = generate_backup_codes()

    # Enable 2FA
    current_user.totp_enabled = True
    current_user.totp_backup_codes = hash_backup_codes(backup_codes)
    await db.commit()

    logger.info(f"2FA enabled for user: {current_user.username}")

    # Audit log
    await audit_logger.log_event(
        AuditEventSchema(
            event_type=AuditEventType.TWO_FACTOR_ENABLED,
            severity=AuditSeverity.INFO,
            user_id=str(current_user.id),
            username=current_user.username,
            user_email=current_user.email,
            action="2fa_enabled",
            result="success",
        )
    )

    return TwoFactorEnableResponse(
        enabled=True,
        backup_codes=backup_codes,
        message="Two-factor authentication enabled successfully. Save your backup codes securely.",
    )


@router.post("/2fa/disable")
async def disable_two_factor(
    disable_data: TwoFactorDisable,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Disable 2FA for the current user.

    Requires both password and current 2FA code for security.

    Args:
        disable_data: Password and 2FA code
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    from app.core.two_factor import verify_totp
    from app.core.audit import AuditEventSchema

    if not current_user.totp_enabled:
        raise BadRequestException("Two-factor authentication is not enabled")

    # Verify password
    if not verify_password(disable_data.password, current_user.hashed_password):
        raise UnauthorizedException("Invalid password")

    # Verify 2FA code
    if not verify_totp(current_user.totp_secret, disable_data.token):
        raise BadRequestException("Invalid 2FA code")

    # Disable 2FA
    current_user.totp_enabled = False
    current_user.totp_secret = None
    current_user.totp_backup_codes = None
    await db.commit()

    logger.info(f"2FA disabled for user: {current_user.username}")

    # Audit log
    await audit_logger.log_event(
        AuditEventSchema(
            event_type=AuditEventType.TWO_FACTOR_DISABLED,
            severity=AuditSeverity.WARNING,
            user_id=str(current_user.id),
            username=current_user.username,
            user_email=current_user.email,
            action="2fa_disabled",
            result="success",
        )
    )

    return {"message": "Two-factor authentication disabled successfully"}


@router.get("/2fa/status", response_model=TwoFactorStatus)
async def get_two_factor_status(
    current_user: User = Depends(get_current_active_user),
) -> TwoFactorStatus:
    """
    Get 2FA status for the current user.

    Args:
        current_user: Current authenticated user

    Returns:
        2FA status including backup codes remaining
    """
    from app.core.two_factor import get_remaining_backup_codes_count

    return TwoFactorStatus(
        enabled=current_user.totp_enabled,
        backup_codes_remaining=get_remaining_backup_codes_count(current_user.totp_backup_codes),
    )


@router.post("/2fa/verify", response_model=Token)
async def verify_two_factor_login(
    verify_data: TwoFactorLoginVerify,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Complete login with 2FA verification.

    Called after initial login returns a 2FA required response.

    Args:
        verify_data: User ID and 2FA code
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        UnauthorizedException: If code is invalid
    """
    from uuid import UUID
    from app.core.two_factor import verify_totp, verify_backup_code

    # Get user
    try:
        user_uuid = UUID(verify_data.user_id)
    except ValueError:
        raise UnauthorizedException("Invalid user ID")

    query = select(User).where(User.id == user_uuid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    if not user.totp_enabled or not user.totp_secret:
        raise BadRequestException("2FA is not enabled for this user")

    # Try TOTP code first
    token_value = verify_data.token.strip()

    if len(token_value) == 6 and token_value.isdigit():
        # Standard TOTP code
        if not verify_totp(user.totp_secret, token_value):
            logger.warning(f"Invalid 2FA code for user: {user.username}")
            raise UnauthorizedException("Invalid 2FA code")
    else:
        # Try backup code
        if user.totp_backup_codes:
            is_valid, updated_codes = verify_backup_code(user.totp_backup_codes, token_value)
            if is_valid:
                user.totp_backup_codes = updated_codes
                await db.commit()
                logger.info(f"Backup code used for user: {user.username}")
            else:
                raise UnauthorizedException("Invalid 2FA code or backup code")
        else:
            raise UnauthorizedException("Invalid 2FA code")

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(
        subject=str(user.id),
        version=user.refresh_token_version,
    )

    logger.info(f"2FA login completed for user: {user.username}")

    return Token(access_token=access_token, refresh_token=refresh_token)


# ============================================================================
# Email Verification Endpoints
# ============================================================================


@router.post("/email/send-verification", response_model=EmailVerificationResponse)
async def send_verification_email(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> EmailVerificationResponse:
    """
    Send email verification link to current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    from app.core.email_verification import (
        create_verification_token,
        send_verification_email as send_email,
        is_token_expired,
    )

    if current_user.email_verified:
        return EmailVerificationResponse(
            message="Email is already verified",
            email_verified=True,
        )

    # Check rate limiting (don't resend if recently sent)
    if (
        current_user.email_verification_sent_at
        and not is_token_expired(current_user.email_verification_sent_at)
    ):
        # Allow resend after 5 minutes
        from datetime import timedelta
        resend_after = current_user.email_verification_sent_at + timedelta(minutes=5)
        if datetime.now(timezone.utc) < resend_after:
            raise BadRequestException("Please wait before requesting another verification email")

    # Create and send token
    token = await create_verification_token(current_user, db)
    await send_email(current_user.email, current_user.username, token)

    logger.info(f"Verification email sent to: {current_user.email}")

    return EmailVerificationResponse(
        message="Verification email sent. Please check your inbox.",
        email_verified=False,
    )


@router.post("/email/verify", response_model=EmailVerificationResponse)
async def verify_email(
    verify_data: EmailVerificationConfirm,
    db: AsyncSession = Depends(get_db),
) -> EmailVerificationResponse:
    """
    Verify email with token.

    Args:
        verify_data: Verification token
        db: Database session

    Returns:
        Success message
    """
    from app.core.email_verification import is_token_expired
    from app.core.audit import AuditEventSchema

    # Find user by token
    query = select(User).where(User.email_verification_token == verify_data.token)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise BadRequestException("Invalid verification token")

    if user.email_verified:
        return EmailVerificationResponse(
            message="Email is already verified",
            email_verified=True,
        )

    # Check token expiration
    if is_token_expired(user.email_verification_sent_at):
        raise BadRequestException("Verification token has expired. Please request a new one.")

    # Verify email
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_sent_at = None
    await db.commit()

    logger.info(f"Email verified for user: {user.username}")

    # Audit log
    await audit_logger.log_event(
        AuditEventSchema(
            event_type=AuditEventType.EMAIL_VERIFIED,
            severity=AuditSeverity.INFO,
            user_id=str(user.id),
            username=user.username,
            user_email=user.email,
            action="email_verified",
            result="success",
        )
    )

    return EmailVerificationResponse(
        message="Email verified successfully",
        email_verified=True,
    )
