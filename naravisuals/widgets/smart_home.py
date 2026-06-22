import requests
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from naravisuals.base import PanelWidget
from naravisuals.config import config

class SmartHomeToggle(PanelWidget):
    WIDGET_NAME = "Smart Home"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(0)
        
        self.btn = QPushButton("💡 Toggle Lights")
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(self._toggle)
        self._layout.addWidget(self.btn)

    def _toggle(self):
        # MVP: Send a dummy POST request to a configured endpoint
        endpoint = config.get("smart_home", "endpoint", "http://homeassistant.local:8123/api/webhook/toggle")
        try:
            # Short timeout so it doesn't freeze the GUI
            requests.post(endpoint, timeout=1.0)
            self.btn.setText("💡 Sent!")
        except Exception:
            self.btn.setText("💡 Error")
