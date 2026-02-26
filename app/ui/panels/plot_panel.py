from __future__ import annotations

from collections import deque
from datetime import datetime

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..theme import ACCENT, TEXT_SECONDARY


class PlotPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")

        self._paused = False
        self._follow_latest = True
        self._follow_window_s = 60.0
        self._t = deque(maxlen=1200)
        self._v = deque(maxlen=1200)
        self._i = deque(maxlen=1200)
        self._p = deque(maxlen=1200)
        self._r = deque(maxlen=1200)  # 添加电阻数据

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("曲线监控")
        title.setStyleSheet("font-size: 14px; font-weight: 800;")

        header.addWidget(title)
        header.addStretch(1)

        self.cb_v = QCheckBox("电压")
        self.cb_i = QCheckBox("电流")
        self.cb_p = QCheckBox("功率")
        self.cb_r = QCheckBox("电阻")  # 添加电阻复选框
        for cb in (self.cb_v, self.cb_i, self.cb_p, self.cb_r):
            cb.setChecked(True)

        self.btn_pause = QPushButton("暂停")
        self.btn_pause.setProperty("variant", "secondary")
        self.btn_clear = QPushButton("清空")
        self.btn_clear.setProperty("variant", "secondary")

        self.btn_follow = QPushButton("跟随最新")
        self.btn_follow.setProperty("variant", "secondary")

        header.addWidget(self.cb_v)
        header.addWidget(self.cb_i)
        header.addWidget(self.cb_p)
        header.addWidget(self.cb_r)  # 添加到界面
        header.addSpacing(10)
        header.addWidget(self.btn_pause)
        header.addWidget(self.btn_clear)
        header.addWidget(self.btn_follow)

        self.marker_label = QLabel("标记点：--")
        self.marker_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")

        self.plot = pg.PlotWidget()
        self.plot.setBackground(None)
        self.plot.showGrid(x=True, y=True, alpha=0.25)
        self.plot.addLegend(offset=(10, 10))
        
        # 启用自动范围调整，解决鼠标交互后不刷新的问题
        self.plot.enableAutoRange(axis='x', enable=True)
        self.plot.enableAutoRange(axis='y', enable=True)
        self.plot.setAutoVisible(y=True)
        
        # 设置 X 轴为时间格式
        axis = pg.DateAxisItem(orientation='bottom')
        self.plot.setAxisItems({'bottom': axis})
        self.plot.getPlotItem().setLabel('bottom', '时间')

        self.curve_v = self.plot.plot(pen=pg.mkPen(ACCENT, width=2), name="电压(V)")
        self.curve_i = self.plot.plot(pen=pg.mkPen("#60A5FA", width=2), name="电流(A)")
        self.curve_p = self.plot.plot(pen=pg.mkPen("#F59E0B", width=2), name="功率(W)")
        self.curve_r = self.plot.plot(pen=pg.mkPen("#A78BFA", width=2), name="电阻(Ω)")  # 添加电阻曲线

        self._marker = pg.ScatterPlotItem(size=8, brush=pg.mkBrush("#E6EDF3"), pen=pg.mkPen("#0F141A"))
        self.plot.addItem(self._marker)

        root.addLayout(header)
        root.addWidget(self.marker_label)
        root.addWidget(self.plot, 1)

        self.cb_v.toggled.connect(self._refresh_visibility)
        self.cb_i.toggled.connect(self._refresh_visibility)
        self.cb_p.toggled.connect(self._refresh_visibility)
        self.cb_r.toggled.connect(self._refresh_visibility)  # 连接信号
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_clear.clicked.connect(self.clear)
        self.btn_follow.clicked.connect(self.enable_follow)

        self.plot.scene().sigMouseClicked.connect(self._on_plot_clicked)
        self.plot.getPlotItem().vb.sigRangeChangedManually.connect(self._on_range_changed_manually)

    def set_paused(self, paused: bool) -> None:
        self._paused = paused
        self.btn_pause.setText("继续" if paused else "暂停")

    def toggle_pause(self) -> None:
        self.set_paused(not self._paused)

    def clear(self) -> None:
        self._t.clear()
        self._v.clear()
        self._i.clear()
        self._p.clear()
        self._r.clear()  # 清空电阻数据
        self._marker.setData([])
        self.marker_label.setText("标记点：--")
        self._update_curves()
        self.enable_follow()

    def append_point(self, t_s: float, v: float, i: float, p: float, r: float) -> None:  # t_s 现在是时间戳
        if self._paused:
            return

        self._t.append(t_s)
        self._v.append(v)
        self._i.append(i)
        self._p.append(p)
        self._r.append(r)
        self._update_curves()
        if self._follow_latest:
            self._apply_follow_view()

    def enable_follow(self) -> None:
        self._follow_latest = True
        self.btn_follow.setText("暂停跟随")
        self._apply_follow_view(force=True)

    def disable_follow(self) -> None:
        self._follow_latest = False
        self.btn_follow.setText("跟随最新")

    def _apply_follow_view(self, force: bool = False) -> None:
        if not self._t:
            return

        t_latest = float(self._t[-1])
        t_min = float(self._t[0])
        left = max(t_latest - self._follow_window_s, t_min)
        right = t_latest

        vb = self.plot.getPlotItem().vb
        vb.setXRange(left, right, padding=0)
        if force:
            vb.enableAutoRange(axis='y', enable=True)

    def _on_range_changed_manually(self, *args) -> None:  # type: ignore[no-untyped-def]
        if self._follow_latest:
            self.disable_follow()

    def _update_curves(self) -> None:
        if not self._t:
            self.curve_v.setData([])
            self.curve_i.setData([])
            self.curve_p.setData([])
            self.curve_r.setData([])
            return

        t = np.fromiter(self._t, dtype=float)
        self.curve_v.setData(t, np.fromiter(self._v, dtype=float))
        self.curve_i.setData(t, np.fromiter(self._i, dtype=float))
        self.curve_p.setData(t, np.fromiter(self._p, dtype=float))
        self.curve_r.setData(t, np.fromiter(self._r, dtype=float))

    def _refresh_visibility(self) -> None:
        self.curve_v.setVisible(self.cb_v.isChecked())
        self.curve_i.setVisible(self.cb_i.isChecked())
        self.curve_p.setVisible(self.cb_p.isChecked())
        self.curve_r.setVisible(self.cb_r.isChecked())  # 控制电阻曲线显示

    def _on_plot_clicked(self, event):  # type: ignore[no-untyped-def]
        if not self._t:
            return

        pos = event.scenePos()
        if not self.plot.sceneBoundingRect().contains(pos):
            return

        mouse_point = self.plot.getPlotItem().vb.mapSceneToView(pos)
        x = float(mouse_point.x())

        t = np.fromiter(self._t, dtype=float)
        idx = int(np.argmin(np.abs(t - x)))

        tt = float(t[idx])
        vv = float(np.fromiter(self._v, dtype=float)[idx])
        ii = float(np.fromiter(self._i, dtype=float)[idx])
        pp = float(np.fromiter(self._p, dtype=float)[idx])
        rr = float(np.fromiter(self._r, dtype=float)[idx])

        # 将时间戳转换为可读时间
        time_str = datetime.fromtimestamp(tt).strftime("%H:%M:%S")
        
        self._marker.setData([tt], [vv])
        self.marker_label.setText(f"标记点：{time_str}  V={vv:.3f}V  I={ii:.3f}A  P={pp:.3f}W  R={rr:.3f}Ω")
