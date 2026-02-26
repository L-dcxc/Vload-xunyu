"""SCPI 协议客户端"""
from __future__ import annotations

import threading
from typing import Callable

from ..exceptions import SCPIError
from ..transport import Transport


class SCPIClient:
    """SCPI 协议客户端，负责命令发送/查询和日志记录"""

    def __init__(self, transport: Transport):
        self._transport = transport
        self._lock = threading.Lock()
        self._log_callback: Callable[[str, str], None] | None = None

    def set_log_callback(self, callback: Callable[[str, str], None]) -> None:
        """设置日志回调函数，参数为 (direction, message)，direction 为 'TX' 或 'RX'"""
        self._log_callback = callback

    def send(self, command: str) -> None:
        """发送命令（无返回值）"""
        with self._lock:
            if not self._transport.is_open():
                raise SCPIError("设备未连接")

            try:
                if self._log_callback:
                    self._log_callback("TX", command)
                self._transport.write_line(command)
            except Exception as e:
                if self._log_callback:
                    self._log_callback("ERR", f"发送失败: {e}")
                raise SCPIError(f"发送命令失败: {e}") from e

    def query(self, command: str) -> str:
        """查询命令（有返回值）"""
        with self._lock:
            if not self._transport.is_open():
                raise SCPIError("设备未连接")

            try:
                if self._log_callback:
                    self._log_callback("TX", command)
                self._transport.write_line(command)

                response = self._transport.read_line()
                if self._log_callback:
                    self._log_callback("RX", response)
                return response
            except Exception as e:
                if self._log_callback:
                    self._log_callback("ERR", f"查询失败: {e}")
                raise SCPIError(f"查询命令失败: {e}") from e

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._transport.is_open()
