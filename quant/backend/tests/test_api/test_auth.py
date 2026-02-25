"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.models.user import User


def test_register_user(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


def test_register_duplicate_username(client: TestClient, test_user: User):
    """Test registration with duplicate username."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "another@example.com",
            "username": test_user.username,
            "password": "Password123",
        },
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_register_weak_password(client: TestClient):
    """Test registration with weak password."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "weak",
        },
    )

    assert response.status_code == 422  # Validation error


def test_login_success(client: TestClient, test_user: User):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_email(client: TestClient, test_user: User):
    """Test login using email instead of username."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.email,  # Using email as username
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client: TestClient, test_user: User):
    """Test login with incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "Password123",
        },
    )

    assert response.status_code == 401


def test_get_current_user(client: TestClient, auth_headers: dict):
    """Test getting current user information."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "hashed_password" not in data


def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 403  # Forbidden (no token provided)


def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


def test_refresh_token(client: TestClient, test_user: User):
    """Test token refresh."""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "TestPassword123",
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    # Use refresh token to get new tokens
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token_invalid(client: TestClient):
    """Test token refresh with invalid token."""
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
    )

    assert response.status_code == 401


def test_logout(client: TestClient, auth_headers: dict):
    """Test logout."""
    response = client.post("/api/v1/auth/logout", headers=auth_headers)

    assert response.status_code == 204
