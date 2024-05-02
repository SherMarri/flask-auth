from marshmallow import Schema, fields
from app.core.schemas import BaseResponse
from app.sql_models import User
from app.api import ma


class ForgotPasswordRequest(Schema):
    email = fields.Email(required=True)


class ResetPasswordRequest(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    verification_code = fields.String(required=True)


class LoginRequest(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        fields = ("customer_id", "email", "country", "language")


class UserResponseSchema(Schema):
    user = fields.Nested(UserSchema)
    jwt = fields.String()


class UserResponse(BaseResponse):
    data = fields.Nested(UserResponseSchema)


class UpdateUserRequest(Schema):
    language = fields.String(
        required=True,
        validate=lambda x: x in User.VALID_LANGUAGES,
        error_messages={
            "validator_failed": f"Invalid language. Valid languages: {User.VALID_LANGUAGES}"
        },
    )
