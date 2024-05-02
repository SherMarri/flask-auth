import jwt
from functools import wraps
from app.api import app
from app.core.config import CONFIG
from flask import request


def check_authenticated(request) -> bool:
    """Checks if request is authenticated, if yes, set the customer ID for the request."""
    token = request.environ.get("HTTP_AUTHORIZATION", "").split("Bearer ")[-1]
    if not token:
        return None
    try:
        token = jwt.decode(
            token,
            CONFIG.JWT_SECRET_KEY,
            algorithms=[CONFIG.JWT_ALGORITHM],
            verify=True,
        )
        customer_id = token.get("sub")
        request.environ["customer_id"] = customer_id
        request.environ["is_authenticated"] = True
        return True
    except Exception as e:
        return False


def authenticate():
    """Decorator to check if request is authenticated."""

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if request.environ.get("is_authenticated"):
                return fn(*args, **kwargs)

            app.client_logger.warning("Unauthorized request.")
            return {"error": "Unauthorized."}, 401

        return decorator

    return wrapper
