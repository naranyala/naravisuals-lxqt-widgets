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
            
            # Apply dynamic theming from QPalette instead of hardcoded colors
            palette = app.palette()
            bg_color = palette.color(palette.ColorRole.Window).name()
            border_color = palette.color(palette.ColorRole.WindowText).name()
            w.setStyleSheet(f"background-color: {bg_color}; border: 1px solid {border_color};")

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


# --- Enriched Foundation Widgets ---

from PyQt6.QtWidgets import QLabel, QHBoxLayout
from naravisuals.core.async_utils import get_text_color, run_async_command

class TextWidget(PanelWidget):
    """A foundation widget that displays simple, configurable text."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        color = get_text_color()
        self.label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self._layout.addWidget(self.label)

    def set_text(self, text: str):
        self.label.setText(text)


class IconTextWidget(PanelWidget):
    """A foundation widget that displays an icon next to text."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Replace the vertical layout with horizontal
        QWidget().setLayout(self.layout()) # Clear old layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 2, 4, 2)
        self._layout.setSpacing(6)
        
        self.icon_label = QLabel()
        self.text_label = QLabel()
        
        color = get_text_color()
        self.text_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        self._layout.addWidget(self.icon_label)
        self._layout.addWidget(self.text_label)
        self._layout.addStretch()

    def set_content(self, text: str, icon_char: str = ""):
        self.text_label.setText(text)
        if icon_char:
            self.icon_label.setText(icon_char)


class AsyncCommandWidget(TextWidget):
    """A foundation widget that runs a shell command asynchronously every tick."""
    def __init__(self, command: list[str], parent=None):
        super().__init__(parent)
        self.command = command

    def _on_tick(self):
        run_async_command(
            self.command,
            on_success_cb=self._handle_success,
            on_error_cb=self._handle_error
        )

    def _handle_success(self, output: str):
        """Override this to parse the output and call self.set_text()"""
        self.set_text(output)

    def _handle_error(self, err: str):
        self.set_text("Error")

