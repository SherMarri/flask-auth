from uuid import uuid4

from app.core.config import CONFIG


def set_request_id(request):
    """Assign a unique request ID to each request."""
    request.environ["request_id"] = str(uuid4())


def validate_client_version(request):
    """Checks if the client version is valid. A client version should be in the format x.y.z"""
    client_version = request.environ.get("HTTP_X_CLIENT_VERSION", "0.0.0")
    tokens = client_version.split(".")
    if len(tokens) != 3:
        return False

    # Check if all tokens are integers
    if not all(token.isdigit() for token in tokens):
        return False

    # Check if the client version is greater than or equal to the minimum client version
    major, minor, patch = map(int, tokens)
    if major < CONFIG.CLIENT_MAJOR_VERSION:
        return False
    elif major == CONFIG.CLIENT_MAJOR_VERSION:
        if minor < CONFIG.CLIENT_MINOR_VERSION:
            return False
        elif minor == CONFIG.CLIENT_MINOR_VERSION:
            if patch < CONFIG.CLIENT_PATCH_VERSION:
                return False
    return True
