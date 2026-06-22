from PyQt6.QtWidgets import QLabel
from naravisuals.core.base_widget import PanelWidget

class SystemTrayWidget(PanelWidget):
    WIDGET_NAME = "System Tray"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(0)
        # MVP: Rendering a mock system tray.
        # True StatusNotifierItem implementation requires pydbus and deep DBus integration
        label = QLabel("📥 [System Tray Mock]")
        self._layout.addWidget(label)
