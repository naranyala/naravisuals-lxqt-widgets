# NaraVisuals LXQt Widgets

Next-generation, API-driven panel widgets for the LXQt desktop environment.

[![License: GPL3](https://img.shields.io/badge/License-GPL3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-yellow.svg)](https://riverbankcomputing.com/software/pyqt/)

---

## Overview

NaraVisuals extends the LXQt desktop with advanced panel widgets through a hybrid C++/Python architecture. The project integrates a native C++ panel plugin with a Python-based D-Bus daemon, enabling complex UI elements to render directly within the LXQt panel while maintaining minimal resource overhead.

The architecture separates data acquisition from UI rendering: Python providers collect system metrics and external data via D-Bus, while C++ renderers handle pixel-level display inside the panel. This design ensures compatibility with both X11 and Wayland display servers.

---

## Architecture

```
+-----------------------------+         +-----------------------------+
|     lxqt-panel (C++)        |         |   naravisuals-daemon (Py)   |
|                             |  D-Bus  |                             |
|  +-----------------------+  | <-----> |  +-----------------------+  |
|  | NaraVisuals Plugin    |  |         |  | SystemMonitorProvider |  |
|  |  - TextRenderer       |  |         |  | WeatherProvider       |  |
|  |  - BarRenderer        |  |         |  | PomodoroProvider      |  |
|  |  - GraphRenderer      |  |         |  | ClipboardProvider     |  |
|  |  - IconTextRenderer   |  |         |  | ... (12 providers)    |  |
|  +-----------------------+  |         |  +-----------------------+  |
+-----------------------------+         +-----------------------------+
         |                                          |
         | embeds                                    | queries
         v                                          v
+-----------------------------+         +-----------------------------+
|    Wayland / X11 Server    |         |     System / Network APIs   |
+-----------------------------+         +-----------------------------+
```

### Component Roles

| Component | Language | Responsibility |
|-----------|----------|----------------|
| `native-plugin/` | C++17 | Panel plugin, UI rendering, D-Bus client |
| `naravisuals/daemon/` | Python 3 | D-Bus service, data provider registry |
| `naravisuals/data_providers/` | Python 3 | System metrics, network, weather APIs |
| `naravisuals/core/` | Python 3 | Base widget classes, async utilities |
| `naravisuals/manager/` | Python 3 | Settings GUI (PyQt6) |
| `naravisuals/widgets/` | Python 3 | Standalone widget implementations |

---

## Directory Structure

```
naravisuals-lxqt-widgets/
├── native-plugin/              # C++ LXQt panel plugin
│   ├── CMakeLists.txt          # Build system (Qt6, lxqt)
│   ├── naravisuals-plugin.cpp  # Plugin + renderers
│   └── build/                  # CMake build artifacts
│
├── naravisuals/                # Python package
│   ├── core/                   # Foundation classes
│   │   ├── base_widget.py      # PanelWidget, TextWidget, IconTextWidget
│   │   ├── async_utils.py      # Thread pool, command execution
│   │   └── config_manager.py   # JSON config persistence
│   │
│   ├── daemon/                 # D-Bus daemon service
│   │   ├── __main__.py         # Entry point
│   │   └── dbus_service.py     # D-Bus interface, provider registry
│   │
│   ├── data_providers/         # Widget data sources
│   │   ├── system.py           # CPU, RAM, disk, network, battery
│   │   ├── weather.py          # wttr.in API integration
│   │   ├── productivity.py     # Pomodoro, notes, clipboard
│   │   └── integrations.py     # MPRIS, system updates
│   │
│   ├── widgets/                # Standalone widget implementations
│   │   ├── system/             # SystemMonitor, NetworkMonitor, Battery
│   │   ├── productivity/       # Pomodoro, QuickNotes, Clipboard
│   │   ├── integrations/       # Weather, MediaPlayer, SystemUpdates
│   │   └── native/             # Clock, AppMenu, Volume, Pager, Taskbar
│   │
│   ├── manager/                # Settings Hub GUI
│   │   └── app.py              # Panel organizer, widget config
│   │
│   └── sddm_manager/          # SDDM display manager integration
│
├── packaging/                  # Distribution packaging
│   ├── naravisuals-lxqt-widgets.spec  # RPM spec (Fedora/RHEL)
│   ├── naravisuals-daemon.service     # systemd user service
│   └── stock-panel.conf               # Default panel config
│
├── scripts/                    # Utility scripts
│   ├── build-rpm.sh            # RPM build helper
│   ├── naravisuals-panel-reset # Panel reset tool (CLI)
│   └── naravisuals-remove      # Uninstaller
│
├── desktop/                    # .desktop launcher files
├── tests/                      # Test suite
├── docs/                       # Distribution-specific guides
├── install.sh                  # Universal installer
├── setup.py                    # PyPI packaging
└── PKGBUILD                    # Arch Linux AUR
```

---

## Dependencies

### Runtime Dependencies

| Library | Version | Purpose | Usage |
|---------|---------|---------|-------|
| **PyQt6** | >= 6.5 | Qt6 Python bindings | All widget UI, D-Bus adaptor, daemon event loop |
| **psutil** | >= 5.8 | System monitoring | CPU, memory, disk, network, battery, uptime |
| **requests** | >= 2.25 | HTTP client | Weather API calls to wttr.in |
| **dbus-python** | >= 1.2 | D-Bus IPC | Daemon-to-plugin communication |
| **notify2** | >= 0.3 | Desktop notifications | Pomodoro alerts, system update notifications |

### Build Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| **CMake** | >= 3.16 | Build system for C++ plugin |
| **Qt6 Widgets** | >= 6.5 | C++ plugin UI framework |
| **Qt6 DBus** | >= 6.5 | C++ D-Bus client |
| **lxqt-build-tools** | >= 2.0 | LXQt panel plugin headers |
| **gcc/g++** | >= 10 | C++17 compiler |
| **python3-devel** | >= 3.10 | Python development headers |

### System Dependencies

| Service | Purpose |
|---------|---------|
| **D-Bus session bus** | IPC between daemon and plugin |
| **systemd** | User service management (optional) |
| **lxqt-panel** | Host panel for widget embedding |
| **psutil** (system) | Kernel-level system metrics |

### Dependency Chain

```
lxqt-panel
    └── loads libnaravisuals.so (C++ plugin)
            ├── Qt6::Widgets (UI rendering)
            ├── Qt6::DBus (D-Bus client)
            └── lxqt (panel plugin API)
                    │
                    │ D-Bus IPC
                    ▼
            naravisuals-daemon (Python)
                ├── PyQt6 (D-Bus adaptor, event loop)
                ├── psutil (system metrics)
                ├── requests (weather API)
                └── dbus-python (D-Bus bindings)
```

---

## Widgets

### System Monitor

Real-time tracking of CPU usage, RAM consumption, disk I/O, and network throughput. Displays progress bars with color-coded indicators.

- **Data Provider**: `SystemMonitorProvider` (psutil)
- **Renderer**: `SystemMonitorRenderer` (composite bar widget)
- **Update Interval**: 2 seconds

### Network Monitor

Live network traffic monitoring with configurable interface selection. Shows upload/download rates and packet statistics.

- **Data Provider**: `NetworkMonitorProvider` (psutil.net_io_counters)
- **Renderer**: `TextRenderer` (rate display)
- **Update Interval**: 1 second

### Battery Info

Hardware battery status including charge percentage, charging state, and estimated time remaining.

- **Data Provider**: `BatteryProvider` (psutil.sensors_battery)
- **Renderer**: `IconTextRenderer` (icon + percentage)
- **Update Interval**: 30 seconds

### Weather

Location-based meteorological data from wttr.in API. Configurable city and temperature units.

- **Data Provider**: `WeatherProvider` (requests + wttr.in)
- **Renderer**: `IconTextRenderer` (icon + temperature)
- **Update Interval**: 10 minutes
- **Config**: `~/.config/naravisuals/weather.json`

### Pomodoro Timer

Productivity timer with configurable work/break durations and session counting.

- **Data Provider**: `PomodoroProvider` (internal state)
- **Renderer**: `TextRenderer` (time display)
- **Update Interval**: 1 second

### Quick Notes

Direct panel-integrated text storage with persistent JSON backing.

- **Data Provider**: `QuickNotesProvider` (JSON file)
- **Renderer**: `TextRenderer` (note preview)
- **Config**: `~/.config/naravisuals/notes.json`

### Clipboard Manager

Persistent clipboard history tracking with configurable maximum entries.

- **Data Provider**: `ClipboardProvider` (in-memory)
- **Renderer**: `TextRenderer` (recent items)
- **Update Interval**: On clipboard change

### System Updates

Background verification of pending package updates across multiple package managers (apt, dnf, pacman).

- **Data Provider**: `SystemUpdatesProvider` (subprocess)
- **Renderer**: `TextRenderer` (update count)
- **Update Interval**: 30 minutes

### Additional Widgets

- **Uptime Counter**: System uptime display
- **Ping Monitor**: Network latency to configurable host
- **Kernel Version**: Active kernel information
- **Media Player**: MPRIS-compatible playback controls
- **Tray Enhanced**: Extended system tray functionality

---

## Installation

### Arch Linux (AUR)

```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
makepkg -si
```

### Fedora / RHEL / CentOS

```bash
# Install build dependencies
sudo dnf install -y cmake gcc-c++ make qt6-qtbase-devel \
    lxqt-build-tools-devel python3-devel python3-setuptools \
    python3-pyqt6 python3-psutil python3-requests \
    python3-dbus-python python3-notify2 lxqt-panel

# Build and install RPM
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
./scripts/build-rpm.sh --setup
./scripts/build-rpm.sh --all
sudo ./scripts/build-rpm.sh --install
```

See [docs/INSTALL-FEDORA.md](docs/INSTALL-FEDORA.md) for detailed instructions.

### Debian / Ubuntu

```bash
sudo apt install -y cmake lxqt-build-tools python3-pyqt6 \
    python3-psutil python3-requests python3-dbus python3-notify2

git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
sudo PREFIX=/usr ./install.sh
```

### From Source (Any Distribution)

```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets

# System-wide installation
sudo PREFIX=/usr/local ./install.sh

# User-only installation
./install.sh
```

### PyPI

```bash
pip install naravisuals-lxqt-widgets
```

---

## Usage

### Adding Widgets to Panel

1. Right-click the LXQt panel
2. Select "Add Widgets..."
3. Search for "NaraVisuals"
4. Select desired widget

### Launching the Settings Hub

```bash
naravisuals-manager
```

The Settings Hub provides:
- Panel organizer (add, remove, reorder widgets)
- Widget-specific configuration
- Panel reset to stock configuration
- Import/export panel templates

### D-Bus Daemon

The daemon runs automatically via systemd user service. Manual control:

```bash
# Start daemon
systemctl --user start naravisuals-daemon

# Stop daemon
systemctl --user stop naravisuals-daemon

# Check status
systemctl --user status naravisuals-daemon

# View logs
journalctl --user -u naravisuals-daemon
```

### Panel Reset

Reset the LXQt panel to default configuration:

```bash
# Reset to stock (removes all NaraVisuals widgets)
naravisuals-panel-reset --stock

# Backup first, then reset
naravisuals-panel-reset --save-backup --stock

# Restore from backup
naravisuals-panel-reset --backup

# Preview changes without applying
naravisuals-panel-reset --dry-run --stock
```

### Diagnostics

Run diagnostic checks to identify issues:

```bash
# Run all diagnostic checks
naravisuals-doctor

# Validate LXQt configuration
naravisuals-lxqt-validator

# Scan and fix LXQt configuration
naravisuals-lxqt-scanner
naravisuals-lxqt-scanner --fix   # Auto-fix issues

# View daemon logs
naravisuals-logs

# Follow logs in real-time
naravisuals-logs -f

# Show only errors
naravisuals-logs -e
```

### Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues and solutions.

---

## Configuration

### Configuration Files

| Path | Purpose |
|------|---------|
| `~/.config/naravisuals/config.json` | Widget settings |
| `~/.config/naravisuals/weather.json` | Weather city configuration |
| `~/.config/naravisuals/notes.json` | Quick Notes storage |
| `~/.config/lxqt/panel.conf` | LXQt panel layout |
| `~/.config/lxqt/panel-backups/` | Panel configuration backups |

### D-Bus Interface

Service name: `org.naravisuals.Daemon`
Object path: `/org/naravisuals/Daemon`

Methods:
- `GetData(widget_id: String) -> String` - Get widget data as JSON
- `ListWidgets() -> String` - List available widget IDs
- `SetConfig(widget_id: String, key: String, value: String)` - Set widget config
- `GetConfig(widget_id: String) -> String` - Get widget config
- `ReloadWidget(widget_id: String)` - Reload widget provider

Signals:
- `dataUpdated(widget_id: String, json_data: String)` - Emitted on data change

---

## Development

### Building the C++ Plugin

```bash
cd native-plugin
mkdir build && cd build
cmake ..
make
```

### Running Tests

```bash
cd naravisuals-lxqt-widgets
python -m pytest tests/
```

### Project Structure Conventions

- Widget classes inherit from `PanelWidget` or its subclasses
- Data providers inherit from `WidgetProvider`
- C++ renderers inherit from `WidgetRenderer`
- Configuration uses JSON format in `~/.config/naravisuals/`

---

## Roadmap

See [TODOS.md](TODOS.md) for the complete development roadmap.

### Phase 1: Wayland-Ready Architecture (Q3 2026)

- D-Bus IPC daemon
- C++ plugin refactoring
- Labwc compatibility
- Performance validation

### Phase 2: Polish and Ecosystem (Q4 2026 - Q2 2027)

- Dynamic theming system
- Widget enhancements
- Debian/Fedora packaging
- Documentation and community

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System architecture and component design |
| [API Reference](docs/API.md) | D-Bus interface documentation |
| [Widgets](docs/WIDGETS.md) | Complete widget reference |
| [Theming](docs/THEMING.md) | Theme customization guide |
| [Development](docs/DEVELOPMENT.md) | Developer guide |
| [Deployment](docs/DEPLOYMENT.md) | Installation and deployment |
| [Security](docs/SECURITY.md) | Security considerations |
| [Contributing](docs/CONTRIBUTING.md) | Contribution guidelines |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [Changelog](docs/CHANGELOG.md) | Version history |
| [Fedora Install](docs/INSTALL-FEDORA.md) | Fedora/RHEL installation |

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please see the [Contributing Guide](docs/CONTRIBUTING.md) for details.

## Support

- [GitHub Issues](https://github.com/naranyala/naravisuals-lxqt-widgets/issues)
- [LXQt Project](https://lxqt-project.org/)
