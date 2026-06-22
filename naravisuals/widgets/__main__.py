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
