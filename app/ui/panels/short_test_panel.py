from __future__ import annotations

import time

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class ShortTestPanel(QFrame):
    start_requested = pyqtSignal(float, str, str)  # duration_s, curr_prot, pow_prot
    stop_requested = pyqtSignal()
    estop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")

        self._running = False
        self._duration_s: float = 0.0
        self._start_monotonic: float = 0.0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        title = QLabel("短路测试")
        title.setStyleSheet("font-size: 14px; font-weight: 800;")

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.in_duration = QLineEdit()
        self.in_duration.setPlaceholderText("短路时长(s)")

        self.in_curr_prot = QLineEdit()
        self.in_curr_prot.setPlaceholderText("电流保护(A) - CURR:PROT")

        self.in_pow_prot = QLineEdit()
        self.in_pow_prot.setPlaceholderText("功率保护(W) - POW:PROT")

        grid.addWidget(QLabel("短路时长"), 0, 0)
        grid.addWidget(self.in_duration, 0, 1)
        grid.addWidget(QLabel("电流保护"), 1, 0)
        grid.addWidget(self.in_curr_prot, 1, 1)
        grid.addWidget(QLabel("功率保护"), 2, 0)
        grid.addWidget(self.in_pow_prot, 2, 1)

        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("开始短路")
        self.btn_stop = QPushButton("停止")
        self.btn_stop.setProperty("variant", "secondary")
        self.btn_estop = QPushButton("紧急停止")
        self.btn_estop.setProperty("danger", "true")

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_estop)
        btn_row.addStretch(1)

        self.lab_status = QLabel("状态：未开始")
        self.lab_timer = QLabel("计时：--")
        for w in (self.lab_status, self.lab_timer):
            w.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._on_tick)

        root.addWidget(title)
        root.addLayout(grid)
        root.addLayout(btn_row)
        root.addWidget(self.lab_status)
        root.addWidget(self.lab_timer)
        root.addStretch(1)

        self.btn_start.clicked.connect(self._on_start_clicked)
        self.btn_stop.clicked.connect(self.stop_requested)
        self.btn_estop.clicked.connect(self.estop_requested)

        self._refresh_buttons()

    def _refresh_buttons(self) -> None:
        self.btn_start.setEnabled(not self._running)
        self.btn_stop.setEnabled(self._running)

    def _on_start_clicked(self) -> None:
        if self._running:
            return

        duration_text = self.in_duration.text().strip()
        curr_prot = self.in_curr_prot.text().strip()
        pow_prot = self.in_pow_prot.text().strip()

        try:
            duration_s = float(duration_text) if duration_text else 0.0
        except ValueError:
            QMessageBox.warning(self, "错误", "短路时长格式错误，请输入数字")
            return

        if duration_s <= 0:
            QMessageBox.warning(self, "错误", "短路时长必须大于 0")
            return

        if curr_prot:
            try:
                float(curr_prot)
            except ValueError:
                QMessageBox.warning(self, "错误", "电流保护格式错误，请输入数字")
                return

        if pow_prot:
            try:
                float(pow_prot)
            except ValueError:
                QMessageBox.warning(self, "错误", "功率保护格式错误，请输入数字")
                return

        self.start_requested.emit(duration_s, curr_prot, pow_prot)

    def set_running(self, running: bool, duration_s: float | None = None) -> None:
        if running:
            self._running = True
            self._duration_s = float(duration_s or 0.0)
            self._start_monotonic = time.monotonic()
            self.lab_status.setText("状态：运行中")
            self._timer.start()
        else:
            self._running = False
            self._timer.stop()
            self.lab_status.setText("状态：已停止")
            self.lab_timer.setText("计时：--")

        self._refresh_buttons()

    def _on_tick(self) -> None:
        if not self._running:
            return

        elapsed = time.monotonic() - self._start_monotonic
        remain = max(0.0, self._duration_s - elapsed)
        self.lab_timer.setText(f"计时：已运行 {elapsed:.1f}s / 剩余 {remain:.1f}s")

        if remain <= 0:
            self.stop_requested.emit()
