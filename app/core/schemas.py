# Base Schemas here
from marshmallow import Schema, fields


class BaseResponse(Schema):
    """To ensure consistency in the response format, all responses should inherit from this class."""

    message = fields.String()
    error = fields.String()
    errors = fields.Dict()  # For field validation errors
