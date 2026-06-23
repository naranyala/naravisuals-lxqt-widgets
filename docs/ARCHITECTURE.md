# Architecture

This document describes the complete architecture of NaraVisuals LXQt Widgets.

## System Overview

NaraVisuals is a hybrid C++/Python system that extends the LXQt desktop with advanced panel widgets. The architecture separates data acquisition from UI rendering, enabling Wayland compatibility through D-Bus IPC.

```
+-----------------------------+         +-----------------------------+
|     lxqt-panel (C++)        |         |   naravisuals-daemon (Py)   |
|                             |  D-Bus  |                             |
|  +-----------------------+  | <-----> |  +-----------------------+  |
|  | NaraVisuals Plugin    |  |         |  | WidgetProvider(s)     |  |
|  |  - TextRenderer       |  |         |  |  - SystemMonitor      |  |
|  |  - BarRenderer        |  |         |  |  - Weather            |  |
|  |  - GraphRenderer      |  |         |  |  - Pomodoro           |  |
|  |  - IconTextRenderer   |  |         |  |  - Clipboard          |  |
|  +-----------------------+  |         |  |  - ... (16 providers) |  |
|                             |         |  +-----------------------+  |
+-----------------------------+         +-----------------------------+
         |                                          |
         | embeds                                    | queries
         v                                          v
+-----------------------------+         +-----------------------------+
|    Wayland / X11 Server    |         |     System / Network APIs   |
+-----------------------------+         +-----------------------------+
```

## Core Components

### 1. C++ Panel Plugin (`native-plugin/`)

**Purpose:** Renders widget UI inside lxqt-panel and communicates with the daemon via D-Bus.

**Key Files:**
- `naravisuals-plugin.cpp` - Main plugin implementation
- `CMakeLists.txt` - Build configuration

**Classes:**

| Class | Purpose |
|-------|---------|
| `NaraVisualsPlugin` | Main plugin class, implements `ILXQtPanelPlugin` |
| `NaraVisualsPluginLibrary` | Plugin library entry point |
| `WidgetRenderer` | Base class for all renderers |
| `TextRenderer` | Simple text display |
| `BarRenderer` | Progress bar display |
| `SystemMonitorRenderer` | Composite bar widget |
| `IconTextRenderer` | Icon + text display |

**Lifecycle:**

```
1. lxqt-panel loads libnaravisuals.so
2. NaraVisualsPluginLibrary::instance() creates NaraVisualsPlugin
3. NaraVisualsPlugin connects to D-Bus daemon
4. Plugin requests widget data via D-Bus
5. Renderer updates UI with received data
```

### 2. D-Bus Daemon (`naravisuals/daemon/`)

**Purpose:** Single Python process managing all widget data providers and exposing them via D-Bus.

**Key Files:**
- `__main__.py` - Entry point
- `dbus_service.py` - D-Bus interface implementation

**D-Bus Interface:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `GetData` | `(string) -> string` | Get widget data as JSON |
| `ListWidgets` | `() -> string` | List available widget IDs |
| `SetConfig` | `(string, string, string)` | Set widget configuration |
| `GetConfig` | `(string) -> string` | Get widget configuration |
| `ReloadWidget` | `(string)` | Reload widget provider |
| `UpdatePanelContext` | `(int, int, string, string)` | Update panel dimensions |
| `GetTheme` | `() -> string` | Get current theme colors |
| `SetCustomColor` | `(string, string)` | Set custom color |
| `GetPanelContext` | `() -> string` | Get panel context |

**Signal:**

| Signal | Signature | Description |
|--------|-----------|-------------|
| `dataUpdated` | `(string, string)` | Emitted when widget data changes |

### 3. Data Providers (`naravisuals/data_providers/`)

**Purpose:** Collect system metrics and external data for widgets.

**Base Class:**

```python
class WidgetProvider:
    PROVIDER_ID: str = ""
    
    def get_data(self) -> dict[str, Any]:
        raise NotImplementedError
    
    def start(self):
        pass
    
    def stop(self):
        pass
```

**Provider Registry:**

| Provider | ID | Data Source |
|----------|-----|-------------|
| `SystemMonitorProvider` | `system-monitor` | psutil |
| `NetworkMonitorProvider` | `network-monitor` | psutil.net_io_counters |
| `BatteryProvider` | `battery` | psutil.sensors_battery |
| `UptimeProvider` | `uptime` | psutil.boot_time |
| `PingProvider` | `ping-monitor` | subprocess (ping) |
| `KernelProvider` | `kernel-version` | platform.release |
| `WeatherProvider` | `weather` | requests (wttr.in) |
| `PomodoroProvider` | `pomodoro` | internal state |
| `QuickNotesProvider` | `quick-notes` | JSON file |
| `ClipboardProvider` | `clipboard-manager` | in-memory |
| `MediaPlayerProvider` | `media-player` | D-Bus MPRIS |
| `SystemUpdatesProvider` | `system-updates` | subprocess (apt/dnf/pacman) |
| `TodoListProvider` | `todo-list` | JSON file |
| `CurrencyProvider` | `currency` | requests (exchangerate-api) |
| `CryptoProvider` | `crypto` | requests (coingecko) |
| `NtfsMountProvider` | `ntfs-mount` | subprocess (lsblk, mount) |

### 4. Theme Engine (`naravisuals/core/theme_engine.py`)

**Purpose:** Dynamic theming based on system QPalette, panel dimensions, and user preferences.

**Key Features:**
- Dark/light mode auto-detection
- Responsive layouts based on panel height
- Custom color overrides
- QPalette integration

**ThemeColors:**

| Property | Default | Description |
|----------|---------|-------------|
| `background` | `#2d2d2d` | Widget background |
| `foreground` | `#ffffff` | Text color |
| `accent` | `#3daee9` | Accent color |
| `border` | `#555555` | Border color |
| `text_primary` | `#ffffff` | Primary text |
| `text_secondary` | `#aaaaaa` | Secondary text |
| `bar_cpu` | `#2ecc71` | CPU bar color |
| `bar_ram` | `#3498db` | RAM bar color |
| `bar_disk` | `#9b59b6` | Disk bar color |
| `bar_swap` | `#e74c3c` | Swap bar color |
| `bar_network` | `#f39c12` | Network bar color |

### 5. Widget Classes (`naravisuals/widgets/`)

**Purpose:** Standalone widget implementations for testing and embedded panel mode.

**Base Classes:**

| Class | Purpose |
|-------|---------|
| `PanelWidget` | Base widget with timer and context menu |
| `TextWidget` | Simple text display |
| `IconTextWidget` | Icon + text display |
| `AsyncCommandWidget` | Shell command execution |

**Widget Categories:**

| Category | Widgets |
|----------|---------|
| `system/` | SystemMonitor, NetworkMonitor, Battery, Uptime, Ping, Kernel, NtfsMount |
| `productivity/` | Pomodoro, QuickNotes, Clipboard |
| `integrations/` | Weather, MediaPlayer, SystemUpdates, TrayEnhanced |
| `native/` | Clock, AppMenu, Volume, Pager, Taskbar, SystemTray |

### 6. Control Center (`naravisuals/manager/control_center.py`)

**Purpose:** All-in-one GUI for managing the entire NaraVisuals ecosystem.

**Pages:**

| Page | Purpose |
|------|---------|
| Dashboard | Daemon status, system stats, quick actions |
| Widget Browser | Widget catalog with enable/disable |
| Panel Organizer | Drag-and-drop panel layout editor |
| Theme | Color customization, panel context |
| Backup & Restore | Create/restore/delete backups |
| Log Viewer | Daemon, system, widget logs |
| About | Version info and links |

## Data Flow

### Widget Update Cycle

```
1. naravisuals-daemon starts
2. Registers D-Bus service at org.naravisuals.Daemon
3. Starts all WidgetProviders
4. Timer ticks every 2 seconds
5. For each provider:
   a. Call provider.get_data()
   b. Serialize to JSON
   c. Emit dataUpdated signal
6. C++ plugin receives signal
7. Parses JSON data
8. Calls renderer.updateData()
9. Renderer updates QWidget
```

### Manual Data Request

```
1. C++ plugin calls requestData()
2. D-Bus call: GetData(widget_id)
3. Daemon receives call
4. Calls provider.get_data()
5. Returns JSON response
6. Plugin updates renderer
```

## Configuration

### File Locations

| File | Purpose |
|------|---------|
| `~/.config/naravisuals/config.json` | Widget settings |
| `~/.config/naravisuals/weather.json` | Weather city |
| `~/.config/naravisuals/notes.json` | Quick notes |
| `~/.config/naravisuals/todos.json` | Todo list |
| `~/.config/naravisuals/theme.json` | Custom theme |
| `~/.config/lxqt/panel.conf` | Panel layout |
| `~/.config/lxqt/panel-backups/` | Panel backups |

### Systemd Service

- Service: `naravisuals-daemon.service`
- Location: `~/.local/share/systemd/user/`
- Type: D-Bus activated

### D-Bus Service

- Service: `org.naravisuals.Daemon.service`
- Location: `~/.local/share/dbus-1/services/`
- Bus: Session

## Build System

### CMake (C++ Plugin)

```bash
cd native-plugin
mkdir build && cd build
cmake ..
make
```

### Python Package

```bash
# Development install
pip install -e .

# System install
python setup.py install
```

### Packaging

| Format | Command |
|--------|---------|
| Arch Linux | `makepkg -si` |
| RPM | `./scripts/build-rpm.sh --all` |
| Debian | `dpkg-buildpackage -us -uc` |
| Flatpak | `flatpak-builder` |

## Security Considerations

### D-Bus Access

- Daemon runs in user session
- No system-wide D-Bus access
- Methods require valid widget IDs

### Privilege Escalation

- NTFS mount uses `pkexec` for root
- User must authenticate via polkit
- No persistent root privileges

### Configuration Files

- All user-owned
- No world-readable sensitive data
- XDG-compliant paths

## Performance

### Memory Usage

| Component | Target |
|-----------|--------|
| Daemon (10 widgets) | <80MB |
| C++ Plugin | <10MB |
| Total | <100MB |

### CPU Usage

| Component | Target |
|-----------|--------|
| Daemon tick | <1% |
| Plugin render | <0.5% |
| Total | <2% |

### D-Bus Latency

| Operation | Target |
|-----------|--------|
| GetData call | <10ms |
| Signal delivery | <5ms |
| Total cycle | <15ms |

## Wayland Compatibility

### Current Status

- D-Bus IPC works on Wayland
- No X11-specific WId embedding
- Compatible with Labwc, Sway, Hyprland

### Future Improvements

- Layer Shell integration
- Native Wayland panel backend
- Direct compositor communication
