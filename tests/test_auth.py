"""Unit tests for the auth module."""

import unittest
from datetime import datetime, timedelta
from app.server import app
from app.api import db
from app.sql_models import User


class BaseAuthTest(unittest.TestCase):
    """Base test class for the auth module."""

    DUMMY_EMAIL = "dummy@test.com"
    DUMMY_PASSWORD = "password"
    VALID_CLIENT_VERSION = "2.1.0"

    def setUp(self):
        """Set up test environment."""
        app.config.from_object("app.core.config.TestingConfig")
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
            self._create_dummy_user()

    def _create_dummy_user(self):
        """Create a dummy user."""
        user = User(
            email=self.DUMMY_EMAIL, customer_id="123", language="en", country="US"
        )
        user.set_password(self.DUMMY_PASSWORD)
        with app.app_context():
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        """Tear down test environment."""
        with app.app_context():
            db.drop_all()


class TestClientVersion(BaseAuthTest):
    """Test the client version."""

    def test_invalid_client_version(self):
        """Test the client version is invalid."""
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": self.DUMMY_PASSWORD},
            headers={"X-Client-Version": "1.0.0"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Unsupported client version.")

    def test_valid_client_version(self):
        """Test the client version is valid."""
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": self.DUMMY_PASSWORD},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)

    def test_missing_client_version(self):
        """Test the client version is missing."""
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": self.DUMMY_PASSWORD},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "Unsupported client version.")


class TestLogin(BaseAuthTest):
    """Test the login endpoint."""

    def test_login(self):
        """Test the login endpoint."""
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": self.DUMMY_PASSWORD},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json["data"]
        self.assertEqual(data["user"]["email"], self.DUMMY_EMAIL)
        self.assertTrue("jwt" in data)

    def test_invalid_email(self):
        """Test the login endpoint with an invalid email."""
        response = self.app.post(
            "/auth/login",
            json={
                "email": "invalid." + self.DUMMY_EMAIL,
                "password": self.DUMMY_PASSWORD,
            },
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 401)

    def test_invalid_password(self):
        """Test the login endpoint with an invalid password."""
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": "invalid"},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 401)

    def test_missing_email(self):
        """Test the login endpoint with a missing email."""
        response = self.app.post(
            "/auth/login",
            json={"password": self.DUMMY_PASSWORD},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_password(self):
        """Test the login endpoint with a missing password."""
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 400)


class TestForgotPassword(BaseAuthTest):
    """Test the forgot password endpoint."""

    def test_forgot_password(self):
        """Test the forgot password endpoint."""
        response = self.app.post(
            "/auth/forgot_password",
            json={"email": self.DUMMY_EMAIL},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_invalid_email(self):
        """Test the forgot password endpoint with an invalid email."""
        response = self.app.post(
            "/auth/forgot_password",
            json={"email": "invalid." + self.DUMMY_EMAIL},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        # Invalid email should still be a 200 response to prevent email enumeration
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_missing_email(self):
        """Test the forgot password endpoint with a missing email."""
        response = self.app.post(
            "/auth/forgot_password",
            json={},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_password(self):
        """Test the reset password endpoint."""
        # First, send a forgot password request
        response = self.app.post(
            "/auth/forgot_password",
            json={"email": self.DUMMY_EMAIL},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        # Then, reset the password
        with app.app_context():
            user = db.session.query(User).filter_by(email=self.DUMMY_EMAIL).first()
        response = self.app.post(
            "/auth/reset_password",
            json={
                "email": self.DUMMY_EMAIL,
                "password": "new_password",
                "verification_code": user.verification_code,
            },
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)

    def test_reset_password_invalid_code(self):
        """Test the reset password endpoint with an invalid code."""
        # First, send a forgot password request
        response = self.app.post(
            "/auth/forgot_password",
            json={"email": self.DUMMY_EMAIL},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        # Then, reset the password with an invalid code
        response = self.app.post(
            "/auth/reset_password",
            json={
                "email": self.DUMMY_EMAIL,
                "password": "new_password",
                "verification_code": "invalid",
            },
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )

    def test_reset_password_missing_verification_code(self):
        """Test the reset password endpoint with a missing verification code."""
        # First, send a forgot password request
        response = self.app.post(
            "/auth/forgot_password",
            json={"email": self.DUMMY_EMAIL},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        # Then, reset the password with a missing verification code
        response = self.app.post(
            "/auth/reset_password",
            json={"email": self.DUMMY_EMAIL, "password": "new_password"},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_password_expired_verification_code(self):
        """Test the reset password endpoint with an expired verification code."""
        # First, send a forgot password request
        response = self.app.post(
            "/auth/forgot_password",
            json={"email": self.DUMMY_EMAIL},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        # Then, reset the password with an expired verification code
        with app.app_context():
            user = db.session.query(User).filter_by(email=self.DUMMY_EMAIL).first()
            user.verification_code_expiry = datetime.now() - timedelta(minutes=1)
            db.session.commit()
            verification_code = user.verification_code
        response = self.app.post(
            "/auth/reset_password",
            json={
                "email": self.DUMMY_EMAIL,
                "password": "new_password",
                "verification_code": verification_code,
            },
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 400)


class TestGetCurrentUser(BaseAuthTest):
    """Test the get current user endpoint."""

    def test_get_current_user(self):
        """Test the get current user endpoint."""
        # First, log in
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": self.DUMMY_PASSWORD},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        jwt = response.json["data"]["jwt"]
        # Then, get the current user
        response = self.app.get(
            "/auth/user",
            headers={
                "Authorization": f"Bearer {jwt}",
                "X-Client-Version": self.VALID_CLIENT_VERSION,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json["data"]
        self.assertEqual(data["user"]["email"], self.DUMMY_EMAIL)

    def test_get_current_user_invalid_jwt(self):
        """Test the get current user endpoint with an invalid JWT."""
        response = self.app.get(
            "/auth/user",
            headers={
                "Authorization": "Bearer invalid",
                "X-Client-Version": self.VALID_CLIENT_VERSION,
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_get_current_user_missing_jwt(self):
        """Test the get current user endpoint with a missing JWT."""
        response = self.app.get(
            "/auth/user",
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 401)


class TestUpdateUser(BaseAuthTest):
    """Test the update user endpoint."""

    def test_unauthenticated(self):
        """Test the update user endpoint without authentication."""
        response = self.app.patch(
            "/auth/user",
            json={"language": "en"},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 401)

    def test_update_language(self):
        """Test the update user endpoint with a valid language."""
        # First, log in
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": self.DUMMY_PASSWORD},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        jwt = response.json["data"]["jwt"]
        # Then, update the user's language
        language = User.VALID_LANGUAGES[1]
        response = self.app.patch(
            "/auth/user",
            json={"language": language},
            headers={
                "Authorization": f"Bearer {jwt}",
                "X-Client-Version": self.VALID_CLIENT_VERSION,
            },
        )
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            user = db.session.query(User).filter_by(email=self.DUMMY_EMAIL).first()
        self.assertEqual(user.language, language)

    def test_update_invalid_language(self):
        """Test the update user endpoint with an invalid language."""
        # First, log in
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": self.DUMMY_PASSWORD},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        jwt = response.json["data"]["jwt"]
        # Then, update the user's language
        response = self.app.patch(
            "/auth/user",
            json={"language": "invalid"},
            headers={
                "Authorization": f"Bearer {jwt}",
                "X-Client-Version": self.VALID_CLIENT_VERSION,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_other_fields(self):
        """Test updating other fields, these are currently not allowed."""
        # First, log in
        response = self.app.post(
            "/auth/login",
            json={"email": self.DUMMY_EMAIL, "password": self.DUMMY_PASSWORD},
            headers={"X-Client-Version": self.VALID_CLIENT_VERSION},
        )
        self.assertEqual(response.status_code, 200)
        jwt = response.json["data"]["jwt"]
        # Then, update the user's language
        response = self.app.patch(
            "/auth/user",
            json={"country": "US"},
            headers={
                "Authorization": f"Bearer {jwt}",
                "X-Client-Version": self.VALID_CLIENT_VERSION,
            },
        )
        self.assertEqual(response.status_code, 400)
