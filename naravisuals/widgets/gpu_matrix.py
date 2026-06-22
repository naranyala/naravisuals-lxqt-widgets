import subprocess
from PyQt6.QtWidgets import QLabel
from naravisuals.base import PanelWidget

class GPUMatrix(PanelWidget):
    WIDGET_NAME = "GPU Matrix"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(1000)
        self.label = QLabel("GPU: N/A")
        self._layout.addWidget(self.label)

    def _on_tick(self):
        try:
            # MVP: Nvidia SMI integration.
            # TODO: add AMD rocm-smi fallback
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            if output:
                util, temp = output.split(", ")
                self.label.setText(f"🎮 {util}% | 🌡️ {temp}°C")
        except Exception:
            self.label.setText("🎮 No NVIDIA GPU")
