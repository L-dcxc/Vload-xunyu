from __future__ import annotations

import time
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)

from ..core.device_manager import DeviceManager
from ..core.recording_manager import RecordingManager
from .dialogs.about_dialog import AboutDialog
from .panels.connection_panel import ConnectionPanel
from .panels.control_panel import ControlPanel
from .panels.data_log_panel import DataLogPanel
from .panels.advanced_test_panel import AdvancedTestPanel
from .panels.header_bar import HeaderBar
from .panels.plot_panel import PlotPanel
from .panels.sequence_panel import SequencePanel


class MainWindowV2(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VLoad - 直流负载可视化")
        self.setMinimumSize(1200, 700)  # 降低最小尺寸以适应小屏幕

        self.header = HeaderBar()
        self.connection = ConnectionPanel()
        self.control = ControlPanel()
        self.plot = PlotPanel()
        self.sequence = SequencePanel()
        self.data_log = DataLogPanel()
        self.advanced = AdvancedTestPanel()

        # 设备管理器
        self._device_manager = DeviceManager()
        self._pending_handlers: dict[str, tuple[callable, callable | None]] = {}
        self._recording = False
        self._recorder = RecordingManager()
        self._last_idn: str = ""

        self._build_ui()
        self._wire_events()
        self._wire_device_manager()

        self.header.set_device(model="--", idn="--")
        self.header.set_address("--")
        self.header.set_connected(False)

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        layout.addWidget(self.header)

        self.pages = QTabWidget()

        monitor_page = QWidget()
        monitor_layout = QVBoxLayout(monitor_page)
        monitor_layout.setContentsMargins(0, 0, 0, 0)
        monitor_layout.setSpacing(12)

        # 添加连接面板到顶部
        monitor_layout.addWidget(self.connection)

        monitor_splitter = QSplitter()
        monitor_splitter.setChildrenCollapsible(False)

        # 为控制面板添加滚动区域
        control_scroll = QScrollArea()
        control_scroll.setWidget(self.control)
        control_scroll.setWidgetResizable(True)
        control_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        control_scroll.setMinimumWidth(320)  # 设置最小宽度
        control_scroll.setMaximumWidth(400)  # 设置最大宽度

        monitor_splitter.addWidget(control_scroll)
        monitor_splitter.addWidget(self.plot)
        monitor_splitter.setStretchFactor(0, 0)
        monitor_splitter.setStretchFactor(1, 1)
        monitor_splitter.setSizes([350, 850])  # 调整初始比例

        monitor_layout.addWidget(monitor_splitter, 1)

        seq_page = QWidget()
        seq_layout = QVBoxLayout(seq_page)
        seq_layout.setContentsMargins(0, 0, 0, 0)
        seq_layout.setSpacing(12)
        seq_layout.addWidget(self.sequence, 1)

        data_page = QWidget()
        data_layout = QVBoxLayout(data_page)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(12)
        data_layout.addWidget(self.data_log, 1)

        adv_page = QWidget()
        adv_layout = QVBoxLayout(adv_page)
        adv_layout.setContentsMargins(0, 0, 0, 0)
        adv_layout.setSpacing(12)
        adv_layout.addWidget(self.advanced, 1)

        self.pages.addTab(monitor_page, "监控")
        self.pages.addTab(adv_page, "高级测试")
        self.pages.addTab(seq_page, "任务序列")
        self.pages.addTab(data_page, "数据与日志")

        layout.addWidget(self.pages, 1)

        self.setCentralWidget(root)

    def _wire_events(self) -> None:
        self.header.help_clicked.connect(self._on_help_clicked)
        self.connection.connect_clicked.connect(self._on_connect)
        self.connection.disconnect_clicked.connect(self._on_disconnect)
        self.control.start_clicked.connect(self._on_start)
        self.control.stop_clicked.connect(self._on_stop)
        self.control.estop_clicked.connect(self._on_estop)
        self.control.mode_changed.connect(self._on_mode_changed)
        self.control.apply_params_clicked.connect(self._on_apply_params)  # 连接新信号

        self.plot.btn_pause.clicked.connect(self._on_plot_pause_clicked)
        self.plot.btn_clear.clicked.connect(lambda: self.data_log.append_run_log("曲线：清空"))

        self.sequence.btn_run.clicked.connect(lambda: self.data_log.append_run_log("任务序列：开始执行（占位）"))
        self.sequence.btn_stop.clicked.connect(lambda: self.data_log.append_run_log("任务序列：停止（占位）"))
        self.sequence.btn_load.clicked.connect(lambda: self.data_log.append_run_log("任务序列：加载（占位）"))
        self.sequence.btn_save.clicked.connect(lambda: self.data_log.append_run_log("任务序列：保存（占位）"))

        self.data_log.btn_term_send.clicked.connect(self._on_terminal_send)
        self.data_log.term_input.returnPressed.connect(self._on_terminal_send)
        self.data_log.data_imported.connect(self._on_data_imported)
        self.data_log.clear_requested.connect(self._on_clear_requested)

        self.advanced.short_start_requested.connect(self._on_short_start_requested)
        self.advanced.short_stop_requested.connect(self._on_short_stop_requested)
        self.advanced.short_estop_requested.connect(self._on_short_estop_requested)

    def _wire_device_manager(self) -> None:
        """连接设备管理器信号"""
        self._device_manager.connected.connect(self._on_device_connected)
        self._device_manager.disconnected.connect(self._on_device_disconnected)
        self._device_manager.error_occurred.connect(self._on_device_error)
        self._device_manager.measurement_ready.connect(self._on_measurement_ready)
        self._device_manager.comm_log.connect(self._on_comm_log)
        self._device_manager.command_result.connect(self._on_command_result)
        self._device_manager.command_error.connect(self._on_command_error)

        self.data_log.export_requested.connect(self._on_export_requested)

    def _on_plot_pause_clicked(self) -> None:
        QTimer.singleShot(
            0,
            lambda: (
                self.data_log.append_run_log("曲线：暂停" if self.plot._paused else "曲线：继续"),
                self._device_manager.set_measurement_enabled(not self.plot._paused),
            ),
        )

    def _on_connect(self) -> None:
        """连接按钮点击"""
        params = self.connection.get_connection_params()
        transport = params["transport"]

        if transport == "COM":
            port = params.get("port")
            if not port:
                QMessageBox.warning(self, "错误", "未找到可用的串口，请检查设备连接")
                return
            baudrate = params.get("baudrate", 115200)
            addr_display = f"{port}@{baudrate}"
            self.data_log.append_run_log(f"正在连接串口: {addr_display}...")
            self.connection.set_connecting(True)
            self._device_manager.connect_serial_async(port, baudrate)
        else:  # TCP
            addr = params.get("address", "").strip()
            if not addr:
                QMessageBox.warning(self, "错误", "请输入 TCP 地址")
                return
            self.data_log.append_run_log(f"正在连接 TCP: {addr}...")
            try:
                parts = addr.split(":")
                host = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 5025
                self.connection.set_connecting(True)
                self._device_manager.connect_tcp_async(host, port)
            except (ValueError, IndexError):
                QMessageBox.warning(self, "错误", "TCP 地址格式错误，应为 IP:端口")

    def _on_disconnect(self) -> None:
        """断开按钮点击"""
        self.connection.set_connecting(True)
        self._device_manager.disconnect_async()

    def _on_device_connected(self, idn: str) -> None:
        """设备连接成功"""
        self._last_idn = idn
        params = self.connection.get_connection_params()
        if params["transport"] == "COM":
            addr = f"{params['port']}@{params['baudrate']}"
        else:
            addr = params["address"]

        parts = idn.split(",")
        model = parts[0] if len(parts) > 0 else "Unknown"
        device_id = parts[1] if len(parts) > 1 else "Unknown"

        self.header.set_connected(True)
        self.header.set_address(addr)
        self.header.set_device(model=model, idn=device_id)
        self.connection.set_connected(True)
        self.connection.set_device_info(idn)
        self.connection.set_connecting(False)
        self.data_log.append_run_log(f"已连接：{addr}")
        self.data_log.append_run_log(f"设备信息：{idn}")
        self.data_log.append_run_log("已进入远程模式")

        self._recording = False
        self._device_manager.set_measurement_enabled(True)

        req = self._device_manager.run_device_call_async(lambda dev: dev.get_mode())

        def _ok(mode_raw: object) -> None:
            mode = str(mode_raw).strip().upper()
            mode_map = {
                "CURR": "CC",
                "CC": "CC",
                "VOLT": "CV",
                "CV": "CV",
                "RES": "CR",
                "CR": "CR",
                "POW": "CP",
                "CP": "CP",
            }
            ui_mode = mode_map.get(mode, "CV")
            self.control.set_mode_value(ui_mode, emit=False)
            self.data_log.append_run_log(f"设备模式：{ui_mode} ({mode})")

        self._pending_handlers[req] = (
            _ok,
            lambda err: self.data_log.append_run_log(f"读取设备模式失败: {err}"),
        )

    def _on_device_disconnected(self) -> None:
        """设备断开连接"""
        self.header.set_connected(False)
        self.connection.set_connected(False)
        self.connection.set_connecting(False)
        self.data_log.append_run_log("已断开连接")
        self._recording = False
        try:
            self._recorder.stop()
        except Exception:
            pass

    def _on_device_error(self, error: str) -> None:
        """设备错误"""
        # 连接/断开失败时，确保 UI 不停留在“连接中…”状态
        try:
            self.connection.set_connecting(False)
        except Exception:
            pass

        self.data_log.append_run_log(f"错误：{error}")
        QMessageBox.critical(self, "设备错误", error)

    def _on_measurement_ready(self, v: float, i: float, p: float, r: float) -> None:
        """测量数据就绪"""
        # 局部导入兜底：即使模块热加载/异常覆盖全局 datetime，也不影响采样回调
        from datetime import datetime as _dt

        t = time.time()  # 使用当前时间戳
        ts = _dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.control.set_monitor_values(v, i, p, r)
        self.advanced.set_monitor_values(v, i, p, r)
        self.plot.append_point(t, v, i, p, r)
        if self._recording:
            self.data_log.append_data(v, i, p, r)
            try:
                self._recorder.append(ts, v, i, p, r)
            except Exception:
                pass

    def _on_short_start_requested(self, duration_s: float, curr_prot: str, pow_prot: str) -> None:
        if not self._device_manager.is_connected():
            return

        try:
            dur = float(duration_s)
        except Exception:
            return

        try:
            ops: list[tuple[callable, str]] = []
            if curr_prot:
                v = float(curr_prot)
                ops.append((lambda dev, val=v: dev.set_current_protection(val), f"设置电流保护：{curr_prot} A"))
            if pow_prot:
                v = float(pow_prot)
                ops.append((lambda dev, val=v: dev.set_power_protection(val), f"设置功率保护：{pow_prot} W"))
        except ValueError:
            QMessageBox.warning(self, "错误", "参数格式错误，请输入数字")
            return

        self.advanced.set_locked(True)

        def _job(dev):
            for op, _log in ops:
                op(dev)
            dev.set_input_short(True)
            dev.set_input(True)

        req = self._device_manager.run_device_call_async(_job)

        def _ok(_res: object) -> None:
            for _op, _log in ops:
                self.data_log.append_run_log(_log)
            self.control.set_running(True)
            self.advanced.short_panel.set_running(True, duration_s=dur)
            self._recording = True
            self._start_recording_session()
            self.data_log.append_run_log(f"短路测试开始：{dur:.1f}s")

        def _err(err: str) -> None:
            self.advanced.set_locked(False)
            self.data_log.append_run_log(f"短路测试启动失败: {err}")

        self._pending_handlers[req] = (_ok, _err)

    def _on_short_stop_requested(self) -> None:
        if not self._device_manager.is_connected():
            return

        def _job(dev):
            dev.set_input(False)
            dev.set_input_short(False)

        req = self._device_manager.run_device_call_async(_job)

        def _ok(_res: object) -> None:
            self.control.set_running(False)
            self.advanced.short_panel.set_running(False)
            self._recording = False
            self._recorder.stop()
            self.advanced.set_locked(False)
            self.data_log.append_run_log("短路测试结束")

        def _err(err: str) -> None:
            self.data_log.append_run_log(f"短路测试停止失败: {err}")

        self._pending_handlers[req] = (_ok, _err)

    def _on_short_estop_requested(self) -> None:
        if not self._device_manager.is_connected():
            return

        def _job(dev):
            dev.set_input(False)
            try:
                dev.set_input_short(False)
            except Exception:
                pass

        req = self._device_manager.run_device_call_async(_job)

        def _ok(_res: object) -> None:
            self.control.set_running(False)
            self.advanced.short_panel.set_running(False)
            self._recording = False
            self._recorder.stop()
            self.advanced.set_locked(False)
            self.data_log.append_run_log("短路测试紧急停止")

        def _err(err: str) -> None:
            self.data_log.append_run_log(f"短路紧急停止失败: {err}")

        self._pending_handlers[req] = (_ok, _err)

    def _on_clear_requested(self) -> None:
        if self.data_log.data_row_count() == 0:
            self.plot.clear()
            self.data_log.clear_data()
            self.data_log.append_run_log("数据：清空")
            return

        box = QMessageBox(self)
        box.setWindowTitle("清空数据")
        box.setText("清空将丢失当前采集数据。是否先导出保存？")
        btn_export = box.addButton("导出", QMessageBox.ButtonRole.AcceptRole)
        btn_clear = box.addButton("直接清空", QMessageBox.ButtonRole.DestructiveRole)
        box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        box.exec()

        clicked = box.clickedButton()
        if clicked == btn_export:
            self.data_log.open_export_dialog()
            return
        if clicked == btn_clear:
            self.plot.clear()
            self.data_log.clear_data()
            self.data_log.append_run_log("数据：清空")

    def _on_comm_log(self, direction: str, message: str) -> None:
        """通信日志"""
        self.data_log.append_comm_log(f"{direction}: {message}")

    def _on_start(self) -> None:
        """START 按钮"""
        if not self._device_manager.is_connected():
            return

        req = self._device_manager.run_device_call_async(lambda dev: dev.set_input(True))
        self._pending_handlers[req] = (
            lambda _res: (
                self.control.set_running(True),
                setattr(self, "_recording", True),
                self._start_recording_session(),
                self.data_log.append_run_log("已启动负载 (INPUT ON)"),
            ),
            lambda err: self.data_log.append_run_log(f"启动失败: {err}"),
        )

    def _start_recording_session(self) -> None:
        try:
            parts = self._last_idn.split(",") if self._last_idn else []
            model = parts[0].strip() if len(parts) > 0 else ""
            dev_id = parts[1].strip() if len(parts) > 1 else ""
            meta = {
                "idn": self._last_idn,
                "model": model,
                "id": dev_id,
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sample_interval_ms": 200,
            }
            session = self._recorder.start_new_session(meta)
            self.data_log.append_run_log(f"采集会话：{session.session_dir}")
        except Exception as e:
            self.data_log.append_run_log(f"创建采集会话失败: {e}")

    def _on_stop(self) -> None:
        """STOP 按钮"""
        if not self._device_manager.is_connected():
            return

        req = self._device_manager.run_device_call_async(lambda dev: dev.set_input(False))
        self._pending_handlers[req] = (
            lambda _res: (
                self.control.set_running(False),
                setattr(self, "_recording", False),
                self._recorder.stop(),
                self.data_log.append_run_log("已停止负载 (INPUT OFF)"),
            ),
            lambda err: self.data_log.append_run_log(f"停止失败: {err}"),
        )

    def _on_estop(self) -> None:
        """紧急停止按钮"""
        if not self._device_manager.is_connected():
            return

        req = self._device_manager.run_device_call_async(lambda dev: dev.set_input(False))
        self._pending_handlers[req] = (
            lambda _res: (
                self.control.set_running(False),
                setattr(self, "_recording", False),
                self._recorder.stop(),
                self.data_log.append_run_log("紧急停止！(INPUT OFF)"),
            ),
            lambda err: self.data_log.append_run_log(f"紧急停止失败: {err}"),
        )

    def _on_mode_changed(self, mode_text: str) -> None:
        """模式切换"""
        if not self._device_manager.is_connected():
            return

        # 从 UI 文本映射到 SCPI 命令
        mode_map = {
            "CC": "CURR",
            "CV": "VOLT",
            "CP": "POW",
            "CR": "RES",
        }
        mode = mode_map.get(mode_text)
        if not mode:
            return

        req = self._device_manager.run_device_call_async(lambda dev: dev.set_mode(mode))
        self._pending_handlers[req] = (
            lambda _res: self.data_log.append_run_log(f"模式切换：{mode_text} ({mode})"),
            lambda err: self.data_log.append_run_log(f"模式切换失败: {err}"),
        )

    def _on_apply_params(self, mode: str) -> None:
        """下发参数按钮"""
        if not self._device_manager.is_connected():
            return

        params = self.control.get_mode_params(mode)

        try:
            ops: list[tuple[callable, str]] = []
            if mode == "CC":
                if params.get("current"):
                    val = float(params["current"])
                    ops.append((lambda dev, v=val: dev.set_current(v), f"设置电流：{params['current']} A"))
                if params.get("current_prot"):
                    val = float(params["current_prot"])
                    ops.append((lambda dev, v=val: dev.set_current_protection(v), f"设置最大电流：{params['current_prot']} A"))
                if params.get("power_prot"):
                    val = float(params["power_prot"])
                    ops.append((lambda dev, v=val: dev.set_power_protection(v), f"设置最大功率：{params['power_prot']} W"))

            elif mode == "CV":
                if params.get("voltage"):
                    val = float(params["voltage"])
                    ops.append((lambda dev, v=val: dev.set_voltage(v), f"设置电压：{params['voltage']} V"))
                if params.get("current_prot"):
                    val = float(params["current_prot"])
                    ops.append((lambda dev, v=val: dev.set_current_protection(v), f"设置最大电流：{params['current_prot']} A"))
                if params.get("power_prot"):
                    val = float(params["power_prot"])
                    ops.append((lambda dev, v=val: dev.set_power_protection(v), f"设置最大功率：{params['power_prot']} W"))
                if params.get("slew"):
                    val = float(params["slew"])
                    ops.append((lambda dev, v=val: dev.set_voltage_slew(v), f"设置电压速率：{params['slew']} V/ms"))

            elif mode == "CP":
                if params.get("power"):
                    val = float(params["power"])
                    ops.append((lambda dev, v=val: dev.set_power(v), f"设置功率：{params['power']} W"))
                if params.get("current_prot"):
                    val = float(params["current_prot"])
                    ops.append((lambda dev, v=val: dev.set_current_protection(v), f"设置最大电流：{params['current_prot']} A"))
                if params.get("power_prot"):
                    val = float(params["power_prot"])
                    ops.append((lambda dev, v=val: dev.set_power_protection(v), f"设置最大功率：{params['power_prot']} W"))

            elif mode == "CR":
                if params.get("resistance"):
                    val = float(params["resistance"])
                    ops.append((lambda dev, v=val: dev.set_resistance(v), f"设置电阻：{params['resistance']} Ω"))
                if params.get("current_prot"):
                    val = float(params["current_prot"])
                    ops.append((lambda dev, v=val: dev.set_current_protection(v), f"设置最大电流：{params['current_prot']} A"))
                if params.get("power_prot"):
                    val = float(params["power_prot"])
                    ops.append((lambda dev, v=val: dev.set_power_protection(v), f"设置最大功率：{params['power_prot']} W"))

        except ValueError:
            QMessageBox.warning(self, "错误", "参数格式错误，请输入数字")
            return

        if not ops:
            return

        def _job(dev):
            for op, _log in ops:
                op(dev)

        req = self._device_manager.run_device_call_async(_job)

        def _ok(_res):
            for _op, _log in ops:
                self.data_log.append_run_log(_log)

        self._pending_handlers[req] = (_ok, lambda err: self.data_log.append_run_log(f"参数下发失败: {err}"))

    def _on_terminal_send(self) -> None:
        """SCPI 终端发送"""
        cmd = self.data_log.term_input.text().strip()
        if not cmd:
            return

        if not self._device_manager.is_connected():
            self.data_log.append_term("错误：设备未连接")
            self.data_log.term_input.clear()
            return

        self.data_log.append_term(f">> {cmd}")

        if "?" in cmd:
            req = self._device_manager.query_async(cmd)
            self._pending_handlers[req] = (
                lambda res: self.data_log.append_term(f"<< {res}"),
                lambda err: self.data_log.append_term(f"错误: {err}"),
            )
        else:
            req = self._device_manager.send_async(cmd)
            self._pending_handlers[req] = (
                lambda _res: self.data_log.append_term("<< OK"),
                lambda err: self.data_log.append_term(f"错误: {err}"),
            )

        self.data_log.term_input.clear()

    def _on_command_result(self, request_id: str, result: object) -> None:
        handler = self._pending_handlers.pop(request_id, None)
        if not handler:
            return
        ok, _err = handler
        if ok:
            ok(result)

    def _on_command_error(self, request_id: str, error: str) -> None:
        handler = self._pending_handlers.pop(request_id, None)
        if not handler:
            return
        _ok, err = handler
        if err:
            err(error)

    def _on_export_requested(self, file_path: str, selected_filter: str) -> None:
        if not self._device_manager.is_connected():
            QMessageBox.warning(self, "错误", "设备未连接，无法读取模式/保护值用于导出")
            return

        req = self._device_manager.export_metadata_async()

        def _ok(meta: object) -> None:
            meta_dict = meta if isinstance(meta, dict) else {}
            session = self._recorder.session
            if session:
                self.data_log.export_from_session(file_path, selected_filter, meta_dict, session.data_csv_path)
            else:
                self.data_log.export_with_metadata(file_path, selected_filter, meta_dict)

        def _err(err: str) -> None:
            QMessageBox.warning(self, "导出失败", f"读取设备信息失败：{err}")

        self._pending_handlers[req] = (_ok, _err)

    def closeEvent(self, event):  # type: ignore[no-untyped-def]
        try:
            self._device_manager.shutdown()
        except Exception:
            pass
        try:
            self._recorder.stop()
        except Exception:
            pass
        return super().closeEvent(event)

    def _on_help_clicked(self) -> None:
        """显示帮助对话框"""
        dialog = AboutDialog(self)
        dialog.exec()

    def _on_data_imported(self, data_list: list) -> None:
        """处理导入的数据"""
        # 清空当前波形
        self.plot.clear()
        self.data_log.append_run_log(f"导入波形数据：{len(data_list)} 条记录")

        # 将导入的数据添加到波形和数据表
        # data_list 中的 t 需要转换为时间戳
        base_time = time.time()
        for idx, (t, v, i, p, r) in enumerate(data_list):
            # 将相对时间转换为绝对时间戳
            timestamp = base_time + t
            self.plot.append_point(timestamp, v, i, p, r)
            self.data_log.append_data(v, i, p, r)
