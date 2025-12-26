import os

from dotenv import load_dotenv

from CEACStatusBot import IOSNotificationHandle
from CEACStatusBot.utils import log_with_timestamp

# 测试命令: uv run test_ios_notification.py


def _load_env() -> None:
    if os.path.exists(".env"):
        load_dotenv(dotenv_path=".env")
    else:
        log_with_timestamp(".env not found, using system environment only")


def send_test_ios_notification() -> None:
    _load_env()

    # iOS notification 可以使用自定义 URL，也可以使用默认 URL
    # 如果需要自定义，可以在环境变量中设置 IOS_NOTIFICATION_URL
    base_url = os.getenv("IOS_NOTIFICATION_URL")
    
    if base_url:
        ios_handle = IOSNotificationHandle(base_url)
        log_with_timestamp(f"Using custom iOS notification URL: {base_url}")
    else:
        ios_handle = IOSNotificationHandle()
        log_with_timestamp("Using default iOS notification URL")

    # 测试状态变更通知
    test_result_status = {
        "application_num_origin": "TEST-CASE",
        "status": "Issued",
        "case_last_updated": "26-Dec-2024",
        "description": "This is a test message to verify iOS Notifications are working correctly.",
    }

    log_with_timestamp("Sending test iOS notification (status change)...")
    ios_handle.send(test_result_status, change_type="status")
    log_with_timestamp("Test iOS notification sent (status change).")

    # 测试案件更新日期变更通知
    test_result_case_updated = {
        "application_num_origin": "TEST-CASE",
        "status": "Administrative Processing",
        "case_last_updated": "26-Dec-2024",
        "description": "This is a test message for case updated notification.",
    }

    log_with_timestamp("\nSending test iOS notification (case updated)...")
    ios_handle.send(test_result_case_updated, change_type="case_updated")
    log_with_timestamp("Test iOS notification sent (case updated).")


if __name__ == "__main__":
    send_test_ios_notification()

