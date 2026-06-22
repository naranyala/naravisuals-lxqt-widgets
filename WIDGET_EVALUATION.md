# Widget Evaluation Report

A comprehensive automated testing suite (`tests/test_widgets.py`) was implemented using Python's `unittest` framework to evaluate the widgets available in the project. The test suite operates in headless mode (`QT_QPA_PLATFORM=offscreen`) to allow execution in CI/CD environments without requiring a display server.

## Architecture (v2.0)

The project now uses a **D-Bus IPC architecture** for Wayland compatibility:

```
┌─────────────────────┐     D-Bus      ┌─────────────────────┐
│  C++ Panel Plugin   │ ◄────────────► │  naravisuals-daemon │
│  (renders UI)       │                │  (data providers)   │
└─────────────────────┘                └─────────────────────┘
```

- **C++ Plugin**: Renders widget UI inside lxqt-panel, communicates via D-Bus
- **Daemon**: Single Python process managing all widget data providers
- **Data Providers**: System, Weather, Productivity, Integrations modules

## Test Results: ✅ PASS

All widgets successfully pass the following checks:
1. **Instantiation Safety:** They can be constructed and embedded into the UI tree without raising exceptions.
2. **Tick Safety:** Their primary core logic (`_on_tick()`) can execute at least once without crashing, even if the underlying system dependencies (e.g., `docker`, `nvidia-smi`, or `journalctl`) are missing or require permissions.
3. **D-Bus Communication:** Data providers return valid JSON responses.

## Data Providers

### System Providers
- **SystemMonitorProvider:** CPU, RAM, disk, swap, network rates
- **NetworkMonitorProvider:** Upload/download speeds, packet counts
- **BatteryProvider:** Percentage, charging status, time remaining
- **UptimeProvider:** System uptime formatted as days/hours/minutes
- **PingProvider:** Network latency to configurable host
- **KernelProvider:** Kernel version and machine architecture

### Weather Provider
- **WeatherProvider:** Temperature, description, humidity, wind speed
- Supports city configuration via `~/.config/naravisuals/weather.json`

### Productivity Providers
- **PomodoroProvider:** Timer state, work/break cycles, pomodoro count
- **QuickNotesProvider:** Note CRUD operations with persistence
- **ClipboardProvider:** Clipboard history management

### Integration Providers
- **MediaPlayerProvider:** MPRIS player detection (basic)
- **SystemUpdatesProvider:** Package manager integration (apt, dnf, pacman)

## C++ Renderers

The C++ plugin includes built-in renderers for each widget type:
- **TextRenderer:** Simple text display (kernel, uptime, ping)
- **BarRenderer:** Progress bars (CPU, RAM, disk usage)
- **SystemMonitorRenderer:** Composite of multiple bars + network label
- **IconTextRenderer:** Icon + text (weather, battery)

## Evaluation Notes

- **SystemMonitor:** Stable. Correctly interfaces with psutil.
- **NetworkMonitor:** Stable. Correctly parses psutil.net_io_counters().
- **BatteryInfo:** Stable. Reliably queries psutil.sensors_battery().
- **Weather:** Needs API Key handling. MVP relies on public unauthenticated endpoints but should migrate to config.py settings.
- **MediaPlayer:** Relies on D-Bus MPRIS. Handled gracefully if no players are active.
- **SystemUpdates:** Detects distro and uses appropriate package manager.

## Wayland Compatibility

The D-Bus architecture enables full Wayland support:
- No X11-specific WId embedding
- D-Bus works on both X11 and Wayland
- Tested with Labwc, Sway, and Hyprland compositors
