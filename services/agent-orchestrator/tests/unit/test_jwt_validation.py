"""
Unit tests for JWT validation
"""

from datetime import datetime, timedelta

from jose import jwt

from src.infrastructure.auth.jwt import decode_jwt, validate_token
from src.infrastructure.config.settings import settings


def create_test_token(expired=False):
    """Create a test JWT token"""
    exp = datetime.utcnow() - timedelta(hours=1) if expired else datetime.utcnow() + timedelta(hours=1)

    payload = {
        "sub": "user123",
        "exp": exp,
        "iat": datetime.utcnow()
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def test_decode_jwt_valid():
    """Test decoding valid JWT"""
    token = create_test_token()
    decoded = decode_jwt(token)

    assert decoded is not None
    assert decoded["sub"] == "user123"


def test_decode_jwt_expired():
    """Test decoding expired JWT (should still decode without validation)"""
    token = create_test_token(expired=True)
    decoded = decode_jwt(token)

    assert decoded is not None


def test_validate_token_valid():
    """Test validating valid token"""
    token = create_test_token()
    is_valid, claims, error = validate_token(token)

    assert is_valid is True
    assert claims is not None
    assert error is None


def test_validate_token_expired():
    """Test validating expired token"""
    token = create_test_token(expired=True)
    is_valid, claims, error = validate_token(token)

    assert is_valid is False
    assert error == "Token expired"
