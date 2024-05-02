from flask import request
from app.api import app
from app.auth.router import auth_router
from app.utils import set_request_id, validate_client_version
from app.auth.utils import check_authenticated
from sentry_sdk import capture_exception


@app.errorhandler(Exception)
def exception_handler(error):
    """Logs internal server errors."""
    # Internal server errors don't have error code
    error_code = getattr(error, "code", None)
    if error_code:
        return error

    app.server_logger.exception(error)
    capture_exception(error)  # Send internal server errors to Sentry
    return {"error": "Oops! Something went wrong on our end. We're on it!"}, 500


@app.before_request
def pre_request_hook():
    """Hooks to run before each request."""
    set_request_id(request)  # Set request ID
    app.server_logger.info(f"{request.method} {request.path}")  # Log request start

    is_valid = validate_client_version(request)  # Validate client version
    if not is_valid:
        app.client_logger.warning(
            f"Unsupported client version: {request.environ.get('HTTP_X_CLIENT_VERSION')}"
        )
        return {"error": "Unsupported client version."}, 400

    check_authenticated(
        request
    )  # If request is authenticated, set customer ID and is_authenticated flag


@app.after_request
def post_request_hook(response):
    """Hooks to run after each request."""
    app.server_logger.info(f"{request.method} {request.path} {response.status_code}")
    return response


app.register_blueprint(auth_router)
