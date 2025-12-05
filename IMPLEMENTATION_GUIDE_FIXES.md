# HIGH PRIORITY FIXES - IMPLEMENTATION GUIDE

## Fix 1: Redis Connection Configuration (CRITICAL)

### Problem
Multiple files have hardcoded Redis connections that will fail in production:
- `app/core/token_blacklist.py:32-36` - Hardcoded localhost:6379
- `app/core/cache.py:36-40` - Hardcoded localhost:6380

### Solution

#### Step 1: Update Configuration (app/core/config.py)

Add Redis configuration parsing:

```python
# app/core/config.py
from urllib.parse import urlparse

class Settings(BaseSettings):
    # ... existing fields ...

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ML_URL: str = "redis://localhost:6380/0"  # For ML caching

    @property
    def redis_config(self) -> dict:
        """Parse Redis URL into connection params."""
        parsed = urlparse(self.REDIS_URL)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
            "password": parsed.password,
            "decode_responses": True
        }

    @property
    def redis_ml_config(self) -> dict:
        """Parse Redis ML URL into connection params."""
        parsed = urlparse(self.REDIS_ML_URL)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6380,
            "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
            "password": parsed.password,
            "decode_responses": False  # ML cache uses pickle
        }
```

#### Step 2: Fix Token Blacklist (app/core/token_blacklist.py)

Replace lines 32-37 with:

```python
async def connect(self):
    """Connect to Redis"""
    if not self.enabled:
        logger.info("Token blacklist disabled in test environment")
        return

    try:
        # Use settings for Redis configuration
        self.redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await self.redis_client.ping()
        logger.info("Token blacklist connected to Redis")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis for blacklist: {e}")
        self.redis_client = None
        self.enabled = False
```

#### Step 3: Fix Cache Manager (app/core/cache.py)

Replace lines 36-41 with:

```python
async def connect(self):
    """Connect to Redis"""
    if not self.enabled:
        logger.info("Cache disabled in non-production environment")
        return

    try:
        # Use settings for Redis ML configuration
        config = settings.redis_ml_config
        self.redis_client = redis.Redis(**config)
        await self.redis_client.ping()
        logger.info("Connected to Redis cache")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Caching disabled.")
        self.redis_client = None
        self.enabled = False
```

#### Step 4: Update Environment Files

Update `.env` and `.env.example`:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_ML_URL=redis://localhost:6380/0

# Production example with password:
# REDIS_URL=redis://:mypassword@redis:6379/0
# REDIS_ML_URL=redis://:mypassword@redis-ml:6380/0
```

#### Step 5: Add Tests

```python
# tests/test_core/test_redis_config.py
import pytest
from app.core.config import Settings

def test_redis_url_parsing():
    """Test Redis URL parsing."""
    settings = Settings(
        SECRET_KEY="a" * 32,
        DATABASE_URL="postgresql://test",
        REDIS_URL="redis://:password@redis-host:6379/1"
    )

    config = settings.redis_config
    assert config["host"] == "redis-host"
    assert config["port"] == 6379
    assert config["db"] == 1
    assert config["password"] == "password"

def test_redis_url_defaults():
    """Test Redis URL with defaults."""
    settings = Settings(
        SECRET_KEY="a" * 32,
        DATABASE_URL="postgresql://test",
        REDIS_URL="redis://localhost"
    )

    config = settings.redis_config
    assert config["host"] == "localhost"
    assert config["port"] == 6379
    assert config["db"] == 0
```

---

## Fix 2: Add Comprehensive Authentication Tests

### Problem
Token blacklist and password change have no test coverage.

### Solution

Create `tests/test_security/test_token_blacklist.py`:

```python
"""Tests for token blacklist functionality."""

import pytest
from datetime import datetime, timedelta
from app.core.token_blacklist import TokenBlacklist
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def blacklist():
    """Create and connect token blacklist."""
    bl = TokenBlacklist()
    await bl.connect()
    yield bl
    await bl.close()


async def test_blacklist_token(blacklist):
    """Test token blacklisting."""
    # Create a token
    token = create_access_token(subject="test-user-id")

    # Blacklist it
    result = await blacklist.blacklist_token(token)
    assert result is True

    # Check it's blacklisted
    is_blacklisted = await blacklist.is_blacklisted(token)
    assert is_blacklisted is True


async def test_blacklist_expired_token(blacklist):
    """Test blacklisting already expired token."""
    # Create expired token
    token = create_access_token(
        subject="test-user-id",
        expires_delta=timedelta(seconds=-10)  # Already expired
    )

    # Should return True but not store it
    result = await blacklist.blacklist_token(token)
    assert result is True


async def test_blacklist_user_tokens(blacklist):
    """Test blacklisting all user tokens."""
    user_id = "test-user-123"

    # Blacklist all user tokens
    result = await blacklist.blacklist_user_tokens(user_id)
    assert result is True

    # Check user is blacklisted
    is_blacklisted = await blacklist.is_user_blacklisted(user_id)
    assert is_blacklisted is True


async def test_token_not_blacklisted(blacklist):
    """Test token that's not blacklisted."""
    token = create_access_token(subject="test-user-id")

    is_blacklisted = await blacklist.is_blacklisted(token)
    assert is_blacklisted is False


async def test_blacklist_with_redis_down(blacklist):
    """Test graceful degradation when Redis is down."""
    # Close Redis connection to simulate failure
    if blacklist.redis_client:
        await blacklist.redis_client.close()
        blacklist.redis_client = None

    # Should fail gracefully
    token = create_access_token(subject="test-user-id")
    result = await blacklist.blacklist_token(token)
    assert result is False

    # Should not block tokens when Redis is down (fail open)
    is_blacklisted = await blacklist.is_blacklisted(token)
    assert is_blacklisted is False
```

Create `tests/test_api/test_password_change.py`:

```python
"""Tests for password change functionality."""

import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.core.security import verify_password


def test_change_password_success(client: TestClient, auth_headers: dict, test_user: User):
    """Test successful password change."""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "TestPassword123",
            "new_password": "NewPassword456"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "sessions_invalidated" in data
    assert data["sessions_invalidated"] is True


def test_change_password_wrong_current(client: TestClient, auth_headers: dict):
    """Test password change with wrong current password."""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "WrongPassword123",
            "new_password": "NewPassword456"
        }
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_change_password_same_as_current(client: TestClient, auth_headers: dict):
    """Test password change with same password."""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "TestPassword123",
            "new_password": "TestPassword123"
        }
    )

    assert response.status_code == 400
    assert "different" in response.json()["detail"].lower()


def test_change_password_invalidates_old_token(client: TestClient, test_user: User):
    """Test that password change invalidates old tokens."""
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "TestPassword123"
        }
    )
    old_token = login_response.json()["access_token"]
    old_headers = {"Authorization": f"Bearer {old_token}"}

    # Change password
    client.post(
        "/api/v1/auth/change-password",
        headers=old_headers,
        json={
            "current_password": "TestPassword123",
            "new_password": "NewPassword456"
        }
    )

    # Old token should no longer work
    response = client.get("/api/v1/auth/me", headers=old_headers)
    assert response.status_code == 401

    # New password should work
    new_login = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "NewPassword456"
        }
    )
    assert new_login.status_code == 200


def test_change_password_weak_new_password(client: TestClient, auth_headers: dict):
    """Test password change with weak new password."""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "TestPassword123",
            "new_password": "weak"
        }
    )

    assert response.status_code == 422  # Validation error
```

---

## Fix 3: Implement Refresh Token Rotation

### Problem
Stolen refresh tokens remain valid for 7 days.

### Solution

#### Step 1: Update User Model to Track Refresh Tokens

```python
# app/models/user.py
from sqlalchemy import Text

class User(Base):
    # ... existing fields ...

    refresh_token_version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    # Increment this on password change or logout to invalidate all tokens
```

#### Step 2: Create Migration

```python
# alembic/versions/003_add_refresh_token_version.py
"""add refresh_token_version

Revision ID: 003
Revises: 002
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users',
        sa.Column('refresh_token_version', sa.Integer(),
                  nullable=False, server_default='0')
    )

def downgrade():
    op.drop_column('users', 'refresh_token_version')
```

#### Step 3: Update Token Creation

```python
# app/core/security.py
def create_refresh_token(subject: str, version: int = 0) -> str:
    """
    Create JWT refresh token with version.

    Args:
        subject: Token subject (user ID)
        version: Refresh token version (for rotation)

    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "ver": version  # Add version
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access", expected_version: int | None = None) -> tuple[str | None, int | None]:
    """
    Verify and decode JWT token.

    Returns:
        Tuple of (user_id, version) if valid, (None, None) otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        token_sub: str = payload.get("sub")
        token_exp: int = payload.get("exp")
        token_typ: str = payload.get("type")
        token_ver: int = payload.get("ver", 0)

        if not token_sub or not token_exp or token_typ != token_type:
            return None, None

        # Check version if provided
        if expected_version is not None and token_ver != expected_version:
            logger.warning(f"Token version mismatch: {token_ver} != {expected_version}")
            return None, None

        # Check expiration
        if datetime.fromtimestamp(token_exp) < datetime.utcnow():
            return None, None

        return token_sub, token_ver

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None, None
```

#### Step 4: Update Auth Endpoints

```python
# app/api/v1/auth.py

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Login with token rotation."""
    # ... existing authentication code ...

    # Create tokens with current version
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(
        subject=str(user.id),
        version=user.refresh_token_version
    )

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Refresh with token rotation."""
    # Verify refresh token
    user_id, token_version = verify_token(
        refresh_data.refresh_token,
        token_type="refresh"
    )

    if not user_id:
        raise UnauthorizedException("Invalid or expired refresh token")

    # Get user
    query = select(User).where(User.id == UUID(user_id))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    # Verify token version matches
    if token_version != user.refresh_token_version:
        logger.warning(f"Refresh token version mismatch for user {user_id}")
        raise UnauthorizedException("Refresh token has been revoked")

    # Rotate: increment version and issue new tokens
    user.refresh_token_version += 1
    await db.commit()

    # Issue new tokens with new version
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(
        subject=str(user.id),
        version=user.refresh_token_version
    )

    logger.info(f"Token refreshed and rotated for user: {user.username}")

    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Change password and invalidate all tokens."""
    # ... existing password verification ...

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)

    # Rotate refresh token version (invalidates all refresh tokens)
    current_user.refresh_token_version += 1
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    # Blacklist current access token
    # (refresh tokens automatically invalidated by version change)
    await token_blacklist.blacklist_user_tokens(str(current_user.id))

    logger.info(f"Password changed and all tokens invalidated: {current_user.username}")

    return {
        "message": "Password changed successfully. All sessions invalidated.",
        "sessions_invalidated": True
    }
```

#### Step 5: Add Tests

```python
# tests/test_api/test_token_rotation.py
def test_refresh_token_rotation(client: TestClient, test_user: User):
    """Test that refresh tokens are rotated on use."""
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": test_user.username, "password": "TestPassword123"}
    )
    first_refresh = login_response.json()["refresh_token"]

    # Use refresh token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh}
    )
    second_refresh = refresh_response.json()["refresh_token"]

    # Tokens should be different
    assert first_refresh != second_refresh

    # Old refresh token should no longer work
    old_refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh}
    )
    assert old_refresh_response.status_code == 401

    # New refresh token should work
    new_refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": second_refresh}
    )
    assert new_refresh_response.status_code == 200
```

---

## Fix 4: Implement Account Lockout

### Problem
No protection against brute force login attempts.

### Solution

#### Step 1: Add Failed Login Tracking to User Model

```python
# app/models/user.py
class User(Base):
    # ... existing fields ...

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
```

#### Step 2: Create Migration

```python
# alembic/versions/004_add_account_lockout.py
"""add account lockout fields

Revision ID: 004
Revises: 003
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users',
        sa.Column('failed_login_attempts', sa.Integer(),
                  nullable=False, server_default='0')
    )
    op.add_column('users',
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True)
    )

def downgrade():
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
```

#### Step 3: Add Lockout Logic

```python
# app/core/security.py
from datetime import datetime, timedelta

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

def is_account_locked(user: User) -> bool:
    """Check if user account is locked."""
    if user.locked_until is None:
        return False

    if datetime.utcnow() >= user.locked_until:
        # Lockout expired
        return False

    return True

def get_lockout_time_remaining(user: User) -> int:
    """Get remaining lockout time in seconds."""
    if user.locked_until is None:
        return 0

    remaining = (user.locked_until - datetime.utcnow()).total_seconds()
    return max(0, int(remaining))

async def handle_failed_login(user: User, db: AsyncSession) -> None:
    """Handle failed login attempt."""
    user.failed_login_attempts += 1

    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        # Lock the account
        user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        logger.warning(
            f"Account locked due to {user.failed_login_attempts} failed attempts: {user.username}"
        )

    await db.commit()

async def reset_failed_login_attempts(user: User, db: AsyncSession) -> None:
    """Reset failed login attempts on successful login."""
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()
```

#### Step 4: Update Login Endpoint

```python
# app/api/v1/auth.py

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Login with account lockout protection."""
    # Find user
    query = select(User).where(
        or_(User.username == login_data.username, User.email == login_data.username)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Login failed - user not found: {login_data.username}")
        # Don't reveal if user exists
        raise UnauthorizedException("Incorrect username or password")

    # Check if account is locked
    if is_account_locked(user):
        remaining = get_lockout_time_remaining(user)
        logger.warning(f"Login attempt on locked account: {user.username}")

        # Audit log
        await audit_logger.log_event(
            AuditEventSchema(
                event_type=AuditEventType.LOGIN_FAILED,
                severity=AuditSeverity.WARNING,
                user_id=str(user.id),
                username=user.username,
                action="login_attempt_locked_account",
                result="blocked"
            )
        )

        raise UnauthorizedException(
            f"Account temporarily locked. Try again in {remaining // 60} minutes."
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Login failed - incorrect password: {login_data.username}")

        # Handle failed attempt
        await handle_failed_login(user, db)

        # Audit log
        await audit_logger.log_event(
            AuditEventSchema(
                event_type=AuditEventType.LOGIN_FAILED,
                severity=AuditSeverity.WARNING,
                user_id=str(user.id),
                username=user.username,
                action="login_failed_wrong_password",
                result="failed"
            )
        )

        attempts_remaining = MAX_FAILED_ATTEMPTS - user.failed_login_attempts
        if attempts_remaining > 0:
            raise UnauthorizedException(
                f"Incorrect username or password. {attempts_remaining} attempts remaining."
            )
        else:
            raise UnauthorizedException(
                f"Account locked due to too many failed attempts. Try again in {LOCKOUT_DURATION_MINUTES} minutes."
            )

    if not user.is_active:
        logger.warning(f"Login failed - inactive user: {login_data.username}")
        raise UnauthorizedException("Inactive user")

    # Successful login - reset failed attempts
    await reset_failed_login_attempts(user, db)

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(
        subject=str(user.id),
        version=user.refresh_token_version
    )

    logger.info(f"User logged in successfully: {user.username}")

    # Audit log
    await audit_logger.log_event(
        AuditEventSchema(
            event_type=AuditEventType.LOGIN,
            severity=AuditSeverity.INFO,
            user_id=str(user.id),
            username=user.username,
            action="login_success",
            result="success"
        )
    )

    return Token(access_token=access_token, refresh_token=refresh_token)
```

#### Step 5: Add Admin Unlock Endpoint

```python
# app/api/v1/auth.py

@router.post("/unlock/{user_id}", dependencies=[Depends(get_current_superuser)])
async def unlock_account(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Unlock a user account (superuser only)."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User", str(user_id))

    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()

    logger.info(f"Account unlocked by admin: {user.username}")

    return {"message": f"Account {user.username} unlocked successfully"}
```

#### Step 6: Add Tests

```python
# tests/test_api/test_account_lockout.py
def test_account_lockout_after_failed_attempts(client: TestClient, test_user: User):
    """Test account locks after max failed login attempts."""
    # Attempt to login with wrong password 5 times
    for i in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "WrongPassword"}
        )
        assert response.status_code == 401

    # 6th attempt should indicate account is locked
    response = client.post(
        "/api/v1/auth/login",
        json={"username": test_user.username, "password": "WrongPassword"}
    )
    assert response.status_code == 401
    assert "locked" in response.json()["detail"].lower()

    # Even correct password should not work
    response = client.post(
        "/api/v1/auth/login",
        json={"username": test_user.username, "password": "TestPassword123"}
    )
    assert response.status_code == 401
    assert "locked" in response.json()["detail"].lower()


def test_failed_attempts_reset_on_success(client: TestClient, test_user: User):
    """Test failed attempts counter resets on successful login."""
    # Failed attempts
    for i in range(3):
        client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "WrongPassword"}
        )

    # Successful login
    response = client.post(
        "/api/v1/auth/login",
        json={"username": test_user.username, "password": "TestPassword123"}
    )
    assert response.status_code == 200

    # Counter should be reset - can fail 5 more times
    for i in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": test_user.username, "password": "WrongPassword"}
        )
        if i < 4:
            assert "locked" not in response.json()["detail"].lower()
```

---

## Summary Checklist

After implementing all fixes:

- [ ] Redis connections use settings.REDIS_URL
- [ ] Token blacklist has test coverage
- [ ] Password change tests added
- [ ] Refresh token rotation implemented
- [ ] Account lockout after 5 failed attempts
- [ ] Admin unlock endpoint added
- [ ] All new features have tests (>80% coverage)
- [ ] Database migrations created and tested
- [ ] Environment variables documented
- [ ] Security audit logs updated

## Deployment Steps

1. **Run tests locally:**
   ```bash
   cd quant/backend
   pytest tests/ -v --cov=app --cov-report=html
   ```

2. **Create and test migrations:**
   ```bash
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head
   ```

3. **Update production environment:**
   - Set `REDIS_URL` and `REDIS_ML_URL`
   - Verify Redis connectivity

4. **Deploy with zero downtime:**
   - Deploy new code
   - Run migrations
   - Restart services

5. **Monitor:**
   - Check error logs for Redis connection issues
   - Monitor failed login attempts
   - Verify token rotation working
