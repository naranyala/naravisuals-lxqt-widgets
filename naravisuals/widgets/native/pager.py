from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget
import subprocess
from naravisuals.core.base_widget import PanelWidget
from naravisuals.core.async_utils import run_async_command

class DesktopPagerWidget(PanelWidget):
    WIDGET_NAME = "Desktop Pager"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000)
        
        # Horizontal layout for the squares
        QWidget().setLayout(self.layout()) # Clear vertical layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        
        self.buttons = []

    def _on_tick(self):
        # Use wmctrl -d to get desktops
        run_async_command(["wmctrl", "-d"], self._parse_desktops)

    def _parse_desktops(self, output: str):
        lines = output.strip().split('\n')
        # Rebuild buttons if desktop count changed
        if len(lines) != len(self.buttons):
            for b in self.buttons:
                b.deleteLater()
            self.buttons.clear()
            for line in lines:
                parts = line.split()
                if not parts: continue
                d_id = parts[0]
                btn = QPushButton(d_id)
                btn.setFixedSize(20, 20)
                btn.clicked.connect(lambda checked, idx=d_id: subprocess.Popen(["wmctrl", "-s", idx]))
                self._layout.addWidget(btn)
                self.buttons.append(btn)
                
        # Highlight active
        for i, line in enumerate(lines):
            if "*" in line:
                self.buttons[i].setStyleSheet("background-color: #0082fc; color: white;")
            else:
                self.buttons[i].setStyleSheet("")
