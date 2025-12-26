import requests
from urllib.parse import quote

from CEACStatusBot.utils import log_with_timestamp
from .handle import NotificationHandle


class IOSNotificationHandle(NotificationHandle):
    def __init__(self, base_url: str = None) -> None:
        """
        iOS 通知处理器
        
        Args:
            base_url: 可选的自定义基础 URL，如果不提供则使用默认 URL
        """
        super().__init__()
        self.__base_url = base_url or "http://119.28.41.230:28080/FhKp8p8Ltd3abpX6bBXAHV"

    def send(self, result, change_type="status"):
        """
        发送 iOS 通知
        
        Args:
            result: 查询结果字典
            change_type: 变更类型，"status" 或 "case_updated"
        """
        # 根据变更类型生成简短的标题和内容
        if change_type == "case_updated":
            # 仅 case_last_updated 变更
            title = "美签正在被Review"
            content = f'更新日期: {result.get("case_last_updated", "未知")}'
        else:
            # status 变更
            title = "美签状态更新"
            status = result.get("status", "未知")
            case_last_updated = result.get("case_last_updated", "")
            
            # 构建简短的内容描述
            if status == "Issued":
                content = f"已签发 ({case_last_updated})"
            elif status == "Administrative Processing":
                content = f"行政审查中 ({case_last_updated})"
            elif status == "Refused":
                content = f"被拒签 ({case_last_updated})"
            elif status == "Ready":
                content = f"准备就绪 ({case_last_updated})"
            else:
                content = f"{status} ({case_last_updated})"
        
        # URL 编码标题和内容
        encoded_title = quote(title)
        encoded_content = quote(content)
        
        # 构建完整的请求 URL
        notification_url = f"{self.__base_url}/{encoded_title}/{encoded_content}"
        
        try:
            # 发送 GET 请求
            response = requests.get(notification_url, timeout=10)
            
            # 检查响应
            if response.status_code == 200:
                log_with_timestamp("iOS notification sent successfully")
            else:
                log_with_timestamp(
                    f"Failed to send iOS notification: "
                    f"status_code={response.status_code}, response={response.text}"
                )
        except requests.exceptions.RequestException as e:
            log_with_timestamp(f"Error sending iOS notification: {e}")

