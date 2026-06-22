import psutil
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from naravisuals.base import PanelWidget


class NetGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._points = [0] * 60
        self._max_val = 1
        self.setMinimumHeight(50)

    def add_value(self, val):
        self._points.append(val)
        if len(self._points) > 60:
            self._points.pop(0)
        self._max_val = max(max(self._points), 1)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w = self.width()
        h = self.height()
        p.fillRect(0, 0, w, h, QColor(20, 20, 20))
        if not self._points:
            return
        step = w / 60.0
        pen = QPen(QColor(46, 204, 113))
        pen.setWidth(2)
        p.setPen(pen)
        for i in range(1, len(self._points)):
            x1 = int((i - 1) * step)
            y1 = int(h - (self._points[i - 1] / self._max_val * h))
            x2 = int(i * step)
            y2 = int(h - (self._points[i] / self._max_val * h))
            p.drawLine(x1, y1, x2, y2)


class NetworkMonitor(PanelWidget):
    WIDGET_NAME = "Network Monitor"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000)

        self._down_label = QLabel("⬇ 0 B/s")
        self._down_label.setStyleSheet("font-size: 10px; color: #3498db;")
        self._up_label = QLabel("⬆ 0 B/s")
        self._up_label.setStyleSheet("font-size: 10px; color: #e67e22;")
        self._graph = NetGraph()

        stats_row = QHBoxLayout()
        stats_row.addWidget(self._down_label)
        stats_row.addWidget(self._up_label)
        stats_row.addStretch()

        self._layout.addLayout(stats_row)
        self._layout.addWidget(self._graph)

        self._last_recv = psutil.net_io_counters().bytes_recv
        self._last_sent = psutil.net_io_counters().bytes_sent

        self._interfaces_label = QLabel("")
        self._interfaces_label.setStyleSheet("font-size: 9px; color: #666;")
        self._layout.addWidget(self._interfaces_label)

    def _on_tick(self):
        counters = psutil.net_io_counters()
        now_recv = counters.bytes_recv
        now_sent = counters.bytes_sent
        down = now_recv - self._last_recv
        up = now_sent - self._last_sent
        self._last_recv = now_recv
        self._last_sent = now_sent

        self._down_label.setText(f"⬇ {self._format(down)}/s")
        self._up_label.setText(f"⬆ {self._format(up)}/s")
        self._graph.add_value(down)

        ifcs = psutil.net_if_stats()
        active = [k for k, v in ifcs.items() if v.isup]
        self._interfaces_label.setText(", ".join(active[:3]))

    @staticmethod
    def _format(b):
        for unit in ('B', 'KB', 'MB', 'GB'):
            if b < 1024:
                return f"{b:.1f}{unit}"
            b /= 1024
        return f"{b:.1f}TB"


if __name__ == "__main__":
    NetworkMonitor.launch_standalone()
