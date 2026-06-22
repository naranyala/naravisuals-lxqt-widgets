import subprocess
from PyQt6.QtWidgets import QLabel
from naravisuals.base import PanelWidget

class ContainerRadar(PanelWidget):
    WIDGET_NAME = "Container Radar"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000) # Check every 2 seconds
        
        self.label = QLabel("🐳 Docker: ?")
        self.label.setStyleSheet("font-weight: bold; color: #0db7ed;")
        self._layout.addWidget(self.label)

    def _on_tick(self):
        try:
            # MVP: Read from docker CLI. 
            # TODO: read directly from /var/run/docker.sock via requests
            output = subprocess.check_output(["docker", "ps", "-q"], stderr=subprocess.DEVNULL)
            count = len(output.decode().strip().split('\n'))
            if not output.strip():
                count = 0
            self.label.setText(f"🐳 {count} Running")
        except FileNotFoundError:
            self.label.setText("🐳 Docker not found")
        except subprocess.CalledProcessError:
            self.label.setText("🐳 Permission Denied (Requires group)")
