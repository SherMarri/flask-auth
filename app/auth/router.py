from flask import Blueprint, request
from marshmallow import ValidationError
from app.auth import schemas
from app.auth.auth_service import auth_service
from app.auth.exceptions import InvalidCredentials
from app.core.exceptions import RecordNotFound
from app.auth.utils import authenticate
from app.api import app


auth_router = Blueprint("auth", __name__, url_prefix="/auth")


@auth_router.route("/login", methods=["POST"])
def login():
    try:
        login_request = schemas.LoginRequest().load(request.json)
        user = auth_service.authenticate(
            login_request["email"], login_request["password"]
        )
        jwt = auth_service.generate_token(user)
        return schemas.UserResponse().dump({"data": {"user": user, "jwt": jwt}})
    except ValidationError as e:
        app.client_logger.warning(e.messages)
        return schemas.UserResponse().dump({"errors": e.messages}), 400
    except InvalidCredentials:
        app.client_logger.warning("Invalid email or password")
        return schemas.UserResponse().dump({"error": "Invalid email or password."}), 401


@auth_router.route("/forgot_password", methods=["POST"])
def forgot_password():
    try:
        forgot_password_request = schemas.ForgotPasswordRequest().load(request.json)
        auth_service.reset_password(forgot_password_request["email"])
        return schemas.BaseResponse().dump(
            {
                "message": "If you have an account, you will receive an email with instructions to reset your password."
            }
        )
    except ValidationError as e:
        app.client_logger.warning(e.messages)
        return schemas.BaseResponse().dump({"errors": e.messages}), 400


# Reset password POST request with email, password, and verification_code as JSON body in ResetPasswordRequest schema
@auth_router.route("/reset_password", methods=["POST"])
def reset_password():
    try:
        reset_password_request = schemas.ResetPasswordRequest().load(request.json)
        done = auth_service.reset_password_confirm(
            reset_password_request["email"],
            reset_password_request["password"],
            reset_password_request["verification_code"],
        )
        if not done:
            return (
                schemas.BaseResponse().dump(
                    {"error": "Invalid email, password, or verification code."}
                ),
                400,
            )
        return schemas.BaseResponse().dump({"message": "Password reset."})
    except ValidationError as e:
        app.client_logger.warning(e.messages)
        return schemas.BaseResponse().dump({"errors": e.messages}), 400


# Get current user GET request with JWT token in Authorization header
@auth_router.route("/", methods=["GET"])
@authenticate()
def get_current_user():
    try:
        customer_id = request.environ.get("customer_id")
        user = auth_service.get_user(customer_id)
        return schemas.UserResponse().dump({"data": {"user": user}})
    except RecordNotFound:
        app.client_logger.warning("User not found")
        return schemas.UserResponse().dump({"error": "User not found."}), 404


@auth_router.route("/", methods=["PATCH"])
@authenticate()
def update_user():
    try:
        update = schemas.UpdateUserRequest().load(request.json)
        customer_id = request.environ.get("customer_id")
        user = auth_service.update_user(customer_id, update)
        return schemas.UserResponse().dump({"data": {"user": user}})
    except ValidationError as e:
        app.client_logger.warning(e.messages)
        return schemas.UserResponse().dump({"errors": e.messages}), 400
    except RecordNotFound:
        app.client_logger.warning("User not found")
        return schemas.UserResponse().dump({"error": "User not found."}), 404
