from __future__ import annotations

import time

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class BatteryTestPanel(QFrame):
    start_requested = pyqtSignal(str, str, str, str, str)  # discharge_mode, value, cutoff_v, cutoff_time_s, cutoff_mah
    stop_requested = pyqtSignal()
    estop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")

        self._running = False
        self._start_monotonic: float = 0.0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        title = QLabel("电池测试")
        title.setStyleSheet("font-size: 14px; font-weight: 800;")

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.sel_mode = QComboBox()
        self.sel_mode.addItems(["恒流放电", "恒阻放电", "恒功放电"])

        value_row = QWidget()
        value_layout = QHBoxLayout(value_row)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(8)

        self.in_value = QLineEdit()
        self.in_value.setPlaceholderText("放电参数")
        self.lab_unit = QLabel("A")
        self.lab_unit.setStyleSheet("color: #9AA7B2; font-size: 12px;")
        value_layout.addWidget(self.in_value, 1)
        value_layout.addWidget(self.lab_unit, 0)

        self.in_cutoff_v = QLineEdit()
        self.in_cutoff_v.setPlaceholderText("截止电压(V)")

        self.in_cutoff_time = QLineEdit()
        self.in_cutoff_time.setPlaceholderText("截止时间(s)")

        self.in_cutoff_mah = QLineEdit()
        self.in_cutoff_mah.setPlaceholderText("截止容量(mAh)")

        grid.addWidget(QLabel("放电模式"), 0, 0)
        grid.addWidget(self.sel_mode, 0, 1)
        grid.addWidget(QLabel("放电参数"), 1, 0)
        grid.addWidget(value_row, 1, 1)
        grid.addWidget(QLabel("截止电压"), 2, 0)
        grid.addWidget(self.in_cutoff_v, 2, 1)
        grid.addWidget(QLabel("截止时间"), 3, 0)
        grid.addWidget(self.in_cutoff_time, 3, 1)
        grid.addWidget(QLabel("截止容量"), 4, 0)
        grid.addWidget(self.in_cutoff_mah, 4, 1)

        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("开始放电")
        self.btn_stop = QPushButton("停止")
        self.btn_stop.setProperty("variant", "secondary")
        self.btn_estop = QPushButton("紧急停止")
        self.btn_estop.setProperty("danger", "true")

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_estop)
        btn_row.addStretch(1)

        stats = QFrame()
        stats.setProperty("card", "true")
        stats_layout = QVBoxLayout(stats)
        stats_layout.setContentsMargins(14, 12, 14, 12)
        stats_layout.setSpacing(6)

        self.lab_big_time = QLabel("00:00:00")
        self.lab_big_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lab_big_time.setStyleSheet("font-size: 28px; font-weight: 900; color: #E11D48;")

        self.lab_stat_v = QLabel("停止电压：-- V")
        self.lab_stat_t = QLabel("放电时间：--")
        self.lab_stat_mah = QLabel("毫安时：-- mAh")
        self.lab_stat_wh = QLabel("瓦时：-- Wh")
        for w in (self.lab_stat_v, self.lab_stat_t, self.lab_stat_mah, self.lab_stat_wh):
            w.setAlignment(Qt.AlignmentFlag.AlignCenter)
            w.setStyleSheet("font-size: 14px; font-weight: 900;")

        self.lab_stat_v.setStyleSheet("font-size: 14px; font-weight: 900; color: #22C55E;")
        self.lab_stat_t.setStyleSheet("font-size: 14px; font-weight: 900; color: #FFFFFF;")
        self.lab_stat_mah.setStyleSheet("font-size: 14px; font-weight: 900; color: #F59E0B;")
        self.lab_stat_wh.setStyleSheet("font-size: 14px; font-weight: 900; color: #A855F7;")

        stats_layout.addWidget(self.lab_big_time)
        stats_layout.addWidget(self.lab_stat_v)
        stats_layout.addWidget(self.lab_stat_t)
        stats_layout.addWidget(self.lab_stat_mah)
        stats_layout.addWidget(self.lab_stat_wh)

        self.lab_status = QLabel("状态：未开始")
        self.lab_status.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._on_tick)

        root.addWidget(title)
        root.addLayout(grid)
        root.addLayout(btn_row)
        root.addWidget(stats)
        root.addWidget(self.lab_status)
        root.addStretch(1)

        self.sel_mode.currentTextChanged.connect(self._on_mode_changed)
        self.btn_start.clicked.connect(self._on_start_clicked)
        self.btn_stop.clicked.connect(self.stop_requested)
        self.btn_estop.clicked.connect(self.estop_requested)

        self._on_mode_changed(self.sel_mode.currentText())
        self._refresh_buttons()

    def _on_mode_changed(self, mode_text: str) -> None:
        if "恒流" in mode_text:
            self.lab_unit.setText("A")
            self.in_value.setPlaceholderText("放电电流")
        elif "恒阻" in mode_text:
            self.lab_unit.setText("Ω")
            self.in_value.setPlaceholderText("放电电阻")
        else:
            self.lab_unit.setText("W")
            self.in_value.setPlaceholderText("放电功率")

    def _refresh_buttons(self) -> None:
        self.btn_start.setEnabled(not self._running)
        self.btn_stop.setEnabled(self._running)

    def _on_start_clicked(self) -> None:
        if self._running:
            return

        mode_text = self.sel_mode.currentText()
        if "恒流" in mode_text:
            mode = "CC"
        elif "恒阻" in mode_text:
            mode = "CR"
        else:
            mode = "CP"

        value = self.in_value.text().strip()
        cutoff_v = self.in_cutoff_v.text().strip()
        cutoff_time_s = self.in_cutoff_time.text().strip()
        cutoff_mah = self.in_cutoff_mah.text().strip()

        if not value:
            QMessageBox.warning(self, "错误", "请填写放电参数")
            return

        try:
            float(value)
        except ValueError:
            QMessageBox.warning(self, "错误", "放电参数格式错误，请输入数字")
            return

        if cutoff_v:
            try:
                float(cutoff_v)
            except ValueError:
                QMessageBox.warning(self, "错误", "截止电压格式错误，请输入数字")
                return

        if cutoff_time_s:
            try:
                float(cutoff_time_s)
            except ValueError:
                QMessageBox.warning(self, "错误", "截止时间格式错误，请输入数字")
                return

        if cutoff_mah:
            try:
                float(cutoff_mah)
            except ValueError:
                QMessageBox.warning(self, "错误", "截止容量格式错误，请输入数字")
                return

        if not cutoff_v and not cutoff_time_s and not cutoff_mah:
            QMessageBox.warning(self, "错误", "请至少设置一个截止条件")
            return

        self.start_requested.emit(mode, value, cutoff_v, cutoff_time_s, cutoff_mah)

    def set_running(self, running: bool) -> None:
        if running:
            self._running = True
            self._start_monotonic = time.monotonic()
            self.lab_status.setText("状态：运行中")
            self._timer.start()
        else:
            self._running = False
            self._timer.stop()
            self.lab_status.setText("状态：已停止")

        self._refresh_buttons()

    def reset_stats(self) -> None:
        self.lab_big_time.setText("00:00:00")
        self.lab_stat_v.setText("电压：-- V")
        self.lab_stat_t.setText("放电时间：00:00:00")
        self.lab_stat_mah.setText("毫安时：-- mAh")
        self.lab_stat_wh.setText("瓦时：-- Wh")

    def set_stats(self, voltage: float | None, elapsed_s: float, mah: float, wh: float) -> None:
        prefix = "电压" if self._running else "停止电压"
        self.lab_stat_v.setText(f"{prefix}：{voltage:.3f} V" if voltage is not None else f"{prefix}：-- V")

        h = int(elapsed_s // 3600)
        m = int((elapsed_s % 3600) // 60)
        s = int(elapsed_s % 60)
        self.lab_stat_t.setText(f"放电时间：{h:02d}:{m:02d}:{s:02d}")
        self.lab_stat_mah.setText(f"毫安时：{mah:.1f} mAh")
        self.lab_stat_wh.setText(f"瓦时：{wh:.3f} Wh")

    def _on_tick(self) -> None:
        if not self._running:
            return

        elapsed = max(0.0, time.monotonic() - self._start_monotonic)
        h = int(elapsed // 3600)
        m = int((elapsed % 3600) // 60)
        s = int(elapsed % 60)
        self.lab_big_time.setText(f"{h:02d}:{m:02d}:{s:02d}")
