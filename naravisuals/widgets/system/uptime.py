from naravisuals.core.base_widget import AsyncCommandWidget

class UptimeWidget(AsyncCommandWidget):
    WIDGET_NAME = "Uptime"

    def __init__(self, parent=None):
        super().__init__(["uptime", "-p"], parent)
        self.set_update_interval(60000) # Update every minute

    def _handle_success(self, output: str):
        # Output is typically "up 2 hours, 15 minutes"
        self.set_text(f"⏳ {output}")
