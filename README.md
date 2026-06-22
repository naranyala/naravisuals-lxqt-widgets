# NaraVisuals LXQt Widgets - Codebase

This README contains the exposed source code for the project.

## `install.sh`

```bash
#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"
PANEL_PLUGIN_DIR="${HOME}/.local/share/lxqt/lxqt-panel"
AUTOSTART_DIR="${HOME}/.config/autostart"

echo "==> Installing NaraVisuals LXQt Widgets..."
echo ""

mkdir -p "$BIN_DIR" "$APP_DIR" "$PANEL_PLUGIN_DIR" "$AUTOSTART_DIR"

cp -r "$PROJECT_DIR/naravisuals" "$BIN_DIR/"

cat > "$BIN_DIR/naravisuals-manager" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.panel_plugin "$@"
SCRIPT
chmod +x "$BIN_DIR/naravisuals-manager"

for widget in system-monitor weather quick-notes clipboard-manager pomodoro network-monitor tray-enhanced media-player battery; do
    name="naravisuals-${widget}"
    cat > "$BIN_DIR/$name" << SCRIPT
#!/usr/bin/env bash
exec python3 -m naravisuals.widgets ${widget} "\$@"
SCRIPT
    chmod +x "$BIN_DIR/$name"
done

for f in "$PROJECT_DIR/desktop/naravisuals-"*.desktop; do
    name=$(basename "$f")
    cp "$f" "$APP_DIR/$name"
done

echo "  Launcher scripts:  $BIN_DIR"
echo "  Desktop files:     $APP_DIR"
echo ""

echo "==> Creating autostart entries (launch with --panel mode)..."
for widget in system-monitor weather network-monitor battery; do
    name="naravisuals-${widget}"
    cat > "$AUTOSTART_DIR/${name}.desktop" << AUTOSTART
[Desktop Entry]
Type=Application
Name=NaraVisuals ${widget}
Exec=${name} --panel
Terminal=false
X-LXQt-Needs=Panel
AUTOSTART
    echo "  + Autostart: ${widget}"
done

echo ""
echo "==> Updating desktop database..."
update-desktop-database "$APP_DIR" 2>/dev/null || true

echo ""
echo "==> Installation complete!"
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  NaraVisuals LXQt Widgets are ready!"
echo ""
echo "  TO ADD TO PANEL (LXQt GUI method):"
echo "  1. Right-click on the LXQt panel → 'Add Widgets...'"
echo "  2. Or right-click → 'Panel Settings' → 'Widgets' tab"
echo "  3. Look for 'NaraVisuals' entries in the list"
echo ""
echo "  TO ADD VIA QUICK LAUNCH:"
echo "  1. Right-click panel → 'Add Widgets...' → 'Quick Launch'"
echo "  2. Right-click the Quick Launch area → 'Preferences'"
echo "  3. Click 'Add' and find NaraVisuals entries in the menu"
echo ""
echo "  STANDALONE LAUNCH:"
echo "    naravisuals-manager           - Widget manager"
echo "    naravisuals-system-monitor    - CPU/RAM/Disk/SWAP"
echo "    naravisuals-weather           - Weather info"
echo "    naravisuals-quick-notes       - Sticky notes"
echo "    naravisuals-clipboard-manager - Clipboard history"
echo "    naravisuals-pomodoro          - Timer"
echo "    naravisuals-network-monitor   - Traffic graph"
echo "    naravisuals-tray-enhanced     - Tray management"
echo "    naravisuals-media-player      - MPRIS control"
echo "    naravisuals-battery           - Battery status"
echo ""
echo "  PANEL MODE (frameless, always-on-top):"
echo "    naravisuals-weather --panel --position 1800+30 --width 200"
echo ""
echo "  REMOVE: naravisuals-remove"
echo "──────────────────────────────────────────────────────────────"
```

## `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name="naravisuals-lxqt-widgets",
    version="1.0.0",
    description="Custom LXQt panel widgets written in Python/PyQt6",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5",
        "psutil>=5.8",
        "requests>=2.25",
        "dbus-python>=1.2",
        "notify2>=0.3",
    ],
    python_requires=">=3.10",
)
```

## `desktop/naravisuals-battery.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Battery Info
Comment=Enhanced battery status with custom icon
Icon=battery
Categories=Hardware;LXQt;
Exec=naravisuals-battery
Terminal=false
```

## `desktop/naravisuals-clipboard-manager.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Clipboard Manager
Comment=Clipboard history manager
Icon=edit-copy
Categories=Utility;LXQt;
Exec=naravisuals-clipboard-manager
Terminal=false
```

## `desktop/naravisuals-manager.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Widget Manager
Comment=Launch and manage all NaraVisuals LXQt widgets
Icon=utilities-system-monitor
Categories=Utility;LXQt;
Exec=naravisuals-manager
Terminal=false
```

## `desktop/naravisuals-media-player.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Media Player
Comment=Control MPRIS-compatible media players
Icon=multimedia-player
Categories=AudioVideo;LXQt;
Exec=naravisuals-media-player
Terminal=false
```

## `desktop/naravisuals-network-monitor.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Network Monitor
Comment=Real-time network traffic graph
Icon=network-wired
Categories=System;Monitor;LXQt;
Exec=naravisuals-network-monitor
Terminal=false
```

## `desktop/naravisuals-pomodoro.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Pomodoro Timer
Comment=Pomodoro productivity timer
Icon=alarm-clock
Categories=Utility;LXQt;
Exec=naravisuals-pomodoro
Terminal=false
```

## `desktop/naravisuals-quick-notes.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Quick Notes
Comment=Quick sticky notes manager
Icon=accessories-text-editor
Categories=Utility;LXQt;
Exec=naravisuals-quick-notes
Terminal=false
```

## `desktop/naravisuals-system-monitor.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals System Monitor
Comment=CPU, RAM, Disk, SWAP usage bars with network speed
Icon=utilities-system-monitor
Categories=System;Monitor;LXQt;
Exec=naravisuals-system-monitor
Terminal=false
```

## `desktop/naravisuals-tray-enhanced.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Tray Enhanced
Comment=Enhanced system tray with extra features
Icon=emblem-system
Categories=Utility;LXQt;
Exec=naravisuals-tray-enhanced
Terminal=false
```

## `desktop/naravisuals-weather.desktop`

```ini
[Desktop Entry]
Type=Application
Name=NaraVisuals Weather
Comment=Current weather conditions for your city
Icon=weather-clear
Categories=Utility;LXQt;
Exec=naravisuals-weather
Terminal=false
```

## `desktop-panel/naravisuals-battery.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=battery
Name=Battery Info
Comment=Enhanced battery status with custom icon
```

## `desktop-panel/naravisuals-clipboard-manager.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=edit-copy
Name=Clipboard Manager
Comment=Clipboard history manager
```

## `desktop-panel/naravisuals-media-player.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=multimedia-player
Name=Media Player
Comment=Control MPRIS-compatible media players
```

## `desktop-panel/naravisuals-network-monitor.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=network-wired
Name=Network Monitor
Comment=Real-time network traffic graph
```

## `desktop-panel/naravisuals-pomodoro.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=alarm-clock
Name=Pomodoro Timer
Comment=Pomodoro productivity timer
```

## `desktop-panel/naravisuals-quick-notes.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=accessories-text-editor
Name=Quick Notes
Comment=Quick sticky notes manager
```

## `desktop-panel/naravisuals-system-monitor.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=utilities-system-monitor
Name=System Monitor
Comment=CPU, RAM, Disk, SWAP usage bars with network speed
```

## `desktop-panel/naravisuals-tray-enhanced.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=emblem-system
Name=Tray Enhanced
Comment=Enhanced system tray with extra features
```

## `desktop-panel/naravisuals-weather.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=weather-clear
Name=Weather
Comment=Current weather conditions for your city
```

## `desktop-panel/naravisuals.desktop`

```ini
[Desktop Entry]
Type=Service
ServiceTypes=LXQtPanel/Plugin
Icon=utilities-system-monitor
Name=NaraVisuals Widget (selectable)
Comment=Select and embed any NaraVisuals Python widget
```

## `naravisuals/__init__.py`

```python

```

## `naravisuals/base.py`

```python
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
```

## `naravisuals/panel_plugin.py`

```python
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
```

## `naravisuals/widgets/__init__.py`

```python
from .system_monitor import SystemMonitor
from .weather import WeatherWidget
from .quick_notes import QuickNotes
from .clipboard_manager import ClipboardManager
from .pomodoro import PomodoroTimer
from .network_monitor import NetworkMonitor
from .tray_enhanced import TrayEnhanced
from .media_player import MediaPlayerController
from .battery import BatteryInfo
```

## `naravisuals/widgets/__main__.py`

```python
import sys
from naravisuals.widgets import (
    SystemMonitor, WeatherWidget, QuickNotes, ClipboardManager,
    PomodoroTimer, NetworkMonitor, TrayEnhanced, MediaPlayerController, BatteryInfo
)

WIDGET_MAP = {
    "system-monitor": SystemMonitor,
    "weather": WeatherWidget,
    "quick-notes": QuickNotes,
    "clipboard-manager": ClipboardManager,
    "pomodoro": PomodoroTimer,
    "network-monitor": NetworkMonitor,
    "tray-enhanced": TrayEnhanced,
    "media-player": MediaPlayerController,
    "battery": BatteryInfo,
}

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print("Usage: python3 -m naravisuals.widgets <widget-name> [options]")
    print("")
    print("Widgets:", ", ".join(sorted(WIDGET_MAP)))
    print("")
    print("Options:")
    print("  --panel, -p          Frameless, always-on-top mode")
    print("  --position X+Y       Screen position (e.g. 1800+30)")
    print("  --width N            Fixed width in pixels")
    print("  --embed              Embedded panel widget mode (for native plugin)")
    sys.exit(0 if sys.argv[1] in ("-h", "--help") else 1)

name = sys.argv[1]
cls = WIDGET_MAP.get(name)
if not cls:
    print(f"Unknown widget: {name}")
    sys.exit(1)

sys.argv = [sys.argv[0]] + sys.argv[2:]
cls.launch_standalone()
```

## `naravisuals/widgets/battery.py`

```python
import psutil
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from naravisuals.base import PanelWidget


class BatteryIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._charging = False
        self.setMinimumSize(40, 24)
        self.setMaximumSize(80, 30)

    def set_values(self, percent, charging):
        self._percent = percent
        self._charging = charging
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w = self.width()
        h = self.height()
        bw = w - 6
        bh = h - 4

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor(46, 204, 113)
        if self._percent < 20:
            color = QColor(231, 76, 60)
        elif self._percent < 40:
            color = QColor(241, 196, 15)

        p.setPen(QPen(QColor(200, 200, 200), 1))
        p.drawRect(2, 2, bw, bh)
        p.fillRect(4, 4, bw - 4, bh - 4, QColor(30, 30, 30))
        fill_w = int((bw - 4) * self._percent / 100.0)
        p.fillRect(4, 4, fill_w, bh - 4, color)

        tip_x = bw + 3
        tip_y = h // 2 - 3
        p.fillRect(tip_x, tip_y, 4, 6, QColor(200, 200, 200))

        if self._charging:
            p.setPen(QColor(255, 255, 255))
            p.drawText(4, 2, bw - 4, bh - 4, Qt.AlignmentFlag.AlignCenter, "⚡")

        p.setPen(QColor(200, 200, 200))
        p.drawText(4, 2, bw - 4, bh - 4, Qt.AlignmentFlag.AlignCenter, f"{self._percent}%")


class BatteryInfo(PanelWidget):
    WIDGET_NAME = "Battery Info"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(5000)

        self._icon = BatteryIcon()
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("font-size: 9px; color: #888;")
        self._time_label = QLabel("")
        self._time_label.setStyleSheet("font-size: 9px; color: #666;")

        row = QHBoxLayout()
        row.addWidget(self._icon)
        right = QVBoxLayout()
        right.addWidget(self._status_label)
        right.addWidget(self._time_label)
        right.addStretch()
        row.addLayout(right)
        row.addStretch()
        self._layout.addLayout(row)

        self.add_action("Refresh", self._on_tick)

    def _on_tick(self):
        try:
            batt = psutil.sensors_battery()
            if batt:
                percent = int(batt.percent)
                charging = batt.power_plugged
                self._icon.set_values(percent, charging)
                status = "Charging" if charging else "Discharging"
                self._status_label.setText(f"{status}")
                secs_left = batt.secsleft
                if secs_left > 0 and not charging:
                    h = secs_left // 3600
                    m = (secs_left % 3600) // 60
                    self._time_label.setText(f"{h}h {m}m remaining")
                elif charging:
                    self._time_label.setText("Plugged in")
                else:
                    self._time_label.setText("")
            else:
                self._status_label.setText("No battery")
        except Exception:
            self._status_label.setText("Error")


if __name__ == "__main__":
    BatteryInfo.launch_standalone()
```

## `naravisuals/widgets/clipboard_manager.py`

```python
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QHBoxLayout, QPushButton, QLabel

from naravisuals.base import PanelWidget


class ClipboardManager(PanelWidget):
    WIDGET_NAME = "Clipboard Manager"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(500)
        self._history = []
        self._max_items = 50
        self._last_text = ""

        self._list = QListWidget()
        self._list.itemClicked.connect(self._copy_item)
        self._layout.addWidget(QLabel("Clipboard History"))
        self._layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_history)
        btn_row.addStretch()
        btn_row.addWidget(clear_btn)
        self._layout.addLayout(btn_row)

        self._clip = QApplication.clipboard()

    def _on_tick(self):
        try:
            text = self._clip.text()
            if text and text != self._last_text:
                self._last_text = text
                if not self._history or self._history[0] != text:
                    self._history.insert(0, text)
                    if len(self._history) > self._max_items:
                        self._history.pop()
                    self._refresh_list()
        except Exception:
            pass

    def _refresh_list(self):
        self._list.clear()
        for item in self._history[:20]:
            display = item[:80].replace('\n', ' ')
            li = QListWidgetItem(display)
            li.setToolTip(item)
            self._list.addItem(li)

    def _copy_item(self, item):
        self._clip.setText(item.toolTip())

    def _clear_history(self):
        self._history.clear()
        self._list.clear()


if __name__ == "__main__":
    ClipboardManager.launch_standalone()
```

## `naravisuals/widgets/media_player.py`

```python
import dbus
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QSlider

from naravisuals.base import PanelWidget


class MediaPlayerController(PanelWidget):
    WIDGET_NAME = "Media Player"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000)
        self._player_name = None

        self._title_label = QLabel("No track")
        self._title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #eee;")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._artist_label = QLabel("")
        self._artist_label.setStyleSheet("font-size: 10px; color: #888;")
        self._artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._pos_slider = QSlider(Qt.Orientation.Horizontal)
        self._pos_slider.setRange(0, 100)
        self._pos_slider.setEnabled(False)

        btn_row = QHBoxLayout()
        self._prev_btn = QPushButton("⏮")
        self._prev_btn.clicked.connect(self._prev)
        self._play_btn = QPushButton("⏯")
        self._play_btn.clicked.connect(self._play_pause)
        self._next_btn = QPushButton("⏭")
        self._next_btn.clicked.connect(self._next)
        btn_row.addStretch()
        btn_row.addWidget(self._prev_btn)
        btn_row.addWidget(self._play_btn)
        btn_row.addWidget(self._next_btn)
        btn_row.addStretch()

        self._layout.addWidget(self._title_label)
        self._layout.addWidget(self._artist_label)
        self._layout.addWidget(self._pos_slider)
        self._layout.addLayout(btn_row)

        self.add_action("Refresh Player", self._find_player)

    def _on_tick(self):
        self._update_info()

    def _get_bus(self):
        try:
            return dbus.SessionBus()
        except Exception:
            return None

    def _find_player(self):
        bus = self._get_bus()
        if not bus:
            return None
        try:
            names = bus.list_names()
            for name in names:
                if "player" in name.lower() or "mpris" in name.lower():
                    if "org.mpris.MediaPlayer2" in name:
                        self._player_name = name
                        return name
        except Exception:
            pass

        for prefix in ["org.mpris.MediaPlayer2."]:
            try:
                obj = bus.get_object(prefix + "spotify", "/org/mpris/MediaPlayer2")
                self._player_name = prefix + "spotify"
                return self._player_name
            except Exception:
                pass
            for p in ["vlc", "audacious", "clementine", "rhythmbox", "firefox"]:
                try:
                    obj = bus.get_object(prefix + p, "/org/mpris/MediaPlayer2")
                    self._player_name = prefix + p
                    return self._player_name
                except Exception:
                    pass
        return None

    def _get_player_iface(self):
        bus = self._get_bus()
        if not bus:
            return None
        name = self._player_name
        if not name:
            name = self._find_player()
        if not name:
            return None
        try:
            return dbus.Interface(
                bus.get_object(name, "/org/mpris/MediaPlayer2"),
                "org.freedesktop.DBus.Properties"
            )
        except Exception:
            return None

    def _update_info(self):
        iface = self._get_player_iface()
        if not iface:
            self._title_label.setText("No player detected")
            self._artist_label.setText("")
            return
        try:
            meta = iface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            status = iface.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
            title = meta.get("xesam:title", "Unknown")
            artist = ", ".join(meta.get("xesam:artist", ["Unknown"]))
            length = meta.get("mpris:length", 0) / 1000000
            pos = iface.Get("org.mpris.MediaPlayer2.Player", "Position") / 1000000
            self._title_label.setText(title)
            self._artist_label.setText(artist)
            if length > 0:
                self._pos_slider.setRange(0, int(length))
                self._pos_slider.setValue(int(pos))
            self._play_btn.setText("⏸" if status == "Playing" else "▶")
        except Exception:
            pass

    def _play_pause(self):
        self._send_cmd("PlayPause")

    def _next(self):
        self._send_cmd("Next")

    def _prev(self):
        self._send_cmd("Previous")

    def _send_cmd(self, method):
        bus = self._get_bus()
        name = self._player_name
        if not name:
            name = self._find_player()
        if not name:
            return
        try:
            iface = dbus.Interface(
                bus.get_object(name, "/org/mpris/MediaPlayer2"),
                "org.mpris.MediaPlayer2.Player"
            )
            iface.__getattr__(method)()
        except Exception:
            pass


if __name__ == "__main__":
    MediaPlayerController.launch_standalone()
```

## `naravisuals/widgets/network_monitor.py`

```python
import psutil
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from naravisuals.base import PanelWidget


class NetGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._points = [0] * 60
        self._max_val = 1
        self.setMinimumHeight(50)

    def add_value(self, val):
        self._points.append(val)
        if len(self._points) > 60:
            self._points.pop(0)
        self._max_val = max(max(self._points), 1)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w = self.width()
        h = self.height()
        p.fillRect(0, 0, w, h, QColor(20, 20, 20))
        if not self._points:
            return
        step = w / 60.0
        pen = QPen(QColor(46, 204, 113))
        pen.setWidth(2)
        p.setPen(pen)
        for i in range(1, len(self._points)):
            x1 = int((i - 1) * step)
            y1 = int(h - (self._points[i - 1] / self._max_val * h))
            x2 = int(i * step)
            y2 = int(h - (self._points[i] / self._max_val * h))
            p.drawLine(x1, y1, x2, y2)


class NetworkMonitor(PanelWidget):
    WIDGET_NAME = "Network Monitor"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000)

        self._down_label = QLabel("⬇ 0 B/s")
        self._down_label.setStyleSheet("font-size: 10px; color: #3498db;")
        self._up_label = QLabel("⬆ 0 B/s")
        self._up_label.setStyleSheet("font-size: 10px; color: #e67e22;")
        self._graph = NetGraph()

        stats_row = QHBoxLayout()
        stats_row.addWidget(self._down_label)
        stats_row.addWidget(self._up_label)
        stats_row.addStretch()

        self._layout.addLayout(stats_row)
        self._layout.addWidget(self._graph)

        self._last_recv = psutil.net_io_counters().bytes_recv
        self._last_sent = psutil.net_io_counters().bytes_sent

        self._interfaces_label = QLabel("")
        self._interfaces_label.setStyleSheet("font-size: 9px; color: #666;")
        self._layout.addWidget(self._interfaces_label)

    def _on_tick(self):
        counters = psutil.net_io_counters()
        now_recv = counters.bytes_recv
        now_sent = counters.bytes_sent
        down = now_recv - self._last_recv
        up = now_sent - self._last_sent
        self._last_recv = now_recv
        self._last_sent = now_sent

        self._down_label.setText(f"⬇ {self._format(down)}/s")
        self._up_label.setText(f"⬆ {self._format(up)}/s")
        self._graph.add_value(down)

        ifcs = psutil.net_if_stats()
        active = [k for k, v in ifcs.items() if v.isup]
        self._interfaces_label.setText(", ".join(active[:3]))

    @staticmethod
    def _format(b):
        for unit in ('B', 'KB', 'MB', 'GB'):
            if b < 1024:
                return f"{b:.1f}{unit}"
            b /= 1024
        return f"{b:.1f}TB"


if __name__ == "__main__":
    NetworkMonitor.launch_standalone()
```

## `naravisuals/widgets/pomodoro.py`

```python
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QSpinBox, QFrame

from naravisuals.base import PanelWidget


class PomodoroTimer(PanelWidget):
    WIDGET_NAME = "Pomodoro Timer"
    WORK_MIN = 25
    BREAK_MIN = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(1000)
        self._state = "idle"
        self._seconds_left = self.WORK_MIN * 60
        self._is_work = True
        self._pomodoro_count = 0

        self._time_label = QLabel(self._format_time(self._seconds_left))
        self._time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #e74c3c;")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet("font-size: 11px; color: #888;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._count_label = QLabel("🍅 0")
        self._count_label.setStyleSheet("font-size: 10px; color: #666;")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        control_row = QHBoxLayout()
        self._start_btn = QPushButton("Start")
        self._start_btn.clicked.connect(self._toggle)
        self._reset_btn = QPushButton("Reset")
        self._reset_btn.clicked.connect(self._reset)
        self._work_spin = QSpinBox()
        self._work_spin.setRange(1, 60)
        self._work_spin.setValue(self.WORK_MIN)
        self._work_spin.setSuffix("m work")
        self._work_spin.valueChanged.connect(self._update_work)
        control_row.addWidget(self._start_btn)
        control_row.addWidget(self._reset_btn)
        control_row.addWidget(self._work_spin)
        control_row.addStretch()

        self._layout.addWidget(self._time_label)
        self._layout.addWidget(self._status_label)
        self._layout.addWidget(self._count_label)
        self._layout.addLayout(control_row)

    def _format_time(self, secs):
        m = secs // 60
        s = secs % 60
        return f"{m:02d}:{s:02d}"

    def _update_work(self, val):
        if self._state == "idle":
            self.WORK_MIN = val
            self._seconds_left = val * 60
            self._time_label.setText(self._format_time(self._seconds_left))

    def _on_tick(self):
        if self._state == "running":
            self._seconds_left -= 1
            self._time_label.setText(self._format_time(self._seconds_left))
            if self._seconds_left <= 0:
                self._switch_phase()

    def _switch_phase(self):
        self._is_work = not self._is_work
        if self._is_work:
            self._seconds_left = self.WORK_MIN * 60
            self._status_label.setText("Work time!")
            self._time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #e74c3c;")
        else:
            self._seconds_left = self.BREAK_MIN * 60
            self._status_label.setText("Break time! 🎉")
            self._time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2ecc71;")
            self._pomodoro_count += 1
            self._count_label.setText(f"🍅 {self._pomodoro_count}")

    def _toggle(self):
        if self._state == "running":
            self._state = "paused"
            self._start_btn.setText("Resume")
        elif self._state == "paused":
            self._state = "running"
            self._start_btn.setText("Pause")
        else:
            self._state = "running"
            self._start_btn.setText("Pause")
            self._status_label.setText("Work time!")

    def _reset(self):
        self._state = "idle"
        self._is_work = True
        self._seconds_left = self.WORK_MIN * 60
        self._time_label.setText(self._format_time(self._seconds_left))
        self._time_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #e74c3c;")
        self._status_label.setText("Ready")
        self._start_btn.setText("Start")


if __name__ == "__main__":
    PomodoroTimer.launch_standalone()
```

## `naravisuals/widgets/quick_notes.py`

```python
import json
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QSplitter, QWidget

from naravisuals.base import PanelWidget


NOTES_PATH = os.path.expanduser("~/.config/naravisuals/notes.json")


class QuickNotes(PanelWidget):
    WIDGET_NAME = "Quick Notes"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(0)
        self._notes = self._load_notes()
        self._current_title = ""

        splitter = QSplitter(Qt.Orientation.Vertical)

        top = QVBoxLayout()
        self._list = QListWidget()
        self._list.itemClicked.connect(self._on_select)
        top.addWidget(QLabel("Notes"))
        top.addWidget(self._list)

        top_w = QWidget()
        top_w.setLayout(top)
        splitter.addWidget(top_w)

        bottom = QVBoxLayout()
        self._editor = QTextEdit()
        self._editor.setPlaceholderText("Write your note here...")
        btn_row = QHBoxLayout()
        self._add_btn = QPushButton("+ New")
        self._add_btn.clicked.connect(self._add_note)
        self._save_btn = QPushButton("Save")
        self._save_btn.clicked.connect(self._save_note)
        self._del_btn = QPushButton("Delete")
        self._del_btn.clicked.connect(self._delete_note)
        btn_row.addWidget(self._add_btn)
        btn_row.addWidget(self._save_btn)
        btn_row.addWidget(self._del_btn)
        btn_row.addStretch()
        bottom.addWidget(self._editor)
        bottom.addLayout(btn_row)

        bottom_w = QWidget()
        bottom_w.setLayout(bottom)
        splitter.addWidget(bottom_w)

        self._layout.addWidget(splitter)
        self._refresh_list()

    def _load_notes(self):
        try:
            os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
            with open(NOTES_PATH) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_notes_to_disk(self):
        os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
        with open(NOTES_PATH, "w") as f:
            json.dump(self._notes, f, indent=2)

    def _refresh_list(self):
        self._list.clear()
        for title in self._notes:
            self._list.addItem(title)

    def _on_select(self, item):
        title = item.text()
        self._current_title = title
        self._editor.setPlainText(self._notes.get(title, ""))

    def _add_note(self):
        title = f"Note {len(self._notes) + 1}"
        while title in self._notes:
            title += "_"
        self._notes[title] = ""
        self._save_notes_to_disk()
        self._refresh_list()

    def _save_note(self):
        if self._current_title:
            self._notes[self._current_title] = self._editor.toPlainText()
            self._save_notes_to_disk()

    def _delete_note(self):
        if self._current_title:
            self._notes.pop(self._current_title, None)
            self._save_notes_to_disk()
            self._refresh_list()
            self._editor.clear()
            self._current_title = ""


if __name__ == "__main__":
    QuickNotes.launch_standalone()
```

## `naravisuals/widgets/system_monitor.py`

```python
import psutil
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from naravisuals.base import PanelWidget


class UsageBar(QWidget):
    def __init__(self, label, color):
        super().__init__()
        self._value = 0.0
        self._label = label
        self._color = QColor(color)
        self.setMinimumHeight(18)
        self.setMaximumHeight(18)

    def set_value(self, v):
        self._value = v
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w = self.width()
        h = self.height()
        p.fillRect(0, 0, w, h, QColor(40, 40, 40))
        fill = int(w * self._value / 100.0)
        p.fillRect(0, 0, fill, h, self._color)
        p.setPen(QColor(200, 200, 200))
        p.drawText(4, 0, w - 4, h, Qt.AlignmentFlag.AlignVCenter, f"{self._label}: {self._value:.1f}%")


class SystemMonitor(PanelWidget):
    WIDGET_NAME = "System Monitor"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000)
        
        # Override the default QVBoxLayout with QHBoxLayout
        QWidget().setLayout(self._layout) # Delete old layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)
        
        self.setMinimumHeight(18)
        
        self._cpu_bar = UsageBar("CPU", QColor(46, 204, 113))
        self._mem_bar = UsageBar("RAM", QColor(52, 152, 219))
        self._disk_bar = UsageBar("DISK", QColor(155, 89, 182))
        self._swap_bar = UsageBar("SWAP", QColor(231, 76, 60))
        self._net_label = QLabel("NET: ?")
        self._net_label.setStyleSheet("color: #aaa; font-size: 10px;")
        
        self._layout.addWidget(self._cpu_bar)
        self._layout.addWidget(self._mem_bar)
        self._layout.addWidget(self._disk_bar)
        self._layout.addWidget(self._swap_bar)
        self._layout.addWidget(self._net_label)
        self._last_net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

    def _on_tick(self):
        self._cpu_bar.set_value(psutil.cpu_percent())
        mem = psutil.virtual_memory()
        self._mem_bar.set_value(mem.percent)
        disk = psutil.disk_usage('/')
        self._disk_bar.set_value(disk.percent)
        swap = psutil.swap_memory()
        self._swap_bar.set_value(swap.percent)
        now = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        diff = now - self._last_net
        self._last_net = now
        self._net_label.setText(f"NET: {self._format_bytes(diff)}/s")

    @staticmethod
    def _format_bytes(b):
        for unit in ('B', 'KB', 'MB', 'GB'):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"


if __name__ == "__main__":
    SystemMonitor.launch_standalone()
```

## `naravisuals/widgets/tray_enhanced.py`

```python
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
```

## `naravisuals/widgets/weather.py`

```python
import json
import os
from datetime import datetime

import requests
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QLineEdit, QPushButton

from naravisuals.base import PanelWidget


CONFIG_PATH = os.path.expanduser("~/.config/naravisuals/weather.json")


class WeatherWidget(PanelWidget):
    WIDGET_NAME = "Weather"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(600000)
        self._city = self._load_city()
        self._api_key = ""

        self._icon_label = QLabel()
        self._icon_label.setStyleSheet("font-size: 28px;")
        self._info_layout = QVBoxLayout()
        self._city_label = QLabel(self._city or "No city set")
        self._city_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #eee;")
        self._temp_label = QLabel("--°C")
        self._temp_label.setStyleSheet("font-size: 11px; color: #aaa;")
        self._desc_label = QLabel("")
        self._desc_label.setStyleSheet("font-size: 10px; color: #888;")
        self._info_layout.addWidget(self._city_label)
        self._info_layout.addWidget(self._temp_label)
        self._info_layout.addWidget(self._desc_label)
        self._info_layout.addStretch()

        row = QHBoxLayout()
        row.addWidget(self._icon_label)
        row.addLayout(self._info_layout)
        self._layout.addLayout(row)

        self._setup_layout = QHBoxLayout()
        self._city_input = QLineEdit()
        self._city_input.setPlaceholderText("Enter city...")
        self._city_input.setStyleSheet("font-size: 10px;")
        self._save_btn = QPushButton("Set")
        self._save_btn.setStyleSheet("font-size: 10px;")
        self._save_btn.clicked.connect(self._save_city)
        self._setup_layout.addWidget(self._city_input)
        self._setup_layout.addWidget(self._save_btn)
        self._layout.addLayout(self._setup_layout)
        self._setup_widgets = [self._city_input, self._save_btn]

        self.add_action("Set City", self._toggle_setup)

    def _toggle_setup(self):
        vis = self._city_input.isVisible()
        for w in self._setup_widgets:
            w.setVisible(not vis)

    def _on_tick(self):
        if self._city:
            self._fetch_weather()

    def _load_city(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH) as f:
                return json.load(f).get("city", "")
        except Exception:
            return ""

    def _save_city(self):
        city = self._city_input.text().strip()
        if city:
            self._city = city
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump({"city": city}, f)
            self._city_label.setText(city)
            self._toggle_setup()
            self._fetch_weather()

    def _fetch_weather(self):
        try:
            url = f"https://wttr.in/{self._city}?format=j1"
            r = requests.get(url, timeout=5)
            data = r.json()
            cc = data["current_condition"][0]
            temp = cc["temp_C"]
            desc = cc["weatherDesc"][0]["value"]
            self._temp_label.setText(f"{temp}°C")
            self._desc_label.setText(desc)
        except Exception:
            self._temp_label.setText("--°C")
            self._desc_label.setText("offline")


if __name__ == "__main__":
    WeatherWidget.launch_standalone()
```

## `native-plugin/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(naravisuals LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Core DBus)
find_package(lxqt REQUIRED)

add_library(naravisuals MODULE
    naravisuals-plugin.cpp
)

target_link_libraries(naravisuals PRIVATE
    Qt6::Widgets
    Qt6::Core
    lxqt
)

target_include_directories(naravisuals PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

install(TARGETS naravisuals
    LIBRARY DESTINATION lib/x86_64-linux-gnu/lxqt-panel
)

install(CODE "
    set(plugin_dir \$ENV{DESTDIR}/lib/x86_64-linux-gnu/lxqt-panel)
    set(widgets system-monitor weather quick-notes clipboard-manager pomodoro network-monitor tray-enhanced media-player battery)
    foreach(widget \${widgets})
        file(CREATE_LINK libnaravisuals.so libnaravisuals-\${widget}.so SYMBOLIC)
    endforeach()
")

install(DIRECTORY ../desktop-panel/
    DESTINATION share/lxqt/lxqt-panel
    FILES_MATCHING PATTERN "*.desktop"
)
```

## `native-plugin/naravisuals-plugin.cpp`

```cpp
#include <QWidget>
#include <QDialog>
#include <QVBoxLayout>
#include <QLabel>
#include <QComboBox>
#include <QPushButton>
#include <QProcess>
#include <QWindow>
#include <QDebug>
#include <QTimer>
#include <QDir>
#include <QFileInfo>
#include <QLibrary>
#include <dlfcn.h>

#include <ilxqtpanelplugin.h>
#include <pluginsettings.h>

// Force liblxqt.so.2 into NEEDED entries
#include <LXQt/lxqttranslator.h>

static QString detectWidgetFromLibName()
{
    Dl_info info;
    if (dladdr((void*)detectWidgetFromLibName, &info) && info.dli_fname)
    {
        QFileInfo fi(info.dli_fname);
        QString base = fi.baseName();
        if (base.startsWith("lib"))
            base = base.mid(3);
        if (base == "naravisuals")
            return QString();
        QString prefix = "naravisuals-";
        if (base.startsWith(prefix))
            return base.mid(prefix.length());
    }
    return QString();
}

static QStringList allWidgets()
{
    return {
        "system-monitor", "weather", "quick-notes", "clipboard-manager",
        "pomodoro", "network-monitor", "tray-enhanced", "media-player", "battery"
    };
}

class NaraVisualsPlugin : public QObject, public ILXQtPanelPlugin
{
    Q_OBJECT

public:
    NaraVisualsPlugin(const ILXQtPanelPluginStartupInfo &info);
    ~NaraVisualsPlugin() override;

    QWidget *widget() override { return mWidget; }
    QString themeId() const override { return QStringLiteral("NaraVisuals"); }
    Flags flags() const override;
    QDialog *configureDialog() override;

private slots:
    void onProcessReadyRead();
    void onProcessFinished(int exitCode, QProcess::ExitStatus status);
    void startWidget();
    void stopWidget();

private:
    QWidget *mWidget = nullptr;
    QWidget *mContainer = nullptr;
    QProcess *mProcess = nullptr;
    QString mSelectedWidget;
    QWindow *mEmbeddedWindow = nullptr;
    bool mIsGeneric = false;
};

class NaraVisualsPluginLibrary : public QObject, public ILXQtPanelPluginLibrary
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "lxqt.org/Panel/PluginInterface/3.0")
    Q_INTERFACES(ILXQtPanelPluginLibrary)

public:
    ILXQtPanelPlugin *instance(const ILXQtPanelPluginStartupInfo &info) const override
    {
        return new NaraVisualsPlugin(info);
    }
};

// --------------------------------------------------------

NaraVisualsPlugin::NaraVisualsPlugin(const ILXQtPanelPluginStartupInfo &info)
    : QObject(nullptr)
    , ILXQtPanelPlugin(info)
{
    QString detected = detectWidgetFromLibName();
    mIsGeneric = detected.isEmpty();

    if (mIsGeneric)
        mSelectedWidget = settings()->value("widget", "system-monitor").toString();
    else
        mSelectedWidget = detected;

    mContainer = new QWidget();
    QVBoxLayout *lay = new QVBoxLayout(mContainer);
    lay->setContentsMargins(0, 0, 0, 0);
    QLabel *label = new QLabel("Starting...");
    label->setAlignment(Qt::AlignCenter);
    label->setStyleSheet("color: #888; font-size: 10px;");
    lay->addWidget(label);
    mWidget = mContainer;

    LXQt::Translator::translatePlugin(mSelectedWidget, QStringLiteral("naravisuals"));

    startWidget();
}

NaraVisualsPlugin::~NaraVisualsPlugin()
{
    stopWidget();
    delete mContainer;
}

ILXQtPanelPlugin::Flags NaraVisualsPlugin::flags() const
{
    return mIsGeneric ? Flags(HaveConfigDialog) : NoFlags;
}

QDialog *NaraVisualsPlugin::configureDialog()
{
    if (!mIsGeneric)
        return nullptr;

    QDialog *dlg = new QDialog();
    dlg->setWindowTitle("NaraVisuals Widget");

    QVBoxLayout *layout = new QVBoxLayout(dlg);
    QLabel *info = new QLabel("Select widget:");
    layout->addWidget(info);

    QComboBox *combo = new QComboBox();
    for (const QString &w : allWidgets())
    {
        QString label = w;
        combo->addItem(label.replace('-', ' '), w);
    }

    int idx = combo->findData(mSelectedWidget);
    if (idx >= 0)
        combo->setCurrentIndex(idx);
    layout->addWidget(combo);

    QPushButton *ok = new QPushButton("OK");
    connect(ok, &QPushButton::clicked, dlg, &QDialog::accept);
    layout->addWidget(ok);

    if (dlg->exec() == QDialog::Accepted)
    {
        QString newWidget = combo->currentData().toString();
        if (newWidget != mSelectedWidget)
        {
            mSelectedWidget = newWidget;
            settings()->setValue("widget", mSelectedWidget);
            settings()->sync();
            stopWidget();
            startWidget();
        }
    }
    dlg->deleteLater();
    return nullptr;
}

void NaraVisualsPlugin::startWidget()
{
    if (mProcess)
        return;

    if (mSelectedWidget.isEmpty() || !allWidgets().contains(mSelectedWidget))
    {
        qWarning("NaraVisuals: No valid widget selected");
        return;
    }

    QStringList env = QProcess::systemEnvironment();
    QString home = QDir::homePath();
    env << QString("PYTHONPATH=%1/.local/bin/naravisuals:%2/.local/lib/python3.14/site-packages").arg(home).arg(home);

    mProcess = new QProcess(this);
    mProcess->setEnvironment(env);
    mProcess->setProcessChannelMode(QProcess::MergedChannels);

    connect(mProcess, &QProcess::readyReadStandardOutput,
            this, &NaraVisualsPlugin::onProcessReadyRead);
    connect(mProcess,
            QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &NaraVisualsPlugin::onProcessFinished);

    mProcess->start("python3", {
        "-m", "naravisuals.widgets", mSelectedWidget, "--embed"
    });

    if (!mProcess->waitForStarted(3000))
    {
        qWarning("NaraVisuals: Failed to start Python process");
        QLabel *err = new QLabel("Failed to start");
        err->setStyleSheet("color: red; font-size: 9px;");
        mContainer->layout()->addWidget(err);
        return;
    }
}

void NaraVisualsPlugin::stopWidget()
{
    if (mEmbeddedWindow)
    {
        QLayout *lay = mContainer->layout();
        if (lay)
        {
            QLayoutItem *item;
            while ((item = lay->takeAt(0)))
            {
                if (item->widget()) item->widget()->deleteLater();
                delete item;
            }
        }
        mEmbeddedWindow->destroy();
        delete mEmbeddedWindow;
        mEmbeddedWindow = nullptr;
    }
    if (mProcess)
    {
        mProcess->kill();
        mProcess->waitForFinished(2000);
        delete mProcess;
        mProcess = nullptr;
    }
}

void NaraVisualsPlugin::onProcessReadyRead()
{
    QByteArray data = mProcess->readAllStandardOutput();
    QString output = QString::fromUtf8(data).trimmed();
    qDebug() << "NaraVisuals:" << output;

    if (!output.contains("WID:"))
        return;

    int start = output.indexOf("WID:") + 4;
    int end = output.indexOf('\n', start);
    if (end < 0) end = output.length();
    QString widStr = output.mid(start, end - start).trimmed();
    bool ok = false;
    WId wid = widStr.toULongLong(&ok, 16);
    if (!ok || !wid)
        return;

    qDebug() << "NaraVisuals: Embedding WId" << widStr;

    QLayout *lay = mContainer->layout();
    QLayoutItem *item;
    while ((item = lay->takeAt(0)))
    {
        if (item->widget()) item->widget()->deleteLater();
        delete item;
    }

    mEmbeddedWindow = QWindow::fromWinId(wid);
    if (!mEmbeddedWindow)
    {
        QLabel *err = new QLabel("Embed failed");
        err->setStyleSheet("color: red; font-size: 9px;");
        lay->addWidget(err);
        return;
    }

    QWidget *embedded = QWidget::createWindowContainer(mEmbeddedWindow);
    embedded->setMinimumSize(16, 16);
    lay->addWidget(embedded);
}

void NaraVisualsPlugin::onProcessFinished(int exitCode, QProcess::ExitStatus status)
{
    qDebug() << "NaraVisuals: Process exited" << exitCode << status;
    if (status == QProcess::CrashExit)
        QTimer::singleShot(2000, this, &NaraVisualsPlugin::startWidget);
}

#include "naravisuals-plugin.moc"
```

## `scripts/install-plugin.sh`

```bash
#!/usr/bin/env bash
set -e

PLUGIN_DIR="/usr/lib/x86_64-linux-gnu/lxqt-panel"
DESKTOP_DIR="/usr/share/lxqt/lxqt-panel"
NATIVE_BUILD="/media/naranyala/Data/projects-remote/naravisuals-lxqt-widgets/native-plugin/build"

echo "==> Installing NaraVisuals native LXQt panel plugin..."
echo ""

# Install the main .so
cp "$NATIVE_BUILD/libnaravisuals.so" "$PLUGIN_DIR/libnaravisuals.so"
chmod 755 "$PLUGIN_DIR/libnaravisuals.so"

# Create symlinks for each widget variant
for widget in system-monitor weather quick-notes clipboard-manager pomodoro network-monitor tray-enhanced media-player battery; do
    ln -sf libnaravisuals.so "$PLUGIN_DIR/libnaravisuals-${widget}.so"
done

echo "  Plugin installed: $PLUGIN_DIR/libnaravisuals.so"
echo "  Symlinks: libnaravisuals-{widget}.so -> libnaravisuals.so"

# Install .desktop files
for f in /media/naranyala/Data/projects-remote/naravisuals-lxqt-widgets/desktop-panel/naravisuals-*.desktop; do
    cp "$f" "$DESKTOP_DIR/"
    echo "  Desktop: $DESKTOP_DIR/$(basename $f)"
done

echo ""
echo "==> Plugin installation complete!"
echo ""
echo "Now restart the panel:"
echo "  lxqt-panel --replace &"
echo ""
echo "Then right-click panel → Add Widgets..."
echo "Look for: System Monitor, Weather, Network Monitor, etc."
```

## `scripts/naravisuals-launcher`

```bash
#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from naravisuals.widgets.__main__ import main
main()
```

## `scripts/naravisuals-remove`

```bash
#!/usr/bin/env bash
set -e

echo "==> Removing NaraVisuals LXQt Widgets..."

BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"
PANEL_DIR="${HOME}/.local/share/lxqt/lxqt-panel"
AUTOSTART_DIR="${HOME}/.config/autostart"

rm -rf "${BIN_DIR}/naravisuals-"*
rm -f "${BIN_DIR}/naravisuals-manager"

for f in "${APP_DIR}/naravisuals-"*.desktop; do
    rm -f "$f"
done

for f in "${PANEL_DIR}/naravisuals-"*.desktop; do
    rm -f "$f"
done

for f in "${AUTOSTART_DIR}/naravisuals-"*.desktop; do
    rm -f "$f"
done

rm -rf "${BIN_DIR}/naravisuals" 2>/dev/null || true

echo "  Removed launchers, desktop files, autostart entries."
echo ""
echo "=== Removal complete ==="
```

