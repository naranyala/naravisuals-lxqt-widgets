# Changelog

All notable changes to NaraVisuals LXQt Widgets will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-22

### Added

#### Architecture
- D-Bus IPC daemon for Wayland compatibility
- Single process architecture (replaces per-widget QProcess)
- Theme engine with panel context and responsive layouts
- Comprehensive error handling and logging

#### Widgets
- NTFS Mount widget with pkexec support
- Todo List widget with priorities
- Currency Exchange widget
- Crypto Prices widget
- Per-core CPU monitoring
- Network interface selector
- Temperature sensor display

#### GUI
- All-in-one Control Center (7 pages)
  - Dashboard with live stats
  - Widget browser with filtering
  - Panel organizer with drag-and-drop
  - Theme editor with preview
  - Backup and restore manager
  - Log viewer with filtering
  - About page
- Legacy manager preserved

#### Tools
- Diagnostic tool (naravisuals-doctor)
- Log viewer (naravisuals-logs)
- Panel reset tool with backup
- Archive script with user confirmation

#### Packaging
- Debian/Ubuntu .deb packaging
- Fedora/RHEL .rpm packaging
- Flatpak manifest
- PyPI with pyproject.toml
- Arch Linux PKGBUILD

#### Documentation
- Professional README with architecture diagrams
- D-Bus API reference
- Widget reference guide
- Theming guide
- Developer guide
- Deployment guide
- Security considerations
- Contributing guide
- Troubleshooting guide

### Changed
- C++ plugin refactored to use D-Bus client
- Install script rewritten with error handling
- Base widget classes use theme engine
- Configuration manager with validation

### Fixed
- Weather provider config path handling
- Widget test assertions
- Panel reset backup handling

### Removed
- run.sh (replaced by individual launcher scripts)

## [1.0.0] - 2026-06-15

### Added
- Initial release
- 13 widgets:
  - System Monitor, Network Monitor, Battery Info
  - Uptime Counter, Ping Monitor, Kernel Version
  - Weather, Media Player, System Updates, Tray Enhanced
  - Pomodoro Timer, Quick Notes, Clipboard Manager
- Native C++ panel plugin
- PyQt6 GUI manager
- Standalone widget launchers
- Panel template import/export
- Panel reset to stock configuration
- Arch Linux PKGBUILD
- Basic documentation

## [0.9.0] - 2026-06-10

### Added
- Beta release for testing
- Core widget framework
- Basic system monitoring
- Weather widget
- Pomodoro timer

### Known Issues
- X11-only (no Wayland support)
- Multiple processes per widget
- Limited error handling

## [0.8.0] - 2026-06-01

### Added
- Alpha release
- Project structure
- Basic widget classes
- Proof of concept

---

## Release Links

- [2.0.0]: https://github.com/naranyala/naravisuals-lxqt-widgets/releases/tag/v2.0.0
- [1.0.0]: https://github.com/naranyala/naravisuals-lxqt-widgets/releases/tag/v1.0.0
- [0.9.0]: https://github.com/naranyala/naravisuals-lxqt-widgets/releases/tag/v0.9.0
- [0.8.0]: https://github.com/naranyala/naravisuals-lxqt-widgets/releases/tag/v0.8.0
