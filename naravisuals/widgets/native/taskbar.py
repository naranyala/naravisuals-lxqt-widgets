from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget
from PyQt6.QtCore import Qt
import subprocess
from naravisuals.core.base_widget import PanelWidget
from naravisuals.core.async_utils import run_async_command

class TaskbarWidget(PanelWidget):
    WIDGET_NAME = "Taskbar"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000)
        
        QWidget().setLayout(self.layout()) # Clear vertical layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(2, 0, 2, 0)
        self._layout.setSpacing(4)
        
        self.buttons = []

    def _on_tick(self):
        # Uses wmctrl to list all managed X11 windows
        run_async_command(["wmctrl", "-l"], self._parse_windows)

    def _parse_windows(self, output: str):
        lines = output.strip().split('\n')
        
        for b in self.buttons:
            b.deleteLater()
        self.buttons.clear()
        
        for line in lines:
            parts = line.split(maxsplit=3)
            if len(parts) < 4: continue
            win_id = parts[0]
            title = parts[3][:20] + "..." if len(parts[3]) > 20 else parts[3]
            
            btn = QPushButton(title)
            btn.setFlat(True)
            # Clicking focuses the window using its X11 ID
            btn.clicked.connect(lambda checked, w=win_id: subprocess.Popen(["wmctrl", "-i", "-a", w]))
            self._layout.addWidget(btn)
            self.buttons.append(btn)
            
        self._layout.addStretch()
