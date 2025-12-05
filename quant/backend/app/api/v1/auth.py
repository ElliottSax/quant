"""Authentication API endpoints."""

from datetime import datetime

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
    response_model=Token,
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
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
) -> Token:
    """
    Authenticate user and return JWT tokens.

    Login with username or email. Returns both an access token (short-lived, 30 minutes)
    and a refresh token (long-lived, 7 days) for session management.

    **Usage:**
    1. Use access token in Authorization header: `Bearer <access_token>`
    2. When access token expires, use refresh token to get new tokens
    3. Store refresh token securely on client

    Args:
        login_data: User login credentials (username or email + password)
        db: Database session

    Returns:
        Access and refresh tokens

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

    # Update last login and reset failed attempts
    user.last_login = datetime.utcnow()
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
    logger.debug("Token refresh attempt")

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
    current_user.updated_at = datetime.utcnow()
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
