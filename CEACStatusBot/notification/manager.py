import os
import datetime

import pytz
import requests

from CEACStatusBot.captcha import CaptchaHandle, OnnxCaptchaHandle
from CEACStatusBot.request import query_status
from CEACStatusBot.utils import log_with_timestamp

from .handle import NotificationHandle

DEFAULT_ACTIVE_HOURS = "00:00-23:59"


class NotificationManager:
    def __init__(
        self,
        location: str,
        number: str,
        passport_number: str,
        surname: str,
        captchaHandle: CaptchaHandle = OnnxCaptchaHandle("captcha.onnx"),
        status_api_base_url: str = None,
    ) -> None:
        self.__handleList = []
        self.__location = location
        self.__number = number
        self.__captchaHandle = captchaHandle
        self.__passport_number = passport_number
        self.__surname = surname
        self.__status_api_base_url = status_api_base_url or os.getenv("STATUS_API_BASE_URL", "")

    def _get_hour_range(self) -> list:
        active_hours = os.getenv("ACTIVE_HOURS")
        if active_hours is None:
            active_hours = DEFAULT_ACTIVE_HOURS
        start_str, end_str = active_hours.split("-")
        
        # 处理 24:00 的特殊情况，将其转换为 23:59:59
        if end_str == "24:00":
            end_str = "23:59"
        
        start = datetime.datetime.strptime(start_str, "%H:%M").time()
        end = datetime.datetime.strptime(end_str, "%H:%M").time()
        if start > end:
            raise ValueError("Start time must be before end time, got start: {start}, end: {end}")
        return start, end

    def addHandle(self, notificationHandle: NotificationHandle) -> None:
        self.__handleList.append(notificationHandle)

    def send(self) -> None:
        res = query_status(
            self.__location,
            self.__number,
            self.__passport_number,
            self.__surname,
            self.__captchaHandle,
        )
        
        # 检查查询是否成功
        if not res.get("success", False):
            log_with_timestamp(f"查询失败详情: {res}")
            log_with_timestamp("无法获取签证状态，可能是验证码识别失败或网络问题")
            return
        
        current_status = res["status"]
        current_last_updated = res["case_last_updated"]
        log_with_timestamp(f"Current status: {current_status} - Last updated: {current_last_updated}")
        
        # Get the previous status from API
        last_status_record = self.__get_last_status()

        # Determine what changed
        status_changed = False
        case_updated_changed = False
        
        if not last_status_record:
            # First run, record as status change
            status_changed = True
        else:
            if current_status != last_status_record["status"]:
                status_changed = True
            if current_last_updated != last_status_record.get("case_last_updated", ""):
                case_updated_changed = True
        
        # Determine notification behavior
        if status_changed:
            # Status changed (with or without case_last_updated change)
            # Treat as status change
            self.__save_current_status(current_status, current_last_updated)
            self.__send_notifications(res, change_type="status")
            log_with_timestamp(f"Result: status changed to: {current_status}")
        elif case_updated_changed:
            # Only case_last_updated changed
            self.__save_current_status(current_status, current_last_updated)
            self.__send_notifications(res, change_type="case_updated")
            log_with_timestamp(f"Result: case last updated changed to: {current_last_updated}")
        else:
            log_with_timestamp("Result: no changes detected, no notification sent.")

    def __get_last_status(self) -> dict:
        """从 API 获取上一次的状态"""
        if not self.__status_api_base_url:
            log_with_timestamp("STATUS_API_BASE_URL not set, cannot get last status")
            return None
        
        try:
            response = requests.get(f"{self.__status_api_base_url}/status", timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("data")
            else:
                log_with_timestamp(f"Failed to get status from API: {result.get('error', 'Unknown error')}")
                return None
        except Exception as e:
            log_with_timestamp(f"Error getting status from API: {e}")
            return None

    def __save_current_status(self, status: str, case_last_updated: str) -> None:
        """保存当前状态到 API"""
        if not self.__status_api_base_url:
            log_with_timestamp("STATUS_API_BASE_URL not set, cannot save status")
            return
        
        try:
            payload = {
                "status": status,
                "case_last_updated": case_last_updated
            }
            response = requests.post(
                f"{self.__status_api_base_url}/status",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                log_with_timestamp(f"Failed to save status to API: {result.get('error', 'Unknown error')}")
        except Exception as e:
            log_with_timestamp(f"Error saving status to API: {e}")

    def __send_notifications(self, res: dict, change_type: str = "status") -> None:
        if res["status"] == "Refused":
            try:
                TIMEZONE = os.environ["TIMEZONE"]
                localTimeZone = pytz.timezone(TIMEZONE)
                localTime = datetime.datetime.now(localTimeZone)
            except pytz.exceptions.UnknownTimeZoneError:
                log_with_timestamp("UNKNOWN TIMEZONE Error, use default")
                localTime = datetime.datetime.now()
            except KeyError:
                log_with_timestamp("TIMEZONE Error")
                localTime = datetime.datetime.now()

            active_hour_start, active_hour_end = self._get_hour_range()
            start_dt = datetime.datetime.combine(localTime.date(), active_hour_start, tzinfo=localTimeZone)
            end_dt = datetime.datetime.combine(localTime.date(), active_hour_end, tzinfo=localTimeZone)
            if not (start_dt <= localTime <= end_dt):
                log_with_timestamp(
                    f"Outside active hours {os.getenv('ACTIVE_HOURS', DEFAULT_ACTIVE_HOURS)}. "
                    "No notification sent for Refused status."
                )
                return

        for notificationHandle in self.__handleList:
            notificationHandle.send(res, change_type=change_type)
