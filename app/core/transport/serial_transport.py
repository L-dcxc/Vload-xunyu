"""串口传输层实现"""
from __future__ import annotations

import serial

from ..exceptions import ConnectionError, TimeoutError, TransportError
from .base import Transport


class SerialTransport(Transport):
    """串口传输实现"""

    def __init__(self, port: str, baudrate: int = 115200, timeout_ms: int = 2000):
        self._port = port
        self._baudrate = baudrate
        self._timeout_ms = timeout_ms
        self._serial: serial.Serial | None = None

    def open(self) -> None:
        """打开串口连接"""
        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self._timeout_ms / 1000.0,
            )
        except serial.SerialException as e:
            raise ConnectionError(f"无法打开串口 {self._port}: {e}") from e

    def close(self) -> None:
        """关闭串口连接"""
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None

    def write_line(self, data: str) -> None:
        """发送一行数据"""
        if not self._serial or not self._serial.is_open:
            raise TransportError("串口未打开")

        try:
            line = data + "\n"
            self._serial.write(line.encode("ascii"))
            self._serial.flush()
        except serial.SerialException as e:
            raise TransportError(f"串口写入失败: {e}") from e

    def read_line(self) -> str:
        """读取一行数据"""
        if not self._serial or not self._serial.is_open:
            raise TransportError("串口未打开")

        try:
            line = self._serial.read_until(b"\n")
            if not line:
                raise TimeoutError("串口读取超时")
            return line.decode("ascii").strip()
        except serial.SerialException as e:
            raise TransportError(f"串口读取失败: {e}") from e
        except UnicodeDecodeError as e:
            raise TransportError(f"数据解码失败: {e}") from e

    def is_open(self) -> bool:
        """检查串口是否打开"""
        return self._serial is not None and self._serial.is_open

    @property
    def timeout_ms(self) -> int:
        return self._timeout_ms

    @timeout_ms.setter
    def timeout_ms(self, value: int) -> None:
        self._timeout_ms = value
        if self._serial:
            self._serial.timeout = value / 1000.0
