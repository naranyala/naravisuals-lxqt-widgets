"""Integration data providers: MPRIS media player, system updates."""
import subprocess
from typing import Any

from naravisuals.daemon.dbus_service import WidgetProvider


class MediaPlayerProvider(WidgetProvider):
    PROVIDER_ID = "media-player"

    def get_data(self) -> dict[str, Any]:
        try:
            from PyQt6.QtDBus import QDBusConnection, QDBusMessage

            bus = QDBusConnection.sessionBus()
            # Try to get MPRIS player list
            msg = bus.call(
                "org.mpris.MediaPlayer2.Player",
                "/org/mpris/MediaPlayer2",
                "org.freedesktop.DBus.Properties",
                "GetAll",
                "s",
                ["org.mpris.MediaPlayer2.Player"],
            )
            if msg.type() == QDBusMessage.MessageType.ErrorMessage:
                return {"available": False, "playing": False}

            # Parse basic MPRIS data
            return {
                "available": True,
                "playing": False,
                "title": "",
                "artist": "",
                "album": "",
            }
        except Exception:
            return {"available": False, "playing": False}


class SystemUpdatesProvider(WidgetProvider):
    PROVIDER_ID = "system-updates"

    def __init__(self):
        super().__init__()
        self._update_count = 0
        self._distro = ""

    def start(self):
        import platform

        self._distro = platform.freedesktop_os_release().get("ID", "unknown")

    def get_data(self) -> dict[str, Any]:
        self._check_updates()
        return {
            "distro": self._distro,
            "update_count": self._update_count,
            "has_updates": self._update_count > 0,
        }

    def _check_updates(self):
        try:
            if self._distro in ("arch", "manjaro", "endeavouros", "garuda"):
                out = subprocess.check_output(
                    ["checkupdates"],
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                ).decode()
                self._update_count = len(out.strip().splitlines()) if out.strip() else 0
            elif self._distro in ("ubuntu", "debian", "linuxmint", "pop"):
                subprocess.run(
                    ["apt", "list", "--upgradable"],
                    capture_output=True,
                    timeout=30,
                )
                out = subprocess.check_output(
                    ["apt", "list", "--upgradable"],
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                ).decode()
                lines = [l for l in out.splitlines() if "/" in l]
                self._update_count = max(0, len(lines) - 1)
            elif self._distro in ("fedora", "rhel", "centos"):
                out = subprocess.check_output(
                    ["dnf", "check-update", "--quiet"],
                    stderr=subprocess.DEVNULL,
                    timeout=30,
                ).decode()
                lines = [l for l in out.splitlines() if l.strip() and not l.startswith("Last")]
                self._update_count = len(lines) if out.strip() else 0
            else:
                self._update_count = 0
        except Exception:
            self._update_count = 0
