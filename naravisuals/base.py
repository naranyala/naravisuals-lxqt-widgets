import sys

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication, QMenu


class PanelWidget(QWidget):
    WIDGET_NAME = "PanelWidget"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._interval = 1000
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.setSpacing(2)
        self.setLayout(self._layout)
        self._menu = None
        self._actions = []

    def set_update_interval(self, ms: int):
        self._interval = max(100, ms)

    def start(self):
        self._on_tick()
        if self._interval > 0:
            self._timer.start(self._interval)

    def stop(self):
        self._timer.stop()

    def _on_tick(self):
        pass

    def add_action(self, text: str, callback, icon=None):
        action = QAction(text, self)
        if icon:
            action.setIcon(QIcon.fromTheme(icon))
        action.triggered.connect(callback)
        self._actions.append(action)
        return action

    def contextMenuEvent(self, event):
        if self._actions:
            if self._menu is None:
                self._menu = QMenu(self)
            self._menu.clear()
            for a in self._actions:
                self._menu.addAction(a)
            self._menu.exec(event.globalPos())

    @classmethod
    def launch_standalone(cls):
        app = QApplication(sys.argv)
        w = cls()
        w.setWindowTitle(cls.WIDGET_NAME)

        args = sys.argv[1:]
        embed_mode = "--embed" in args
        panel_mode = ("--panel" in args or "-p" in args) and not embed_mode

        if embed_mode:
            w.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            w.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            w.setStyleSheet("background: transparent;")
            w.show()
            w.start()
            app.processEvents()
            wid = int(w.winId())
            print(f"WID:{wid:x}", flush=True)
            sys.exit(app.exec())
            return

        if panel_mode:
            w.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
            )
            w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            w.setStyleSheet("background-color: #2d2d2d; border: 1px solid #555;")

            try:
                idx = args.index("--position") if "--position" in args else args.index("-pos")
                pos = args[idx + 1]
                parts = pos.replace("+", " ").split()
                x, y = int(parts[0]), int(parts[1])
                w.move(x, y)
            except (ValueError, IndexError):
                pass

            try:
                idx = args.index("--width") if "--width" in args else args.index("-w")
                width = int(args[idx + 1])
                w.setFixedWidth(width)
            except (ValueError, IndexError):
                pass

        w.show()
        w.start()
        sys.exit(app.exec())
