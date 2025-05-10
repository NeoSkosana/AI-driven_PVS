"""Tests for authentication service."""
import pytest
from datetime import timedelta
from jose import jwt
import os
from src.auth.auth_service import (
    Token,
    TokenData,
    User,
    UserInDB,
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
)

@pytest.fixture
def test_user():
    """Create a test user."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpass123",
    }

@pytest.fixture
def test_user_db(test_user):
    """Create a test user with hashed password."""
    hashed_password = get_password_hash(test_user["password"])
    return UserInDB(
        username=test_user["username"],
        email=test_user["email"],
        full_name=test_user["full_name"],
        hashed_password=hashed_password,
        disabled=False
    )

def test_verify_password():
    """Test password verification."""
    password = "testpass123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrongpass", hashed)

def test_create_access_token(test_user):
    """Test access token creation."""
    data = {"sub": test_user["username"]}
    expires_delta = timedelta(minutes=30)
    
    token = create_access_token(data, expires_delta)
    assert isinstance(token, str)
    
    # Verify token can be decoded
    payload = jwt.decode(
        token,
        os.getenv("JWT_SECRET_KEY", "test_secret"),
        algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
    )
    assert payload["sub"] == test_user["username"]

def test_decode_token(test_user):
    """Test token decoding."""
    token = create_access_token({"sub": test_user["username"]})
    token_data = decode_token(token)
    
    assert isinstance(token_data, TokenData)
    assert token_data.username == test_user["username"]

def test_decode_invalid_token():
    """Test decoding an invalid token."""
    with pytest.raises(ValueError, match="Invalid token"):
        decode_token("invalid_token")

def test_decode_expired_token(test_user):
    """Test decoding an expired token."""
    token = create_access_token(
        {"sub": test_user["username"]},
        expires_delta=timedelta(microseconds=1)
    )
    
    # Wait for token to expire
    import time
    time.sleep(0.1)
    
    with pytest.raises(ValueError, match="Invalid token"):
        decode_token(token)
