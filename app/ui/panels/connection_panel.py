"""连接配置面板"""
from __future__ import annotations

import serial.tools.list_ports
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class ConnectionPanel(QFrame):
    """连接配置面板"""

    connect_clicked = pyqtSignal()
    disconnect_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")

        self._connected = False

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(12)

        # 连接方式
        root.addWidget(QLabel("连接方式"))
        self.transport = QComboBox()
        self.transport.addItems(["TCP", "COM"])
        self.transport.setMinimumWidth(80)
        self.transport.currentTextChanged.connect(self._on_transport_changed)
        root.addWidget(self.transport)

        # 地址配置（堆叠控件）
        self.addr_stack = QStackedWidget()

        # TCP 配置
        tcp_widget = QWidget()
        tcp_layout = QHBoxLayout(tcp_widget)
        tcp_layout.setContentsMargins(0, 0, 0, 0)
        tcp_layout.setSpacing(8)
        tcp_layout.addWidget(QLabel("地址"))
        self.tcp_address = QLineEdit()
        self.tcp_address.setPlaceholderText("192.168.1.50:5025")
        self.tcp_address.setMinimumWidth(180)
        tcp_layout.addWidget(self.tcp_address)

        # COM 配置
        com_widget = QWidget()
        com_layout = QHBoxLayout(com_widget)
        com_layout.setContentsMargins(0, 0, 0, 0)
        com_layout.setSpacing(8)
        com_layout.addWidget(QLabel("端口"))
        self.com_port = QComboBox()
        self.com_port.setMinimumWidth(150)
        com_layout.addWidget(self.com_port)
        self.btn_refresh_com = QPushButton("刷新")
        self.btn_refresh_com.setProperty("variant", "secondary")
        self.btn_refresh_com.setMinimumWidth(65)
        self.btn_refresh_com.setMaximumWidth(70)
        self.btn_refresh_com.clicked.connect(self._refresh_com_ports)
        com_layout.addWidget(self.btn_refresh_com)
        com_layout.addWidget(QLabel("波特率"))
        self.com_baudrate = QComboBox()
        self.com_baudrate.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.com_baudrate.setCurrentText("9600")
        self.com_baudrate.setMinimumWidth(100)
        com_layout.addWidget(self.com_baudrate)

        self.addr_stack.addWidget(tcp_widget)
        self.addr_stack.addWidget(com_widget)
        root.addWidget(self.addr_stack)

        # 连接按钮（紧跟在地址配置后面）
        self.btn_connect = QPushButton("连接")
        self.btn_connect.setMinimumWidth(70)
        self.btn_disconnect = QPushButton("断开")
        self.btn_disconnect.setProperty("variant", "secondary")
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setMinimumWidth(70)

        root.addWidget(self.btn_connect)
        root.addWidget(self.btn_disconnect)

        # 设备信息（放在连接按钮后面）
        self.idn_hint = QLabel("设备信息：--")
        self.idn_hint.setStyleSheet("color: #9AA7B2; font-size: 12px;")
        root.addWidget(self.idn_hint)

        root.addStretch(1)

        self.btn_connect.clicked.connect(self.connect_clicked)
        self.btn_disconnect.clicked.connect(self.disconnect_clicked)

        # 初始化
        self._refresh_com_ports()
        self.transport.setCurrentText("COM")
        self._on_transport_changed("COM")

    def _on_transport_changed(self, transport: str) -> None:
        """切换传输方式"""
        if transport == "TCP":
            self.addr_stack.setCurrentIndex(0)
        else:
            self.addr_stack.setCurrentIndex(1)

    def _refresh_com_ports(self) -> None:
        """刷新 COM 口列表"""
        current = self.com_port.currentText()
        self.com_port.clear()

        ports = serial.tools.list_ports.comports()
        if ports:
            for port in ports:
                display_name = f"{port.device}"
                if port.description and port.description != port.device:
                    display_name += f" ({port.description})"
                self.com_port.addItem(display_name, port.device)

            idx = self.com_port.findData(current)
            if idx >= 0:
                self.com_port.setCurrentIndex(idx)
            elif self.com_port.count() > 0:
                for i in range(self.com_port.count()):
                    if "COM1" not in self.com_port.itemText(i):
                        self.com_port.setCurrentIndex(i)
                        break
        else:
            self.com_port.addItem("未找到串口", None)

    def get_connection_params(self) -> dict:
        """获取连接参数"""
        transport = self.transport.currentText()
        if transport == "TCP":
            addr = self.tcp_address.text().strip()
            return {"transport": "TCP", "address": addr}
        else:
            port_data = self.com_port.currentData()
            if not port_data:
                return {"transport": "COM", "port": None, "baudrate": 9600}
            return {
                "transport": "COM",
                "port": port_data,
                "baudrate": int(self.com_baudrate.currentText()),
            }

    def set_connected(self, connected: bool) -> None:
        """设置连接状态"""
        self._connected = connected
        self.btn_connect.setEnabled(not connected)
        self.btn_disconnect.setEnabled(connected)
        
        # 连接后，断开按钮变为警告色（醒目）
        if connected:
            self.btn_disconnect.setProperty("variant", "warning")
            self.btn_disconnect.setStyle(self.btn_disconnect.style())  # 刷新样式
        else:
            self.btn_disconnect.setProperty("variant", "secondary")
            self.btn_disconnect.setStyle(self.btn_disconnect.style())
        
        self.transport.setEnabled(not connected)
        self.tcp_address.setEnabled(not connected)
        self.com_port.setEnabled(not connected)
        self.com_baudrate.setEnabled(not connected)
        self.btn_refresh_com.setEnabled(not connected)

    def set_connecting(self, connecting: bool) -> None:
        """设置连接中状态（连接/断开过程中禁用操作）"""
        if connecting:
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(False)
            self.btn_connect.setText("连接中…")
        else:
            self.btn_connect.setText("连接")
            self.set_connected(self._connected)

    def set_device_info(self, text: str) -> None:
        """设置设备信息"""
        self.idn_hint.setText(f"设备信息：{text}" if text else "设备信息：--")
