# NaraVisuals LXQt Widgets - Roadmap

## Phase 1: Wayland-Ready Architecture (Critical)

> Make the project work on Wayland via D-Bus IPC and single daemon.

### 1.1 D-Bus IPC Daemon
- [x] Create `naravisuals/daemon/__main__.py` with D-Bus service at `org.naravisuals.Daemon`
- [x] Implement widget data providers (system, weather, productivity, integrations)
- [x] Add D-Bus interface: `GetData(widget_id)`, `DataUpdated` signal
- [x] Create systemd user service file
- [ ] Add data caching layer to avoid redundant system calls

### 1.2 C++ Plugin Refactoring
- [x] Remove `QProcess` spawning from `naravisuals-plugin.cpp`
- [x] Add D-Bus client to request widget data from daemon
- [x] Implement C++ renderers (Text, Bar, Graph, IconText)
- [ ] Handle D-Bus disconnection/reconnection

### 1.3 Widget Data Providers
- [x] `naravisuals/data_providers/system.py` - CPU, RAM, disk, network
- [x] `naravisuals/data_providers/weather.py` - Weather API
- [x] `naravisuals/data_providers/productivity.py` - Pomodoro, clipboard
- [x] `naravisuals/data_providers/integrations.py` - MPRIS, updates

### 1.4 Testing & Validation
- [ ] Labwc integration tests
- [ ] Memory profiling (target: <80MB for 10 widgets)
- [ ] D-Bus latency tests (target: <10ms)

---

## Phase 2: Polish & Ecosystem (Medium)

> Enhance UX, add widgets, improve packaging and community.

### 2.1 Theming & Responsiveness
- [x] Panel context integration (height, width, orientation)
- [x] Dark/light mode auto-detection
- [x] Responsive layouts for different panel sizes
- [ ] Animation system for value changes

### 2.2 Widget Enhancements
- [x] SystemMonitor: per-core CPU, temperature sensors
- [x] NetworkMonitor: interface selector, separate up/down graphs
- [ ] BatteryInfo: time remaining, health percentage
- [ ] Weather: multiple locations, forecast display
- [ ] MediaPlayer: album art, playlist browser
- [x] New widgets: TodoList, Currency, Crypto

### 2.3 Manager & Configuration
- [ ] Widget browser tab (install/uninstall)
- [x] Theme preview and apply
- [x] Export/import settings
- [x] Reset panel to stock configuration
- [ ] Configuration profiles

### 2.4 Packaging & Distribution
- [x] Debian/Ubuntu .deb package
- [x] Fedora/RHEL .rpm package
- [x] Flatpak manifest
- [x] Improve PyPI with pyproject.toml

### 2.5 Testing & Documentation
- [x] Unit tests for core modules
- [x] Integration tests for D-Bus
- [ ] API documentation (Sphinx + Doxygen)
- [x] User installation guides
- [ ] Widget development tutorial

### 2.6 Community
- [ ] Submit to awesome-labwc-lxqt
- [ ] Create project website (GitHub Pages)
- [ ] LXQt official plugin submission
- [ ] Widget marketplace concept

---

## Milestones

| Version | Target | Deliverables |
|---------|--------|--------------|
| **v2.0** | Q3 2026 | D-Bus daemon, C++ refactored, Labwc working |
| **v2.1** | Q4 2026 | Theming, new widgets, performance validated |
| **v2.2** | Q1 2027 | Manager redesign, packages, documentation |
| **v3.0** | Q2 2027 | LXQt official, marketplace, ecosystem |
