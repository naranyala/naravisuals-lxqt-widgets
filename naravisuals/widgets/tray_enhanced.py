from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QMenu

from naravisuals.base import PanelWidget


class TrayEnhanced(PanelWidget):
    WIDGET_NAME = "Tray Enhanced"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(1000)

        self._tray = None
        self._enabled = False

        self._status_label = QLabel("System Tray: Standalone")
        self._status_label.setStyleSheet("font-size: 11px; color: #aaa;")
        self._layout.addWidget(self._status_label)

        info = QLabel("This widget runs outside\nthe panel as a tray icon.\nUse it with Custom Command.")
        info.setStyleSheet("font-size: 10px; color: #666; padding: 4px;")
        self._layout.addWidget(info)
        self._layout.addStretch()

        self.add_action("Show Tray Icon", self._toggle_tray)
        self.add_action("Quit", QApplication.quit)

    def _toggle_tray(self):
        if self._tray:
            self._tray.hide()
            self._tray = None
            self._status_label.setText("System Tray: Hidden")
            self._enabled = False
        else:
            self._tray = QSystemTrayIcon(QIcon.fromTheme("emblem-system"), self)
            self._tray.setToolTip("NaraVisuals Tray")
            menu = QMenu()
            quit_action = menu.addAction("Quit")
            quit_action.triggered.connect(QApplication.quit)
            self._tray.setContextMenu(menu)
            self._tray.show()
            self._status_label.setText("System Tray: Active")
            self._enabled = True

    def _on_tick(self):
        pass


if __name__ == "__main__":
    TrayEnhanced.launch_standalone()
