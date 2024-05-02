import bcrypt
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates


meta = MetaData(
    # For naming constraints, used by alembic
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
Base = declarative_base(metadata=meta)


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    __tablename__ = "users"

    VALID_LANGUAGES = ["en", "de"]

    customer_id = db.Column(db.String, primary_key=True, index=True)
    email = db.Column(db.String, unique=True, index=True, nullable=False)
    hashed_password = db.Column(db.String)
    salt = db.Column(db.String)
    is_active = db.Column(db.Boolean, default=True)
    country = db.Column(db.String(2), nullable=False)
    language = db.Column(
        db.String(2), nullable=False, default="en", server_default="en"
    )
    verification_code = db.Column(db.String)
    verification_code_expiry = db.Column(db.DateTime)

    def check_password(self, password: str) -> bool:
        """Check if the given password matches the stored password."""
        hash_password = bcrypt.hashpw(
            password.encode("utf-8"), self.salt.encode("utf-8")
        ).decode("utf-8")
        return hash_password == self.hashed_password

    @validates("language")
    def validate_language(self, key, value):
        if value not in self.VALID_LANGUAGES:
            raise ValueError("Invalid language")
        return value

    def set_password(self, password: str) -> None:
        """Set the user's hashed password and salt. Does not commit to the database."""
        self.salt = bcrypt.gensalt().decode("utf-8")
        self.hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), self.salt.encode("utf-8")
        ).decode("utf-8")
