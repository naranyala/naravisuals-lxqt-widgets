"""NaraVisuals data providers for D-Bus daemon."""
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

__all__ = [
    "SystemMonitorProvider",
    "NetworkMonitorProvider",
    "BatteryProvider",
    "UptimeProvider",
    "PingProvider",
    "KernelProvider",
    "WeatherProvider",
    "PomodoroProvider",
    "QuickNotesProvider",
    "ClipboardProvider",
    "MediaPlayerProvider",
    "SystemUpdatesProvider",
]
