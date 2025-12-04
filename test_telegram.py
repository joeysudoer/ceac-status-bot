import os

from dotenv import load_dotenv

from CEACStatusBot import TelegramNotificationHandle
from CEACStatusBot.utils import log_with_timestamp

# 测试命令: uv run test_telegram.py

def _load_env() -> None:
    if os.path.exists(".env"):
        load_dotenv(dotenv_path=".env")
    else:
        log_with_timestamp(".env not found, using system environment only")


def send_test_telegram() -> None:
    _load_env()

    bot_token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")

    if not bot_token or not chat_id:
        msg = (
            "Telegram notification config missing or incomplete, "
            "please set TG_BOT_TOKEN and TG_CHAT_ID in environment/.env"
        )
        raise RuntimeError(msg)

    tg_handle = TelegramNotificationHandle(bot_token, chat_id)

    test_result = {
        "application_num_origin": "TEST-CASE",
        "status": "Test",
        "description": "This is a test message to verify Telegram Notifications are working correctly.",
    }

    log_with_timestamp("Sending test telegram message...")
    tg_handle.send(test_result)
    log_with_timestamp("Test telegram message sent, please check your Telegram chat.")


if __name__ == "__main__":
    send_test_telegram()
