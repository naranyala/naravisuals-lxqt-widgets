import subprocess
import re
from naravisuals.core.base_widget import AsyncCommandWidget

class VolumeWidget(AsyncCommandWidget):
    WIDGET_NAME = "Volume Control"

    def __init__(self, parent=None):
        # MVP: Uses amixer to get Master volume
        super().__init__(["amixer", "sget", "Master"], parent)
        self.set_update_interval(1000)

    def _handle_success(self, output: str):
        match = re.search(r"\[(\d+)%\]", output)
        if match:
            vol = match.group(1)
            icon = "🔊" if int(vol) > 0 else "🔇"
            self.set_text(f"{icon} {vol}%")
        else:
            self.set_text("🔊 --%")

    def wheelEvent(self, event):
        # MVP scroll to change volume
        if event.angleDelta().y() > 0:
            subprocess.Popen(["amixer", "sset", "Master", "5%+"])
        else:
            subprocess.Popen(["amixer", "sset", "Master", "5%-"])
        self._on_tick() # Force update immediately for responsive feel
