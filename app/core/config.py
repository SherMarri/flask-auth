import os
import logging
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()


class Config:
    """Set all the configuration variables here"""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = None
    ALEMBIC = {
        "file_template": " %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s",
    }
    LOG_FILE = "app.log"  # Default log file
    VERIFICATION_CODE_EXPIRATION = 60 * 60  # 1 hour
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_ALGORITHM = "HS256"
    JWT_ERROR_MESSAGE_KEY = "error"
    CLIENT_MAJOR_VERSION, CLIENT_MINOR_VERSION, CLIENT_PATCH_VERSION = 2, 1, 0
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    LOG_LEVEL = logging.WARNING


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_TEST_DATABASE_URI")
    LOG_FILE = "test.log"
    LOG_LEVEL = logging.INFO


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DEV_DATABASE_URI")
    LOG_FILE = "dev.log"
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """Production configuration"""

    LOG_FILE = "prod.log"
    LOG_LEVEL = logging.ERROR
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_PROD_DATABASE_URI")


configs: dict[str, Config] = {
    "testing": TestingConfig,
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

CONFIG = configs[os.getenv("FLASK_ENV", "development")]
