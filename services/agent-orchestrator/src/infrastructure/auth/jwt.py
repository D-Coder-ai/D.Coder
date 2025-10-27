"""
JWT token validation and decoding
"""

from typing import Any

from jose import JWTError, jwt

from src.infrastructure.config.settings import settings


def decode_jwt(token: str) -> dict[str, Any] | None:
    """
    Decode JWT token without validation (for R1 warn-only mode)

    Args:
        token: JWT token string

    Returns:
        Decoded token claims or None if invalid
    """
    try:
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_signature": False}
        )
        return decoded
    except JWTError:
        return None


def validate_token(token: str) -> tuple[bool, dict[str, Any] | None, str | None]:
    """
    Validate JWT token (R1: warn-only, doesn't block)

    Args:
        token: JWT token string

    Returns:
        Tuple of (is_valid, claims, error_message)
    """
    try:
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        return True, decoded, None

    except jwt.ExpiredSignatureError:
        decoded = decode_jwt(token)
        return False, decoded, "Token expired"

    except JWTError as e:
        return False, None, f"Invalid token: {str(e)}"
