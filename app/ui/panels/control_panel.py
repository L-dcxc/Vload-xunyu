from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..widgets.segmented import SegmentedControl


class ControlPanel(QFrame):
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    estop_clicked = pyqtSignal()
    mode_changed = pyqtSignal(str)
    apply_params_clicked = pyqtSignal(str)  # 参数下发信号，参数为模式 (CC/CV/CP/CR)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")
        self.setMinimumWidth(280)  # 减小最小宽度

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(12)

        title = QLabel("设备控制")
        title.setStyleSheet("font-size: 14px; font-weight: 800;")
        root.addWidget(title)

        # 模式选择 - 顺序改为 CV, CC, CR, CP
        mode_title = QLabel("模式选择")
        mode_title.setStyleSheet("color: #9AA7B2; font-size: 12px;")
        self.mode = SegmentedControl(["CV", "CC", "CR", "CP"])  # 修改顺序
        self.mode.changed.connect(self._on_mode_changed_internal)

        root.addWidget(mode_title)
        root.addWidget(self.mode)

        param_title = QLabel("参数设置")
        param_title.setStyleSheet("color: #9AA7B2; font-size: 12px;")
        root.addWidget(param_title)

        # 创建堆叠控件，用于不同模式的参数界面
        self.param_stack = QStackedWidget()

        # 按新顺序创建参数界面：CV, CC, CR, CP
        cv_widget = self._create_cv_params()
        cc_widget = self._create_cc_params()
        cr_widget = self._create_cr_params()
        cp_widget = self._create_cp_params()

        self.param_stack.addWidget(cv_widget)  # index 0
        self.param_stack.addWidget(cc_widget)  # index 1
        self.param_stack.addWidget(cr_widget)  # index 2
        self.param_stack.addWidget(cp_widget)  # index 3

        root.addWidget(self.param_stack)

        monitor_title = QLabel("实时监控")
        monitor_title.setStyleSheet("color: #9AA7B2; font-size: 12px;")
        root.addWidget(monitor_title)

        self.mon_v = QLabel("电压  -- V")
        self.mon_i = QLabel("电流  -- A")
        self.mon_p = QLabel("功率  -- W")
        self.mon_r = QLabel("内阻  -- Ω")
        for w in (self.mon_v, self.mon_i, self.mon_p, self.mon_r):
            w.setStyleSheet("font-size: 18px; font-weight: 800;")

        root.addWidget(self.mon_v)
        root.addWidget(self.mon_i)
        root.addWidget(self.mon_p)
        root.addWidget(self.mon_r)

        run_title = QLabel("运行控制")
        run_title.setStyleSheet("color: #9AA7B2; font-size: 12px;")
        root.addWidget(run_title)

        run_row = QHBoxLayout()
        self.btn_start = QPushButton("START")
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setProperty("variant", "secondary")
        self.btn_estop = QPushButton("紧急停止")
        self.btn_estop.setProperty("danger", "true")

        run_row.addWidget(self.btn_start)
        run_row.addWidget(self.btn_stop)
        root.addLayout(run_row)
        root.addWidget(self.btn_estop)

        root.addStretch(1)

        self.btn_start.clicked.connect(self.start_clicked)
        self.btn_stop.clicked.connect(self.stop_clicked)
        self.btn_estop.clicked.connect(self.estop_clicked)

        # 连接各模式的下发参数按钮
        self.btn_apply_cv.clicked.connect(lambda: self._emit_apply_params("CV"))
        self.btn_apply_cc.clicked.connect(lambda: self._emit_apply_params("CC"))
        self.btn_apply_cr.clicked.connect(lambda: self._emit_apply_params("CR"))
        self.btn_apply_cp.clicked.connect(lambda: self._emit_apply_params("CP"))

        # 默认显示 CV 模式参数
        self._on_mode_changed_internal("CV")

    def _emit_apply_params(self, mode: str) -> None:
        """发射下发参数信号"""
        self.apply_params_clicked.emit(mode)

    def _create_cc_params(self) -> QWidget:
        """创建 CC 模式参数界面"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self.cc_current = QLineEdit()
        self.cc_current.setPlaceholderText("电流设定(A)")
        self.cc_current_prot = QLineEdit()
        self.cc_current_prot.setPlaceholderText("最大电流(A)")
        self.cc_power_prot = QLineEdit()
        self.cc_power_prot.setPlaceholderText("最大功率(W)")

        self.btn_apply_cc = QPushButton("下发参数")
        self.btn_apply_cc.setProperty("variant", "secondary")

        layout.addWidget(QLabel("电流设定"), 0, 0)
        layout.addWidget(self.cc_current, 0, 1)
        layout.addWidget(QLabel("最大电流"), 1, 0)
        layout.addWidget(self.cc_current_prot, 1, 1)
        layout.addWidget(QLabel("最大功率"), 2, 0)
        layout.addWidget(self.cc_power_prot, 2, 1)
        layout.addWidget(self.btn_apply_cc, 3, 0, 1, 2)

        return widget

    def _create_cv_params(self) -> QWidget:
        """创建 CV 模式参数界面"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self.cv_voltage = QLineEdit()
        self.cv_voltage.setPlaceholderText("电压设定(V)")
        self.cv_current_prot = QLineEdit()
        self.cv_current_prot.setPlaceholderText("最大电流(A)")
        self.cv_power_prot = QLineEdit()
        self.cv_power_prot.setPlaceholderText("最大功率(W)")
        self.cv_slew = QLineEdit()
        self.cv_slew.setPlaceholderText("电压速率(V/ms)")

        self.btn_apply_cv = QPushButton("下发参数")
        self.btn_apply_cv.setProperty("variant", "secondary")

        layout.addWidget(QLabel("电压设定"), 0, 0)
        layout.addWidget(self.cv_voltage, 0, 1)
        layout.addWidget(QLabel("最大电流"), 1, 0)
        layout.addWidget(self.cv_current_prot, 1, 1)
        layout.addWidget(QLabel("最大功率"), 2, 0)
        layout.addWidget(self.cv_power_prot, 2, 1)
        layout.addWidget(QLabel("电压速率"), 3, 0)
        layout.addWidget(self.cv_slew, 3, 1)
        layout.addWidget(self.btn_apply_cv, 4, 0, 1, 2)

        return widget

    def _create_cp_params(self) -> QWidget:
        """创建 CP 模式参数界面"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self.cp_power = QLineEdit()
        self.cp_power.setPlaceholderText("功率设定(W)")
        self.cp_current_prot = QLineEdit()
        self.cp_current_prot.setPlaceholderText("最大电流(A)")
        self.cp_power_prot = QLineEdit()
        self.cp_power_prot.setPlaceholderText("最大功率(W)")

        self.btn_apply_cp = QPushButton("下发参数")
        self.btn_apply_cp.setProperty("variant", "secondary")

        layout.addWidget(QLabel("功率设定"), 0, 0)
        layout.addWidget(self.cp_power, 0, 1)
        layout.addWidget(QLabel("最大电流"), 1, 0)
        layout.addWidget(self.cp_current_prot, 1, 1)
        layout.addWidget(QLabel("最大功率"), 2, 0)
        layout.addWidget(self.cp_power_prot, 2, 1)
        layout.addWidget(self.btn_apply_cp, 3, 0, 1, 2)

        return widget

    def _create_cr_params(self) -> QWidget:
        """创建 CR 模式参数界面"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self.cr_resistance = QLineEdit()
        self.cr_resistance.setPlaceholderText("电阻设定(Ω)")
        self.cr_current_prot = QLineEdit()
        self.cr_current_prot.setPlaceholderText("最大电流(A)")
        self.cr_power_prot = QLineEdit()
        self.cr_power_prot.setPlaceholderText("最大功率(W)")

        self.btn_apply_cr = QPushButton("下发参数")
        self.btn_apply_cr.setProperty("variant", "secondary")

        layout.addWidget(QLabel("电阻设定"), 0, 0)
        layout.addWidget(self.cr_resistance, 0, 1)
        layout.addWidget(QLabel("最大电流"), 1, 0)
        layout.addWidget(self.cr_current_prot, 1, 1)
        layout.addWidget(QLabel("最大功率"), 2, 0)
        layout.addWidget(self.cr_power_prot, 2, 1)
        layout.addWidget(self.btn_apply_cr, 3, 0, 1, 2)

        return widget

    def _on_mode_changed_internal(self, mode_text: str) -> None:
        """内部模式切换处理"""
        # 更新参数界面 - 新顺序：CV, CC, CR, CP
        mode_map = {
            "CV": 0,
            "CC": 1,
            "CR": 2,
            "CP": 3,
        }
        idx = mode_map.get(mode_text, 0)
        self.param_stack.setCurrentIndex(idx)
        # 发射信号给外部
        self.mode_changed.emit(mode_text)

    def set_mode_value(self, mode_text: str, emit: bool = False) -> None:
        """设置模式选择。

        emit=False 用于仅同步 UI 显示（不触发外部模式切换下发）。
        """
        if emit:
            self.mode.set_value(mode_text)
            return

        self.mode.blockSignals(True)
        try:
            self.mode.set_value(mode_text)
        finally:
            self.mode.blockSignals(False)

        mode_map = {
            "CV": 0,
            "CC": 1,
            "CR": 2,
            "CP": 3,
        }
        self.param_stack.setCurrentIndex(mode_map.get(mode_text, 0))

    def get_mode_params(self, mode: str) -> dict:
        """获取当前模式的参数"""
        if mode == "CC":
            return {
                "current": self.cc_current.text().strip(),
                "current_prot": self.cc_current_prot.text().strip(),
                "power_prot": self.cc_power_prot.text().strip(),
            }
        elif mode == "CV":
            return {
                "voltage": self.cv_voltage.text().strip(),
                "current_prot": self.cv_current_prot.text().strip(),
                "power_prot": self.cv_power_prot.text().strip(),
                "slew": self.cv_slew.text().strip(),
            }
        elif mode == "CP":
            return {
                "power": self.cp_power.text().strip(),
                "current_prot": self.cp_current_prot.text().strip(),
                "power_prot": self.cp_power_prot.text().strip(),
            }
        elif mode == "CR":
            return {
                "resistance": self.cr_resistance.text().strip(),
                "current_prot": self.cr_current_prot.text().strip(),
                "power_prot": self.cr_power_prot.text().strip(),
            }
        return {}

    def set_monitor_values(self, v: float | None, i: float | None, p: float | None, r: float | None) -> None:
        self.mon_v.setText(f"电压  {v:.3f} V" if v is not None else "电压  -- V")
        self.mon_i.setText(f"电流  {i:.3f} A" if i is not None else "电流  -- A")
        self.mon_p.setText(f"功率  {p:.3f} W" if p is not None else "功率  -- W")
        self.mon_r.setText(f"内阻  {r:.3f} Ω" if r is not None else "内阻  -- Ω")

    def set_running(self, running: bool) -> None:
        """设置运行状态，running=True 时 STOP 按钮变醒目"""
        if running:
            self.btn_stop.setProperty("variant", "warning")
            self.btn_stop.setStyle(self.btn_stop.style())
        else:
            self.btn_stop.setProperty("variant", "secondary")
            self.btn_stop.setStyle(self.btn_stop.style())
