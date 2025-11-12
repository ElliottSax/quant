"""Authentication API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token,
)
from app.core.deps import get_current_user, get_current_active_user
from app.core.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ConflictException,
)
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    TokenRefresh,
)

logger = get_logger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user

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
    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Authenticate user and return tokens.

    Args:
        login_data: User login credentials
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

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Login failed - incorrect password: {login_data.username}")
        raise UnauthorizedException("Incorrect username or password")

    if not user.is_active:
        logger.warning(f"Login failed - inactive user: {login_data.username}")
        raise UnauthorizedException("Inactive user")

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

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
    user_id = verify_token(refresh_data.refresh_token, token_type="refresh")
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

    # Create new tokens
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))

    logger.info(f"Token refreshed for user: {user.username}")

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
) -> None:
    """
    Logout user (client should discard tokens).

    Args:
        current_user: Current authenticated user

    Note:
        Since we're using stateless JWT tokens, logout is handled client-side
        by discarding the tokens. This endpoint is provided for completeness
        and could be extended with token blacklisting if needed.
    """
    logger.info(f"User logged out: {current_user.username}")
    # In a production system, you might want to blacklist the token here
    return None
