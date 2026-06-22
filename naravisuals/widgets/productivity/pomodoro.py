from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QSpinBox, QFrame

from naravisuals.core.base_widget import PanelWidget


class PomodoroTimer(PanelWidget):
    WIDGET_NAME = "Pomodoro Timer"
    WORK_MIN = 25
    BREAK_MIN = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(1000)
        self._state = "idle"
        self._seconds_left = self.WORK_MIN * 60
        self._is_work = True
        self._pomodoro_count = 0

        self._time_label = QLabel(self._format_time(self._seconds_left))
        self._time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #e74c3c;")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet("font-size: 11px; color: #888;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._count_label = QLabel("🍅 0")
        self._count_label.setStyleSheet("font-size: 10px; color: #666;")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        control_row = QHBoxLayout()
        self._start_btn = QPushButton("Start")
        self._start_btn.clicked.connect(self._toggle)
        self._reset_btn = QPushButton("Reset")
        self._reset_btn.clicked.connect(self._reset)
        self._work_spin = QSpinBox()
        self._work_spin.setRange(1, 60)
        self._work_spin.setValue(self.WORK_MIN)
        self._work_spin.setSuffix("m work")
        self._work_spin.valueChanged.connect(self._update_work)
        control_row.addWidget(self._start_btn)
        control_row.addWidget(self._reset_btn)
        control_row.addWidget(self._work_spin)
        control_row.addStretch()

        self._layout.addWidget(self._time_label)
        self._layout.addWidget(self._status_label)
        self._layout.addWidget(self._count_label)
        self._layout.addLayout(control_row)

    def _format_time(self, secs):
        m = secs // 60
        s = secs % 60
        return f"{m:02d}:{s:02d}"

    def _update_work(self, val):
        if self._state == "idle":
            self.WORK_MIN = val
            self._seconds_left = val * 60
            self._time_label.setText(self._format_time(self._seconds_left))

    def _on_tick(self):
        if self._state == "running":
            self._seconds_left -= 1
            self._time_label.setText(self._format_time(self._seconds_left))
            if self._seconds_left <= 0:
                self._switch_phase()

    def _switch_phase(self):
        self._is_work = not self._is_work
        if self._is_work:
            self._seconds_left = self.WORK_MIN * 60
            self._status_label.setText("Work time!")
            self._time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #e74c3c;")
        else:
            self._seconds_left = self.BREAK_MIN * 60
            self._status_label.setText("Break time! 🎉")
            self._time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2ecc71;")
            self._pomodoro_count += 1
            self._count_label.setText(f"🍅 {self._pomodoro_count}")

    def _toggle(self):
        if self._state == "running":
            self._state = "paused"
            self._start_btn.setText("Resume")
        elif self._state == "paused":
            self._state = "running"
            self._start_btn.setText("Pause")
        else:
            self._state = "running"
            self._start_btn.setText("Pause")
            self._status_label.setText("Work time!")

    def _reset(self):
        self._state = "idle"
        self._is_work = True
        self._seconds_left = self.WORK_MIN * 60
        self._time_label.setText(self._format_time(self._seconds_left))
        self._time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #e74c3c;")
        self._status_label.setText("Ready")
        self._start_btn.setText("Start")


if __name__ == "__main__":
    PomodoroTimer.launch_standalone()
