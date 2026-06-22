import sys
import importlib
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea
from PyQt6.QtCore import Qt


WIDGETS = {
    "1": ("System Monitor", "naravisuals.widgets.system_monitor", "SystemMonitor"),
    "2": ("Weather", "naravisuals.widgets.weather", "WeatherWidget"),
    "3": ("Quick Notes", "naravisuals.widgets.quick_notes", "QuickNotes"),
    "4": ("Clipboard Manager", "naravisuals.widgets.clipboard_manager", "ClipboardManager"),
    "5": ("Pomodoro Timer", "naravisuals.widgets.pomodoro", "PomodoroTimer"),
    "6": ("Network Monitor", "naravisuals.widgets.network_monitor", "NetworkMonitor"),
    "7": ("Tray Enhanced", "naravisuals.widgets.tray_enhanced", "TrayEnhanced"),
    "8": ("Media Player", "naravisuals.widgets.media_player", "MediaPlayerController"),
    "9": ("Battery Info", "naravisuals.widgets.battery", "BatteryInfo"),
}


class ManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NaraVisuals LXQt Widgets")
        self.setGeometry(100, 100, 500, 400)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self._widgets = {}

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self._grid = QVBoxLayout(container)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        for key, (name, mod_path, cls_name) in WIDGETS.items():
            row = QHBoxLayout()
            btn = QPushButton(f"Launch {name}")
            btn.clicked.connect(lambda checked, k=key, m=mod_path, c=cls_name, n=name: self._launch(k, m, c, n))
            row.addWidget(btn)
            self._grid.addLayout(row)

    def _launch(self, key, mod_path, cls_name, name):
        if key in self._widgets and self._widgets[key].isVisible():
            self._widgets[key].raise_()
            self._widgets[key].activateWindow()
            return
        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name)
        w = cls()
        w.setWindowTitle(name)
        w.resize(300, 100)
        w.show()
        w.start()
        self._widgets[key] = w


def main():
    app = QApplication(sys.argv)
    win = ManagerWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
