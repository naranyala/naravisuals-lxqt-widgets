import subprocess
import os
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from naravisuals.core.base_widget import IconTextWidget

class AppMenuWidget(IconTextWidget):
    WIDGET_NAME = "Application Menu"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(0)
        self.set_content("Menu", "🪟")
        self.menu = QMenu(self)
        
        # MVP: Launching a few hardcoded shortcuts
        term = QAction("Terminal", self)
        term.triggered.connect(lambda: subprocess.Popen(["x-terminal-emulator"]))
        
        browser = QAction("Web Browser", self)
        browser.triggered.connect(lambda: subprocess.Popen(["xdg-open", "http://google.com"]))
        
        files = QAction("File Manager", self)
        files.triggered.connect(lambda: subprocess.Popen(["xdg-open", os.path.expanduser("~")]))
        
        self.menu.addAction(term)
        self.menu.addAction(browser)
        self.menu.addAction(files)

    def mousePressEvent(self, event):
        self.menu.popup(event.globalPosition().toPoint())
