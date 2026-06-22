import dbus
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QSlider

from naravisuals.core.base_widget import PanelWidget


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
