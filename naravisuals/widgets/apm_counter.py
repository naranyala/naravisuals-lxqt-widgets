import random
from PyQt6.QtWidgets import QLabel
from naravisuals.base import PanelWidget

class APMCounter(PanelWidget):
    WIDGET_NAME = "APM Counter"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(1000)
        self.label = QLabel("⌨️ 0 APM")
        self.label.setStyleSheet("color: #ffaa00; font-weight: bold;")
        self._layout.addWidget(self.label)
        
        self.simulated_apm = 0

    def _on_tick(self):
        # MVP: Simulating keystrokes since actual global keylogging
        # requires root /dev/input/ or complex X11 hooks.
        # TODO: Implement python-evdev integration
        self.simulated_apm += random.randint(-15, 20)
        self.simulated_apm = max(0, min(self.simulated_apm, 150))
        
        self.label.setText(f"⌨️ {self.simulated_apm} APM")
