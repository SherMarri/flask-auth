"""Logger module for the application."""

from enum import Enum
from flask import has_request_context, request
import logging
from app.core.config import CONFIG


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.path = request.path
            record.remote_addr = request.remote_addr
            record.request_id = request.environ.get("request_id")
            record.customer_id = request.environ.get("customer_id")
        else:
            record.path = None
            record.remote_addr = None
            record.request_id = None
            record.customer_id = None

        if not hasattr(record, "log_type"):
            record.log_type = ""

        return super().format(record)


formatter = RequestFormatter(
    "[%(asctime)s][%(remote_addr)s][%(request_id)s][%(customer_id)s][%(path)s][%(filename)s][%(lineno)d][%(levelname)s][%(log_type)s]: %(message)s"
)


log_file = CONFIG.LOG_FILE
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)


class Logger:

    class LoggerType(Enum):
        CLIENT = "client"
        SERVER = "server"

    def __init__(self, logger: logging.Logger, log_type: LoggerType):
        self.logger = logger
        self.log_type = log_type.value

    def info(self, message: str):
        self.logger.info(message, extra={"log_type": self.log_type})

    def error(self, message: any):
        self.logger.error(message, extra={"log_type": self.log_type})

    def exception(self, exception: any):
        self.logger.exception(exception, extra={"log_type": self.log_type})

    def warning(self, message: str):
        self.logger.warning(message, extra={"log_type": self.log_type})

    def debug(self, message: str):
        self.logger.debug(message, extra={"log_type": self.log_type})

    def critical(self, message: str):
        self.logger.critical(message, extra={"log_type": self.log_type})

    def log(self, level: int, message: any):
        self.logger.log(level, message, extra={"log_type": self.log_type})
