"""Tests for authentication and security."""
import pytest
from app.core.security import verify_password, get_password_hash, create_access_token
from app.config import settings


def test_password_hashing():
    """Password hashing is one-way."""
    password = "test-password-123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_password_verification_failure():
    """Wrong password fails verification."""
    password = "test-password-123"
    wrong_password = "wrong-password"
    hashed = get_password_hash(password)
    assert not verify_password(wrong_password, hashed)


def test_token_creation():
    """JWT token creation works."""
    data = {"sub": "user-id-123", "email": "test@example.com"}
    access_token = create_access_token(data)
    assert isinstance(access_token, str)
    assert len(access_token) > 0