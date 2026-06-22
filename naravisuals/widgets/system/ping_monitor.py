import re
from naravisuals.core.base_widget import AsyncCommandWidget

class PingMonitor(AsyncCommandWidget):
    WIDGET_NAME = "Ping Monitor"

    def __init__(self, parent=None):
        # Ping Google DNS once, timeout after 1 second
        super().__init__(["ping", "-c", "1", "-W", "1", "8.8.8.8"], parent)
        self.set_update_interval(2000) # Every 2 seconds

    def _handle_success(self, output: str):
        match = re.search(r"time=([\d\.]+)\s*ms", output)
        if match:
            ms = float(match.group(1))
            self.set_text(f"📡 {ms:.1f} ms")
        else:
            self.set_text("📡 timeout")

    def _handle_error(self, err: str):
        self.set_text("📡 offline")
