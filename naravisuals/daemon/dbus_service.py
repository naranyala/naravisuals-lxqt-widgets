"""D-Bus service for NaraVisuals daemon.

Provides widget data to C++ panel plugin via D-Bus IPC.
Interface: org.naravisuals.Daemon
Object path: /org/naravisuals/Daemon
"""
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtDBus import (
    QDBusAbstractAdaptor,
    QDBusConnection,
    QDBusMessage,
    QDBusVariant,
)

from naravisuals.core.theme_engine import theme, PanelContext

log = logging.getLogger("naravisuals.daemon")

# D-Bus constants
BUS_NAME = "org.naravisuals.Daemon"
OBJ_PATH = "/org/naravisuals/Daemon"
IFACE_NAME = "org.naravisuals.Daemon"


class WidgetProvider:
    """Base class for widget data providers."""

    PROVIDER_ID: str = ""

    def get_data(self) -> dict[str, Any]:
        raise NotImplementedError

    def start(self):
        pass

    def stop(self):
        pass


class DaemonAdaptor(QDBusAbstractAdaptor):
    """D-Bus adaptor exposing the daemon interface."""

    data_updated = pyqtSignal(str, str)  # widget_id, json_data

    def __init__(self, parent: "NaraVisualsDaemon"):
        super().__init__(parent)
        self.parent = parent

    @pyqtSlot(str, result=str)
    def GetData(self, widget_id: str) -> str:
        """Return current data for a widget as JSON string."""
        provider = self.parent.get_provider(widget_id)
        if provider is None:
            return json.dumps({"error": f"Unknown widget: {widget_id}"})
        try:
            data = provider.get_data()
            return json.dumps(data)
        except Exception as e:
            log.error("GetData(%s) failed: %s", widget_id, e)
            return json.dumps({"error": str(e)})

    @pyqtSlot(result=str)
    def ListWidgets(self) -> str:
        """Return list of registered widget IDs."""
        return json.dumps(list(self.parent.providers.keys()))

    @pyqtSlot(str, str)
    def SetConfig(self, widget_id: str, key: str, value: str):
        """Set a configuration value for a widget."""
        self.parent.set_config(widget_id, key, value)

    @pyqtSlot(str, result=str)
    def GetConfig(self, widget_id: str) -> str:
        """Get all configuration for a widget."""
        return json.dumps(self.parent.get_config(widget_id))

    @pyqtSlot(str)
    def ReloadWidget(self, widget_id: str):
        """Reload a specific widget provider."""
        self.parent.reload_provider(widget_id)

    @pyqtSlot(int, int, str, str)
    def UpdatePanelContext(self, height: int, width: int, orientation: str, position: str):
        """Update panel dimensions and orientation."""
        ctx = PanelContext(height=height, width=width, orientation=orientation, position=position)
        theme.update_panel_context(ctx)
        theme.update_from_palette()
        log.info("Panel context updated: %dx%d %s %s", height, width, orientation, position)

    @pyqtSlot(result=str)
    def GetTheme(self) -> str:
        """Get current theme colors as JSON."""
        colors = theme.colors
        return json.dumps({
            "background": colors.background,
            "foreground": colors.foreground,
            "accent": colors.accent,
            "border": colors.border,
            "text_primary": colors.text_primary,
            "text_secondary": colors.text_secondary,
            "is_dark": theme.is_dark,
        })

    @pyqtSlot(str, str)
    def SetCustomColor(self, name: str, color: str):
        """Set a custom color override."""
        theme.set_custom_color(name, color)

    @pyqtSlot(result=str)
    def GetPanelContext(self) -> str:
        """Get current panel context as JSON."""
        ctx = theme.panel_context
        return json.dumps({
            "height": ctx.height,
            "width": ctx.width,
            "orientation": ctx.orientation,
            "position": ctx.position,
        })


class NaraVisualsDaemon(QObject):
    """Main daemon managing widget data providers and D-Bus communication."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.providers: dict[str, WidgetProvider] = {}
        self.config: dict[str, dict[str, Any]] = {}
        self._adaptor: DaemonAdaptor | None = None
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_interval_ms = 2000

    def start(self) -> bool:
        """Register D-Bus service and start providers."""
        bus = QDBusConnection.sessionBus()
        if not bus.isConnected():
            log.error("Cannot connect to D-Bus session bus")
            return False

        # Register bus name
        if not bus.registerService(BUS_NAME):
            log.error("Cannot register D-Bus service %s: %s", bus.lastError().message())
            return False

        # Create adaptor and register object
        self._adaptor = DaemonAdaptor(self)
        if not bus.registerObject(OBJ_PATH, self):
            log.error("Cannot register D-Bus object: %s", bus.lastError().message())
            return False

        # Load and start providers
        self._register_providers()
        for provider in self.providers.values():
            try:
                provider.start()
            except Exception as e:
                log.error("Failed to start provider %s: %s", provider.PROVIDER_ID, e)

        self._tick_timer.start(self._tick_interval_ms)
        log.info("D-Bus service registered at %s", BUS_NAME)
        return True

    def stop(self):
        """Stop all providers and unregister D-Bus."""
        self._tick_timer.stop()
        for provider in self.providers.values():
            try:
                provider.stop()
            except Exception as e:
                log.error("Failed to stop provider %s: %s", provider.PROVIDER_ID, e)

        bus = QDBusConnection.sessionBus()
        bus.unregisterObject(OBJ_PATH)
        bus.unregisterService(BUS_NAME)

    def get_provider(self, widget_id: str) -> WidgetProvider | None:
        return self.providers.get(widget_id)

    def set_config(self, widget_id: str, key: str, value: str):
        if widget_id not in self.config:
            self.config[widget_id] = {}
        self.config[widget_id][key] = value
        # Persist to disk
        self._save_config()

    def get_config(self, widget_id: str) -> dict[str, Any]:
        return self.config.get(widget_id, {})

    def reload_provider(self, widget_id: str):
        provider = self.providers.get(widget_id)
        if provider:
            provider.stop()
            provider.start()

    def _register_providers(self):
        """Import and register all widget data providers."""
        from naravisuals.data_providers.system import (
            SystemMonitorProvider,
            NetworkMonitorProvider,
            BatteryProvider,
            UptimeProvider,
            PingProvider,
            KernelProvider,
        )
        from naravisuals.data_providers.weather import WeatherProvider
        from naravisuals.data_providers.productivity import (
            PomodoroProvider,
            QuickNotesProvider,
            ClipboardProvider,
        )
        from naravisuals.data_providers.integrations import (
            MediaPlayerProvider,
            SystemUpdatesProvider,
        )
        from naravisuals.data_providers.todo import TodoListProvider
        from naravisuals.data_providers.financial import CurrencyProvider, CryptoProvider
        from naravisuals.data_providers.ntfs_mount import NtfsMountProvider

        for cls in [
            SystemMonitorProvider,
            NetworkMonitorProvider,
            BatteryProvider,
            UptimeProvider,
            PingProvider,
            KernelProvider,
            WeatherProvider,
            PomodoroProvider,
            QuickNotesProvider,
            ClipboardProvider,
            MediaPlayerProvider,
            SystemUpdatesProvider,
            TodoListProvider,
            CurrencyProvider,
            CryptoProvider,
            NtfsMountProvider,
        ]:
            provider = cls()
            self.providers[provider.PROVIDER_ID] = provider
            log.info("Registered provider: %s", provider.PROVIDER_ID)

    def _on_tick(self):
        """Periodically emit data updates for all providers."""
        if not self._adaptor:
            return
        for widget_id, provider in self.providers.items():
            try:
                data = provider.get_data()
                json_data = json.dumps(data)
                self._adaptor.data_updated.emit(widget_id, json_data)
            except Exception as e:
                log.error("Tick failed for %s: %s", widget_id, e)

    def _save_config(self):
        import os
        from pathlib import Path

        config_dir = Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))) / "naravisuals"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"
        try:
            with open(config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            log.error("Failed to save config: %s", e)
