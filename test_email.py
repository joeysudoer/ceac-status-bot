import os

from dotenv import load_dotenv

from CEACStatusBot import EmailNotificationHandle
from CEACStatusBot.utils import log_with_timestamp

# 测试命令: uv run test_email.py

def _load_env() -> None:
    if os.path.exists(".env"):
        load_dotenv(dotenv_path=".env")
    else:
        log_with_timestamp(".env not found, using system environment only")


def send_test_email() -> None:
    _load_env()

    from_email = os.getenv("FROM")
    to_email = os.getenv("TO")
    password = os.getenv("PASSWORD")
    smtp = os.getenv("SMTP", "")

    if not from_email or not to_email or not password:
        msg = "Email notification config missing or incomplete, please set FROM, TO and PASSWORD in environment/.env"
        raise RuntimeError(msg)

    email_handle = EmailNotificationHandle(from_email, to_email, password, smtp)

    test_result = {
        "application_num_origin": "TEST-CASE",
        "status": "Test",
        "description": "This is a test email to verify Email Notifications are working correctly.",
    }

    log_with_timestamp("Sending test email...")
    email_handle.send(test_result)
    log_with_timestamp("Test email sent, please check your inbox.")


if __name__ == "__main__":
    send_test_email()


