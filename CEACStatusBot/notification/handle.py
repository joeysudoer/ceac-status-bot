from abc import ABC, abstractmethod

class NotificationHandle(ABC):
    def __init__(self) -> None:
        super().__init__() 

    @abstractmethod
    def send(self, result, change_type="status"):
        """
        发送通知
        
        Args:
            result: 查询结果字典
            change_type: 变更类型，可选值: "status" (状态变更) 或 "case_updated" (案件更新日期变更)
        """
        pass