# flask-auth
Flask-based API demonstrating auth functions


## Quickstart
- Rename `.env.example` to `.env`
- Run db migrations: `docker compose up flask-migrations`
- Run: `docker compose up flask-app`

## Ingest Sample Data
- Copy `customer_export.json` to project root directory.
- Run the following commands:
    - `docker compose up flask-app`
    - `docker compose exec -it flask-app bash`
    - `python cli.py create-users customer_export.json`

## Unit Tests
- Run: `docker compose up tests`


## Docker Services
- **flask-app**: Servers the main application.
- **flask-migrations**: Applying db migrations, exits after execution.
- **tests**: Runs unit tests, exists after execution.
- **postgres**: Database for `users` and other models.
- **celery**: Handles async tasks, like emailing verification codes for password reset.
- **redis**: Message broker for `celery`.



## API Guide
### Endpoints
**Login**:
 * Route: POST `http://localhost:5000/auth/login/`
 * Description: Login with email and password
 * Content type: JSON
 * Headers:
    ```
    X-Client-Version: 2.1.0 (Minimum)
    ```
 * Example request body:
    ```
    {
        "email": "dummy@example.com",
        "password": "dummy"
    }
    ```
 * Example response:
    ```
    {
        "data": {
            "jwt": "ey...",
            "user": {
                "country": "FR",
                "customer_id": "8b4a1343-292d-45ed-ba5f-846fa9167ede",
                "email": "njmekwhvmncrzuhwja@protonmail.com",
                "language": "en"
            }
        }
    }
    ```
**Get Current User**
 * Route: GET `http://localhost:5000/auth/`
 * Description: Get currently logged in user.
 * Headers:
    ```
    X-Client-Version: 2.1.0 (Minimum)
    ```
 * Example response:
    ```
    {
        "data": {
            "user": {
                "country": "FR",
                "customer_id": "8b4a1343-292d-45ed-ba5f-846fa9167ede",
                "email": "njmekwhvmncrzuhwja@protonmail.com",
                "language": "en"
            }
        }
    }
    ```
**Initiate Forgot Password**:
 * Route: POST `http://localhost:5000/auth/forgot_password/`
 * Description: Request a password reset.
 * Content type: JSON
 * Headers:
    ```
    X-Client-Version: 2.1.0 (Minimum)
    ```
 * Example request body:
    ```
    {
        "email": "dummy@example.com",
    }
    ```
 * Example response:
    ```
    {
        "message": "If you have an account, you will receive an email with instructions to reset your password."
    }
    ```

**Reset Password**:
 * Route: POST `http://localhost:5000/auth/reset_password/`
 * Description: Reset password.
 * Content type: JSON
 * Headers:
    ```
    X-Client-Version: 2.1.0 (Minimum)
    ```
 * Example request body:
    ```
    {
        "email": "dummy@example.com",
        "password": "new_password",
        "verification_code": "4eba97c4-982a-4df2-bba1-92a35f25f091"
    }
    ```
 * Example response:
    ```
    {
        "message": "Password reset."
    }
    ```


## Logs
**Destinations**:
- Dev: `dev.log`
- Prod: `prod.log`
- Testing: `test.log`

**Log Format**:
- Format: `[%(asctime)s][%(remote_addr)s][%(request_id)s][%(customer_id)s][%(path)s][%(filename)s][%(lineno)d][%(levelname)s][%(log_type)s]: %(message)s`
- Examples:
    ```
    [2024-05-02 22:53:59,923][127.0.0.1][05f8154f-b0fb-4f9d-93d9-79f290955658][None][/auth/forgot_password][logger.py][58][WARNING][client]: {'email': ['Missing data for required field.']}
    ```
    ```
    [2024-05-02 22:54:01,404][127.0.0.1][51304047-a5c6-4dd1-800f-19e38bad56b1][123][/auth/][logger.py][49][INFO][server]: GET /auth/ 200
    ```
- `log_type` parameter is used to differentiate between `client` and `server` logs..
- `client` related errors are logged as `WARNING`.
- `server` related errors can be logged at any level.