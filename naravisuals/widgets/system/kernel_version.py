from naravisuals.core.base_widget import AsyncCommandWidget

class KernelVersion(AsyncCommandWidget):
    WIDGET_NAME = "Kernel Version"

    def __init__(self, parent=None):
        super().__init__(["uname", "-r"], parent)
        # Update interval 0 means it will only tick once when the widget starts
        self.set_update_interval(0) 

    def _handle_success(self, output: str):
        self.set_text(f"🐧 {output}")
