import os

from dotenv import load_dotenv

from CEACStatusBot import (
    EmailNotificationHandle,
    IOSNotificationHandle,
    NotificationManager,
    TelegramNotificationHandle,
)
from CEACStatusBot.utils import log_with_timestamp

# --- Load .env if present, else fallback to system env ---
if os.path.exists(".env"):
    load_dotenv(dotenv_path=".env")  # loads into os.environ
else:
    log_with_timestamp(".env not found, using system environment only")

try:
    LOCATION = os.environ["LOCATION"]
    NUMBER = os.environ["NUMBER"]
    PASSPORT_NUMBER = os.environ["PASSPORT_NUMBER"]
    SURNAME = os.environ["SURNAME"]
    STATUS_API_BASE_URL = os.getenv("STATUS_API_BASE_URL")
    
    if not STATUS_API_BASE_URL:
        log_with_timestamp("WARNING: STATUS_API_BASE_URL not set, status tracking will not work")
    
    notificationManager = NotificationManager(
        LOCATION, 
        NUMBER, 
        PASSPORT_NUMBER, 
        SURNAME,
        status_api_base_url=STATUS_API_BASE_URL
    )
except KeyError as e:
    raise RuntimeError(f"Missing required env var: {e}") from e


# --- Optional: Email notifications ---
FROM = os.getenv("FROM")
TO = os.getenv("TO")
PASSWORD = os.getenv("PASSWORD")
SMTP = os.getenv("SMTP", "")

if FROM and TO and PASSWORD:
    emailNotificationHandle = EmailNotificationHandle(FROM, TO, PASSWORD, SMTP)
    notificationManager.addHandle(emailNotificationHandle)
else:
    log_with_timestamp("Email notification config missing or incomplete")


# --- Optional: Telegram notifications ---
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

if BOT_TOKEN and CHAT_ID:
    tgNotif = TelegramNotificationHandle(BOT_TOKEN, CHAT_ID)
    notificationManager.addHandle(tgNotif)
else:
    log_with_timestamp("Telegram bot notification config missing or incomplete")


# --- Optional: iOS notifications ---
# iOS notification 默认启用，使用内置的默认 URL
# 如果需要自定义 URL，可以设置环境变量 IOS_NOTIFICATION_URL
IOS_NOTIFICATION_URL = os.getenv("IOS_NOTIFICATION_URL")

if IOS_NOTIFICATION_URL:
    iosNotif = IOSNotificationHandle(IOS_NOTIFICATION_URL)
    notificationManager.addHandle(iosNotif)
    log_with_timestamp(f"iOS notification enabled with custom URL: {IOS_NOTIFICATION_URL}")
else:
    # 使用默认 URL
    iosNotif = IOSNotificationHandle()
    notificationManager.addHandle(iosNotif)
    log_with_timestamp("iOS notification enabled with default URL")


# --- Send notifications ---
notificationManager.send()
