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
        self._follow_window_s = 600.0
        self._t = deque(maxlen=50000)
        self._v = deque(maxlen=50000)
        self._i = deque(maxlen=50000)
        self._p = deque(maxlen=50000)
        self._r = deque(maxlen=50000)  # 添加电阻数据

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
        self._legend = self.plot.addLegend(offset=(10, 10))
        
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

        self._install_legend_sync()

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

    def show_all(self) -> None:
        if not self._t:
            return
        self.disable_follow()
        t_min = float(self._t[0])
        t_max = float(self._t[-1])
        vb = self.plot.getPlotItem().vb
        vb.setXRange(t_min, t_max, padding=0.02)
        vb.enableAutoRange(axis='y', enable=True)

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
        self._sync_checkboxes_from_curves()

    def _sync_checkboxes_from_curves(self) -> None:
        def _set(cb: QCheckBox, checked: bool) -> None:
            cb.blockSignals(True)
            try:
                cb.setChecked(checked)
            finally:
                cb.blockSignals(False)

        _set(self.cb_v, bool(self.curve_v.isVisible()))
        _set(self.cb_i, bool(self.curve_i.isVisible()))
        _set(self.cb_p, bool(self.curve_p.isVisible()))
        _set(self.cb_r, bool(self.curve_r.isVisible()))

    def _install_legend_sync(self) -> None:
        if not getattr(self, "_legend", None):
            return

        def _set_cb(cb: QCheckBox, checked: bool) -> None:
            cb.blockSignals(True)
            try:
                cb.setChecked(checked)
            finally:
                cb.blockSignals(False)
            self._refresh_visibility()

        for sample, label in getattr(self._legend, "items", []):
            try:
                text = str(label.text)
            except Exception:
                try:
                    text = str(label.textItem.toPlainText())
                except Exception:
                    text = ""

            if "电压" in text:
                cb = self.cb_v
                curve = self.curve_v
            elif "电流" in text:
                cb = self.cb_i
                curve = self.curve_i
            elif "功率" in text:
                cb = self.cb_p
                curve = self.curve_p
            elif "电阻" in text or "内阻" in text:
                cb = self.cb_r
                curve = self.curve_r
            else:
                continue

            old = getattr(label, "mouseClickEvent", None)

            def _handler(ev, _cb=cb, _curve=curve, _old=old):  # type: ignore[no-untyped-def]
                try:
                    if _old:
                        _old(ev)
                except Exception:
                    pass
                _set_cb(_cb, not _curve.isVisible())

            try:
                label.mouseClickEvent = _handler  # type: ignore[method-assign]
            except Exception:
                pass

    def _on_plot_clicked(self, event):  # type: ignore[no-untyped-def]
        # 无论点到哪里（含左侧图例的“眼睛”），都先同步一次状态，避免左右开关不同步
        try:
            self._sync_checkboxes_from_curves()
        except Exception:
            pass

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

        # 处理完标记点后再次同步（legend 点击可能发生在同一帧）
        try:
            self._sync_checkboxes_from_curves()
        except Exception:
            pass
