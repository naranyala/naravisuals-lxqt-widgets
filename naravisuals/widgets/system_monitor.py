import psutil
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from naravisuals.base import PanelWidget


class UsageBar(QWidget):
    def __init__(self, label, color):
        super().__init__()
        self._value = 0.0
        self._label = label
        self._color = QColor(color)
        self.setMinimumHeight(18)
        self.setMaximumHeight(18)

    def set_value(self, v):
        self._value = v
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w = self.width()
        h = self.height()
        p.fillRect(0, 0, w, h, QColor(40, 40, 40))
        fill = int(w * self._value / 100.0)
        p.fillRect(0, 0, fill, h, self._color)
        p.setPen(QColor(200, 200, 200))
        p.drawText(4, 0, w - 4, h, Qt.AlignmentFlag.AlignVCenter, f"{self._label}: {self._value:.1f}%")


class SystemMonitor(PanelWidget):
    WIDGET_NAME = "System Monitor"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000)
        
        # Override the default QVBoxLayout with QHBoxLayout
        QWidget().setLayout(self._layout) # Delete old layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)
        
        self.setMinimumHeight(18)
        
        self._cpu_bar = UsageBar("CPU", QColor(46, 204, 113))
        self._mem_bar = UsageBar("RAM", QColor(52, 152, 219))
        self._disk_bar = UsageBar("DISK", QColor(155, 89, 182))
        self._swap_bar = UsageBar("SWAP", QColor(231, 76, 60))
        self._net_label = QLabel("NET: ?")
        self._net_label.setStyleSheet("color: #aaa; font-size: 10px;")
        
        self._layout.addWidget(self._cpu_bar)
        self._layout.addWidget(self._mem_bar)
        self._layout.addWidget(self._disk_bar)
        self._layout.addWidget(self._swap_bar)
        self._layout.addWidget(self._net_label)
        self._last_net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

    def _on_tick(self):
        self._cpu_bar.set_value(psutil.cpu_percent())
        mem = psutil.virtual_memory()
        self._mem_bar.set_value(mem.percent)
        disk = psutil.disk_usage('/')
        self._disk_bar.set_value(disk.percent)
        swap = psutil.swap_memory()
        self._swap_bar.set_value(swap.percent)
        now = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        diff = now - self._last_net
        self._last_net = now
        self._net_label.setText(f"NET: {self._format_bytes(diff)}/s")

    @staticmethod
    def _format_bytes(b):
        for unit in ('B', 'KB', 'MB', 'GB'):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"


if __name__ == "__main__":
    SystemMonitor.launch_standalone()
