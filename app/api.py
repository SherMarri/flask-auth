from flask import Flask
from flask_marshmallow import Marshmallow
from flask_alembic import Alembic
from flask_jwt_extended import JWTManager
import sentry_sdk

from app.core.logger import file_handler, Logger
from app.core.config import CONFIG
from app.sql_models import db


sentry_sdk.init(CONFIG.SENTRY_DSN)


app = Flask(__name__)
app.config.from_object(CONFIG)

app.logger.addHandler(file_handler)
app.logger.setLevel(CONFIG.LOG_LEVEL)
app.client_logger = Logger(app.logger, Logger.LoggerType.CLIENT)
app.server_logger = Logger(app.logger, Logger.LoggerType.SERVER)

db.init_app(app)
ma = Marshmallow(app)
alembic = Alembic(app)
jwt = JWTManager(app)
jwt.invalid_token_loader(lambda x: ({"error": "Invalid token."}, 401))
