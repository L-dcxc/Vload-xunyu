from __future__ import annotations

import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget, QPushButton

from ..theme import ACCENT, DANGER, TEXT_SECONDARY
from ..widgets.status_indicator import StatusIndicator


class HeaderBar(QWidget):
    help_clicked = pyqtSignal()  # 帮助按钮点击信号

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(60)  # 增加高度
        self.setProperty("card", "true")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)  # 增加边距
        layout.setSpacing(12)

        # 加载 LOGO 图片
        self.logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "LOGO_全.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # 缩放到合适大小，保持宽高比
            scaled_pixmap = pixmap.scaled(120, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo.setPixmap(scaled_pixmap)
            self.logo.setFixedHeight(40)
        else:
            # 如果图片不存在，显示文字
            self.logo.setText("LOGO")
            self.logo.setFixedSize(44, 32)
            self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo.setStyleSheet(
                "background: #0B1016; border: 1px solid #243040; border-radius: 8px; font-weight: 800;"
            )

        self.app_name = QLabel("VLoad - 直流负载可视化")
        self.app_name.setStyleSheet("font-size: 16px; font-weight: 800;")
        self.app_name.setMinimumWidth(220)

        self.device_info = QLabel("设备：--")
        self.device_info.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.device_info.setMinimumWidth(200)  # 确保设备信息有足够空间

        self.status_dot = StatusIndicator(10)
        self.status_text = QLabel("未连接")
        self.status_text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 700;")

        self.addr = QLabel("地址：--")
        self.addr.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.addr.setMinimumWidth(150)  # 确保地址有足够空间

        # 帮助按钮
        self.btn_help = QPushButton("帮助")
        self.btn_help.setProperty("variant", "secondary")
        self.btn_help.setMinimumWidth(70)
        self.btn_help.clicked.connect(self.help_clicked)

        layout.addWidget(self.logo)
        layout.addWidget(self.app_name)
        layout.addSpacing(10)
        layout.addWidget(self.device_info)
        layout.addStretch(1)
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_text)
        layout.addSpacing(12)
        layout.addWidget(self.addr)
        layout.addSpacing(12)
        layout.addWidget(self.btn_help)

        self.set_connected(False)

    def set_connected(self, connected: bool) -> None:
        if connected:
            self.status_dot.set_color(ACCENT)
            self.status_text.setText("已连接")
        else:
            self.status_dot.set_color(DANGER)
            self.status_text.setText("未连接")

    def set_device(self, model: str, idn: str) -> None:
        text = f"设备：{model}  ID：{idn}" if model or idn else "设备：--"
        self.device_info.setText(text)

    def set_address(self, address: str) -> None:
        self.addr.setText(f"地址：{address}" if address else "地址：--")
