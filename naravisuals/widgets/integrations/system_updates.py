from naravisuals.core.base_widget import AsyncCommandWidget

class SystemUpdates(AsyncCommandWidget):
    WIDGET_NAME = "System Updates"

    def __init__(self, parent=None):
        # checkupdates is Arch Linux specific for checking pacman without root
        super().__init__(["checkupdates"], parent)
        self.set_update_interval(3600000) # Update every hour

    def _handle_success(self, output: str):
        count = len([line for line in output.split('\n') if line.strip()])
        if count > 0:
            self.set_text(f"📦 {count} Updates")
        else:
            self.set_text("📦 Up to date")

    def _handle_error(self, err: str):
        # checkupdates returns exit code 2 if there are no updates, which triggers error callback
        self.set_text("📦 Up to date")
