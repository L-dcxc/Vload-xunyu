"""关于对话框"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


class AboutDialog(QDialog):
    """关于对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 VLoad")
        self.setFixedSize(550, 500)  # 增加对话框尺寸
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)  # 增加边距
        layout.setSpacing(20)

        # Logo
        logo_label = QLabel()
        logo_path = Path("LOGO_全.png")
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                # 增加 Logo 尺寸
                scaled_pixmap = pixmap.scaled(
                    300, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                logo_label.setMinimumHeight(100)  # 确保有足够高度
        else:
            logo_label.setText("VLoad")
            logo_label.setStyleSheet("font-size: 36px; font-weight: 800;")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(logo_label)

        # 软件名称和版本号放在同一行
        title_version_label = QLabel("VLoad - 直流负载可视化    版本：V1.0")
        title_version_label.setStyleSheet("font-size: 18px; font-weight: 700;")
        title_version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_version_label)

        layout.addSpacing(10)

        # 公司信息
        company_label = QLabel("作者：广州迅屿科技有限公司")
        company_label.setStyleSheet("font-size: 14px;")
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(company_label)

        # 网站
        website_label = QLabel('<a href="http://www.xunyutek.com" style="color: #22C6A8; text-decoration: none;">www.xunyutek.com</a>')
        website_label.setStyleSheet("font-size: 14px;")
        website_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        website_label.setOpenExternalLinks(True)
        layout.addWidget(website_label)

        layout.addSpacing(10)

        # 联系方式
        contact_title = QLabel("联系方式：")
        contact_title.setStyleSheet("font-size: 14px; font-weight: 600;")
        contact_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(contact_title)

        phone_label = QLabel("电话：13417952055")
        phone_label.setStyleSheet("font-size: 13px; color: #9AA7B2;")
        phone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(phone_label)

        email_label = QLabel("邮箱：2711597159@qq.com")
        email_label.setStyleSheet("font-size: 13px; color: #9AA7B2;")
        email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(email_label)

        layout.addStretch(1)

        # 关闭按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        close_btn = QPushButton("关闭")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)
