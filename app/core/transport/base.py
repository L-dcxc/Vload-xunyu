"""传输层基类"""
from abc import ABC, abstractmethod


class Transport(ABC):
    """传输层抽象基类"""

    @abstractmethod
    def open(self) -> None:
        """打开连接"""
        pass

    @abstractmethod
    def close(self) -> None:
        """关闭连接"""
        pass

    @abstractmethod
    def write_line(self, data: str) -> None:
        """发送一行数据（自动添加换行符）"""
        pass

    @abstractmethod
    def read_line(self) -> str:
        """读取一行数据（读到换行符或超时）"""
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """检查连接是否打开"""
        pass

    @property
    @abstractmethod
    def timeout_ms(self) -> int:
        """获取超时时间（毫秒）"""
        pass

    @timeout_ms.setter
    @abstractmethod
    def timeout_ms(self, value: int) -> None:
        """设置超时时间（毫秒）"""
        pass
