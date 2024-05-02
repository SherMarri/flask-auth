import json
from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from app.api import app, db
from app.sql_models import User
from app.auth.exceptions import InvalidCredentials
from app.core.exceptions import RecordNotFound
from app.core.config import CONFIG

from tasks import send_email


class AuthService:

    def authenticate(self, email: str, password: str) -> User:
        """Authenticate a user by email and password"""
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            raise InvalidCredentials
        if not user.check_password(password):
            raise InvalidCredentials
        return user

    def generate_token(self, user: User) -> str:
        """Generate a JWT token for a user"""
        token = create_access_token(identity=user.customer_id)
        return token

    def get_user(self, customer_id: str) -> Optional[User]:
        """Get a user by customer_id if it exists"""
        user = db.session.query(User).filter_by(customer_id=customer_id).first()
        return user

    def reset_password(self, email: str) -> bool:
        """Initiates reset password process and sends email with verification code"""
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            return False
        verification_code = str(uuid4())
        app.server_logger.info(f"Verification code for {email}: {verification_code}")
        user.verification_code = verification_code
        user.verification_code_expiry = datetime.now() + timedelta(
            minutes=CONFIG.VERIFICATION_CODE_EXPIRATION
        )
        db.session.commit()
        send_email.delay(
            email,
            "Password Reset",
            f"Use this verification code to reset your password: {verification_code}",
        )
        return True

    def reset_password_confirm(
        self, email: str, password: str, verification_code: str
    ) -> bool:
        """Confirm a user's password reset"""
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            return False
        if (
            user.verification_code != verification_code
            or user.verification_code_expiry < datetime.now()
        ):
            return False
        user.set_password(password)
        user.verification_code = None
        user.verification_code_expiry = None
        db.session.commit()
        return True

    def create_users(self, file: str) -> None:
        """Create new users from JSONL file. Only called by the CLI."""
        with app.app_context():
            try:
                with open(file, "r") as f:
                    users = [json.loads(line) for line in f]
                    for user in users:
                        if (
                            "language" not in user
                            or user["language"] not in User.VALID_LANGUAGES
                        ):
                            user["language"] = "en"
                        new_user = User(**user)
                        db.session.add(new_user)
                    db.session.commit()
                print("Users created successfully.")
            except Exception as e:
                print(f"Error creating users: {e}")

    def update_user(self, customer_id: str, update: dict) -> User:
        """Update user record with new data"""
        user = db.session.query(User).filter_by(customer_id=customer_id).first()
        if not user:
            raise RecordNotFound
        for key, value in update.items():
            setattr(user, key, value)
        db.session.commit()
        return user


auth_service = AuthService()
