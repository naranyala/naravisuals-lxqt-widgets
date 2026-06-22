import psutil
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from naravisuals.base import PanelWidget


class BatteryIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._charging = False
        self.setMinimumSize(40, 24)
        self.setMaximumSize(80, 30)

    def set_values(self, percent, charging):
        self._percent = percent
        self._charging = charging
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w = self.width()
        h = self.height()
        bw = w - 6
        bh = h - 4

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor(46, 204, 113)
        if self._percent < 20:
            color = QColor(231, 76, 60)
        elif self._percent < 40:
            color = QColor(241, 196, 15)

        p.setPen(QPen(QColor(200, 200, 200), 1))
        p.drawRect(2, 2, bw, bh)
        p.fillRect(4, 4, bw - 4, bh - 4, QColor(30, 30, 30))
        fill_w = int((bw - 4) * self._percent / 100.0)
        p.fillRect(4, 4, fill_w, bh - 4, color)

        tip_x = bw + 3
        tip_y = h // 2 - 3
        p.fillRect(tip_x, tip_y, 4, 6, QColor(200, 200, 200))

        if self._charging:
            p.setPen(QColor(255, 255, 255))
            p.drawText(4, 2, bw - 4, bh - 4, Qt.AlignmentFlag.AlignCenter, "⚡")

        p.setPen(QColor(200, 200, 200))
        p.drawText(4, 2, bw - 4, bh - 4, Qt.AlignmentFlag.AlignCenter, f"{self._percent}%")


class BatteryInfo(PanelWidget):
    WIDGET_NAME = "Battery Info"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(5000)

        self._icon = BatteryIcon()
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("font-size: 9px; color: #888;")
        self._time_label = QLabel("")
        self._time_label.setStyleSheet("font-size: 9px; color: #666;")

        row = QHBoxLayout()
        row.addWidget(self._icon)
        right = QVBoxLayout()
        right.addWidget(self._status_label)
        right.addWidget(self._time_label)
        right.addStretch()
        row.addLayout(right)
        row.addStretch()
        self._layout.addLayout(row)

        self.add_action("Refresh", self._on_tick)

    def _on_tick(self):
        try:
            batt = psutil.sensors_battery()
            if batt:
                percent = int(batt.percent)
                charging = batt.power_plugged
                self._icon.set_values(percent, charging)
                status = "Charging" if charging else "Discharging"
                self._status_label.setText(f"{status}")
                secs_left = batt.secsleft
                if secs_left > 0 and not charging:
                    h = secs_left // 3600
                    m = (secs_left % 3600) // 60
                    self._time_label.setText(f"{h}h {m}m remaining")
                elif charging:
                    self._time_label.setText("Plugged in")
                else:
                    self._time_label.setText("")
            else:
                self._status_label.setText("No battery")
        except Exception:
            self._status_label.setText("Error")


if __name__ == "__main__":
    BatteryInfo.launch_standalone()
