from celery import Celery
from app.core.config import CONFIG


# Create the Celery application with redis as the broker
app = Celery("tasks", broker=CONFIG.CELERY_BROKER_URL)


@app.task
def send_email(email: str, subject: str, body: str):
    """Send an email to the user"""
    # Implementation of sending an email
    print(f"Email sent to {email} with subject: {subject} and body: {body}")


if __name__ == "__main__":
    app.start()
