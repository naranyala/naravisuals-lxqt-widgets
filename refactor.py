import os
import shutil
import glob

# 1. Move core files
core_moves = {
    "naravisuals/base.py": "naravisuals/core/base_widget.py",
    "naravisuals/config.py": "naravisuals/core/config_manager.py",
    "naravisuals/utils.py": "naravisuals/core/async_utils.py"
}

for src, dst in core_moves.items():
    if os.path.exists(src):
        os.rename(src, dst)

# 2. Move widgets to categories
widget_moves = {
    # System
    "system_monitor.py": "system",
    "network_monitor.py": "system",
    "battery.py": "system",
    "uptime.py": "system",
    "kernel_version.py": "system",
    "ping_monitor.py": "system",
    # Productivity
    "pomodoro.py": "productivity",
    "quick_notes.py": "productivity",
    "clipboard_manager.py": "productivity",
    # Integrations
    "weather.py": "integrations",
    "tray_enhanced.py": "integrations",
    "media_player.py": "integrations",
    "system_updates.py": "integrations",
}

for w_file, category in widget_moves.items():
    src = f"naravisuals/widgets/{w_file}"
    dst = f"naravisuals/widgets/{category}/{w_file}"
    if os.path.exists(src):
        os.rename(src, dst)

# 3. Create __init__.py files
init_files = [
    "naravisuals/core/__init__.py",
    "naravisuals/manager/__init__.py",
    "naravisuals/manager/tabs/__init__.py",
    "naravisuals/data_providers/__init__.py",
    "naravisuals/widgets/system/__init__.py",
    "naravisuals/widgets/productivity/__init__.py",
    "naravisuals/widgets/integrations/__init__.py",
]
for init in init_files:
    open(init, 'a').close()

# 4. Refactor Imports inside ALL python files
replacements = {
    "from naravisuals.base import ": "from naravisuals.core.base_widget import ",
    "from naravisuals.config import ": "from naravisuals.core.config_manager import ",
    "from naravisuals.utils import ": "from naravisuals.core.async_utils import ",
    "import naravisuals.widgets as w": "from naravisuals import widgets as w",
    "naravisuals.widgets.system_monitor": "naravisuals.widgets.system.system_monitor",
    "naravisuals.widgets.network_monitor": "naravisuals.widgets.system.network_monitor",
    "naravisuals.widgets.battery": "naravisuals.widgets.system.battery",
    "naravisuals.widgets.uptime": "naravisuals.widgets.system.uptime",
    "naravisuals.widgets.kernel_version": "naravisuals.widgets.system.kernel_version",
    "naravisuals.widgets.ping_monitor": "naravisuals.widgets.system.ping_monitor",
    "naravisuals.widgets.pomodoro": "naravisuals.widgets.productivity.pomodoro",
    "naravisuals.widgets.quick_notes": "naravisuals.widgets.productivity.quick_notes",
    "naravisuals.widgets.clipboard_manager": "naravisuals.widgets.productivity.clipboard_manager",
    "naravisuals.widgets.weather": "naravisuals.widgets.integrations.weather",
    "naravisuals.widgets.tray_enhanced": "naravisuals.widgets.integrations.tray_enhanced",
    "naravisuals.widgets.media_player": "naravisuals.widgets.integrations.media_player",
    "naravisuals.widgets.system_updates": "naravisuals.widgets.integrations.system_updates",
}

for root, _, files in os.walk("naravisuals"):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            for old, new in replacements.items():
                content = content.replace(old, new)
            with open(filepath, 'w') as f:
                f.write(content)

# Refactor test file imports
test_file = "tests/test_widgets.py"
if os.path.exists(test_file):
    with open(test_file, 'r') as f:
        content = f.read()
    content = content.replace("w.SystemMonitor", "w.system.system_monitor.SystemMonitor")
    content = content.replace("w.WeatherWidget", "w.integrations.weather.WeatherWidget")
    content = content.replace("w.QuickNotes", "w.productivity.quick_notes.QuickNotes")
    content = content.replace("w.ClipboardManager", "w.productivity.clipboard_manager.ClipboardManager")
    content = content.replace("w.PomodoroTimer", "w.productivity.pomodoro.PomodoroTimer")
    content = content.replace("w.NetworkMonitor", "w.system.network_monitor.NetworkMonitor")
    content = content.replace("w.TrayEnhanced", "w.integrations.tray_enhanced.TrayEnhanced")
    content = content.replace("w.MediaPlayerController", "w.integrations.media_player.MediaPlayerController")
    content = content.replace("w.BatteryInfo", "w.system.battery.BatteryInfo")
    content = content.replace("w.UptimeWidget", "w.system.uptime.UptimeWidget")
    content = content.replace("w.PingMonitor", "w.system.ping_monitor.PingMonitor")
    content = content.replace("w.SystemUpdates", "w.integrations.system_updates.SystemUpdates")
    content = content.replace("w.KernelVersion", "w.system.kernel_version.KernelVersion")
    with open(test_file, 'w') as f:
        f.write(content)

print("Mass refactoring complete.")
