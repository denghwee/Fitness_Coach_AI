from flask import Request


def get_access_token(request: Request) -> str:
    """
    Lấy access token từ Authorization header.
    Expect format: Authorization: Bearer <token>
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise ValueError("Authorization header missing")

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError("Invalid Authorization header format")

    return parts[1]
from flask_jwt_extended import get_jwt


def get_user_id_from_token():
    claims = get_jwt()
    user_id = claims.get("userId")
    return user_id
