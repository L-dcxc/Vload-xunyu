"""TCP 传输层实现"""
from __future__ import annotations

import socket

from ..exceptions import ConnectionError, TimeoutError, TransportError
from .base import Transport


class TcpTransport(Transport):
    """TCP Socket 传输实现"""

    def __init__(self, host: str, port: int, timeout_ms: int = 2000):
        self._host = host
        self._port = port
        self._timeout_ms = timeout_ms
        self._socket: socket.socket | None = None

    def open(self) -> None:
        """打开 TCP 连接"""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self._timeout_ms / 1000.0)
            self._socket.connect((self._host, self._port))
        except socket.error as e:
            raise ConnectionError(f"无法连接到 {self._host}:{self._port}: {e}") from e

    def close(self) -> None:
        """关闭 TCP 连接"""
        if self._socket:
            try:
                self._socket.close()
            except socket.error:
                pass
        self._socket = None

    def write_line(self, data: str) -> None:
        """发送一行数据"""
        if not self._socket:
            raise TransportError("TCP 连接未打开")

        try:
            line = data + "\n"
            self._socket.sendall(line.encode("ascii"))
        except socket.error as e:
            raise TransportError(f"TCP 写入失败: {e}") from e

    def read_line(self) -> str:
        """读取一行数据"""
        if not self._socket:
            raise TransportError("TCP 连接未打开")

        try:
            buffer = b""
            while b"\n" not in buffer:
                chunk = self._socket.recv(1024)
                if not chunk:
                    raise TimeoutError("TCP 读取超时或连接断开")
                buffer += chunk

            line = buffer.split(b"\n", 1)[0]
            return line.decode("ascii").strip()
        except socket.timeout as e:
            raise TimeoutError("TCP 读取超时") from e
        except socket.error as e:
            raise TransportError(f"TCP 读取失败: {e}") from e
        except UnicodeDecodeError as e:
            raise TransportError(f"数据解码失败: {e}") from e

    def is_open(self) -> bool:
        """检查 TCP 连接是否打开"""
        return self._socket is not None

    @property
    def timeout_ms(self) -> int:
        return self._timeout_ms

    @timeout_ms.setter
    def timeout_ms(self, value: int) -> None:
        self._timeout_ms = value
        if self._socket:
            self._socket.settimeout(value / 1000.0)
