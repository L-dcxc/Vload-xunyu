"""设备管理器，协调 UI 和设备通信"""
from __future__ import annotations

from dataclasses import dataclass
from queue import Queue
from typing import Any, Callable
from uuid import uuid4

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from .device import ElectronicLoad
from .exceptions import ConnectionError, SCPIError, TransportError
from .scpi import SCPIClient
from .transport import SerialTransport, TcpTransport, Transport


class MeasurementWorker(QThread):
    """测量轮询工作线程"""

    measurement_ready = pyqtSignal(float, float, float, float)  # v, i, p, r
    error_occurred = pyqtSignal(str)

    def __init__(self, device: ElectronicLoad, interval_ms: int = 200):
        super().__init__()
        self._device = device
        self._interval_ms = interval_ms
        self._running = False

    def run(self) -> None:
        """线程主循环"""
        self._running = True
        while self._running:
            try:
                v = self._device.measure_voltage()
                i = self._device.measure_current()
                p = self._device.measure_power()
                r = self._device.measure_resistance()
                self.measurement_ready.emit(v, i, p, r)
            except Exception as e:
                self.error_occurred.emit(f"测量失败: {e}")

            self.msleep(self._interval_ms)

    def stop(self) -> None:
        """停止线程"""
        self._running = False


@dataclass(frozen=True)
class _Command:
    request_id: str
    func: Callable[[], Any]


class _CommandWorker(QThread):
    result_ready = pyqtSignal(str, object)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, queue: Queue[_Command]):
        super().__init__()
        self._queue = queue
        self._running = False

    def run(self) -> None:
        self._running = True
        while self._running:
            cmd = self._queue.get()
            if cmd.request_id == "__STOP__":
                break
            try:
                res = cmd.func()
                self.result_ready.emit(cmd.request_id, res)
            except Exception as e:
                self.error_occurred.emit(cmd.request_id, str(e))

    def stop(self) -> None:
        self._running = False
        try:
            self._queue.put_nowait(_Command("__STOP__", lambda: None))
        except Exception:
            pass


class DeviceManager(QObject):
    """设备管理器，负责连接、断开、测量轮询"""

    connected = pyqtSignal(str)  # 连接成功，参数为 IDN
    disconnected = pyqtSignal()
    error_occurred = pyqtSignal(str)
    measurement_ready = pyqtSignal(float, float, float, float)  # v, i, p, r
    comm_log = pyqtSignal(str, str)  # direction, message
    command_result = pyqtSignal(str, object)  # request_id, result
    command_error = pyqtSignal(str, str)  # request_id, error

    def __init__(self):
        super().__init__()
        self._transport: Transport | None = None
        self._scpi: SCPIClient | None = None
        self._device: ElectronicLoad | None = None
        self._measurement_worker: MeasurementWorker | None = None

        self._pending_connect_ids: set[str] = set()
        self._pending_disconnect_ids: set[str] = set()

        self._cmd_queue: Queue[_Command] = Queue()
        self._cmd_worker = _CommandWorker(self._cmd_queue)
        self._cmd_worker.result_ready.connect(self._on_command_result)
        self._cmd_worker.error_occurred.connect(self._on_command_error)
        self._cmd_worker.start()

    def connect_serial_async(self, port: str, baudrate: int = 115200) -> str:
        """异步连接串口设备（不阻塞 UI）"""
        req = self._enqueue(lambda: self._connect_serial_impl(port, baudrate))
        self._pending_connect_ids.add(req)
        return req

    def connect_tcp_async(self, host: str, port: int) -> str:
        """异步连接 TCP 设备（不阻塞 UI）"""
        req = self._enqueue(lambda: self._connect_tcp_impl(host, port))
        self._pending_connect_ids.add(req)
        return req

    def _connect_serial_impl(self, port: str, baudrate: int) -> str:
        self._stop_measurement()
        self._cleanup()

        self._transport = SerialTransport(port, baudrate)
        self._transport.open()
        return self._setup_device_impl()

    def _connect_tcp_impl(self, host: str, port: int) -> str:
        self._stop_measurement()
        self._cleanup()

        self._transport = TcpTransport(host, port)
        self._transport.open()
        return self._setup_device_impl()

    def _setup_device_impl(self) -> str:
        if not self._transport:
            raise ConnectionError("连接未建立")

        self._scpi = SCPIClient(self._transport)
        self._scpi.set_log_callback(self._on_comm_log)
        self._device = ElectronicLoad(self._scpi)

        idn = self._device.get_idn()

        try:
            self._device.set_remote()
        except Exception:
            pass

        return idn

    def disconnect_async(self) -> str:
        """异步断开连接（不阻塞 UI）"""
        req = self._enqueue(self._disconnect_impl)
        self._pending_disconnect_ids.add(req)
        return req

    def _disconnect_impl(self) -> None:
        self._stop_measurement()
        self._cleanup()

    def _cleanup(self) -> None:
        """清理资源"""
        if self._transport:
            self._transport.close()
        self._transport = None
        self._scpi = None
        self._device = None

    def _enqueue(self, func: Callable[[], Any]) -> str:
        request_id = uuid4().hex
        self._cmd_queue.put(_Command(request_id, func))
        return request_id

    def send_async(self, command: str) -> str:
        return self._enqueue(lambda: self._send_impl(command))

    def query_async(self, command: str) -> str:
        return self._enqueue(lambda: self._query_impl(command))

    def run_device_call_async(self, func: Callable[[ElectronicLoad], Any]) -> str:
        return self._enqueue(lambda: func(self._require_device()))

    def _require_device(self) -> ElectronicLoad:
        if not self._device:
            raise SCPIError("设备未连接")
        return self._device

    def _send_impl(self, command: str) -> None:
        if not self._scpi:
            raise SCPIError("设备未连接")
        self._scpi.send(command)

    def _query_impl(self, command: str) -> str:
        if not self._scpi:
            raise SCPIError("设备未连接")
        return self._scpi.query(command)

    def export_metadata_async(self) -> str:
        def _job() -> dict:
            dev = self._require_device()
            mode = dev.get_mode()
            max_i = dev.get_current_protection()
            max_p = dev.get_power_protection()
            return {"mode": mode, "max_current": max_i, "max_power": max_p}

        return self._enqueue(_job)

    def _on_command_result(self, request_id: str, result: object) -> None:
        if request_id.startswith("__"):
            return

        if request_id in self._pending_connect_ids:
            self._pending_connect_ids.discard(request_id)
            idn = str(result)
            self.connected.emit(idn)
            self._start_measurement()

        if request_id in self._pending_disconnect_ids:
            self._pending_disconnect_ids.discard(request_id)
            self.disconnected.emit()

        self.command_result.emit(request_id, result)

    def _on_command_error(self, request_id: str, error: str) -> None:
        self.command_error.emit(request_id, error)
        if request_id.startswith("__"):
            return

        is_connect = request_id in self._pending_connect_ids
        is_disconnect = request_id in self._pending_disconnect_ids

        self._pending_connect_ids.discard(request_id)
        self._pending_disconnect_ids.discard(request_id)

        if is_connect or is_disconnect:
            self.error_occurred.emit(error)

    def shutdown(self) -> None:
        self._stop_measurement()
        try:
            self._cmd_worker.stop()
            self._cmd_worker.wait(1000)
        except Exception:
            pass

    def _start_measurement(self) -> None:
        """启动测量轮询"""
        if not self._device:
            return

        if self._measurement_worker:
            return

        self._measurement_worker = MeasurementWorker(self._device)
        self._measurement_worker.measurement_ready.connect(self.measurement_ready)
        self._measurement_worker.error_occurred.connect(self.error_occurred)
        self._measurement_worker.finished.connect(self._on_measurement_finished)
        self._measurement_worker.start()

    def _on_measurement_finished(self) -> None:
        self._measurement_worker = None

    def set_measurement_enabled(self, enabled: bool) -> None:
        """启用/暂停测量轮询（用于曲线暂停时停止查询）"""
        if enabled:
            if self.is_connected():
                self._start_measurement()
            return

        if self._measurement_worker:
            try:
                self._measurement_worker.stop()
            except Exception:
                pass

    def _stop_measurement(self) -> None:
        """停止测量轮询"""
        if self._measurement_worker:
            self._measurement_worker.stop()
            self._measurement_worker.wait()
            self._measurement_worker = None

    def _on_comm_log(self, direction: str, message: str) -> None:
        """通信日志回调"""
        self.comm_log.emit(direction, message)

    @property
    def device(self) -> ElectronicLoad | None:
        """获取设备实例"""
        return self._device

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._device is not None and self._scpi is not None and self._scpi.is_connected()
