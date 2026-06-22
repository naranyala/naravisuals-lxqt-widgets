import subprocess
from PyQt6.QtWidgets import QLabel
from naravisuals.base import PanelWidget

class BluetoothRadar(PanelWidget):
    WIDGET_NAME = "Bluetooth Radar"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(5000)
        self.label = QLabel("📶 BT: Scanning...")
        self.label.setStyleSheet("color: #0082fc;")
        self._layout.addWidget(self.label)

    def _on_tick(self):
        try:
            # MVP: Use bluetoothctl to see connected devices
            # TODO: use D-Bus directly
            output = subprocess.check_output(["bluetoothctl", "info"], stderr=subprocess.DEVNULL).decode()
            if "Missing device" in output or "No default controller" in output or not output.strip():
                self.label.setText("📶 BT: Disconnected")
            else:
                name = "Unknown"
                for line in output.split('\n'):
                    if "Name:" in line:
                        name = line.split("Name: ")[-1]
                        break
                self.label.setText(f"📶 {name}")
        except Exception:
            self.label.setText("📶 BT: Error")
