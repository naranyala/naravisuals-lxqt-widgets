from PyQt6.QtCore import QProcess
from PyQt6.QtWidgets import QLabel
from naravisuals.base import PanelWidget

class SystemLogTicker(PanelWidget):
    WIDGET_NAME = "System Log Ticker"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(0) # Event-driven via QProcess
        self.label = QLabel("Waiting for logs...")
        self.label.setStyleSheet("color: #ff5555; font-family: monospace;")
        self._layout.addWidget(self.label)
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._read_log)
        # MVP: Tail system journal for priority 3 (ERR)
        self.process.start("journalctl", ["-f", "-p", "3", "-n", "1"])

    def _read_log(self):
        data = self.process.readAllStandardOutput().data().decode().strip()
        if data:
            lines = data.split('\n')
            # Extract just the message part of the latest log
            msg = lines[-1].split("]: ")[-1] if "]: " in lines[-1] else lines[-1]
            # Truncate for panel
            if len(msg) > 40:
                msg = msg[:37] + "..."
            self.label.setText(f"🚨 {msg}")
