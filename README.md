# NaraVisuals LXQt Widgets

Next-Generation, API-Driven Panel Widgets for the LXQt Desktop Environment.

[![License: GPL3](https://img.shields.io/badge/License-GPL3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-yellow.svg)](https://riverbankcomputing.com/software/pyqt/)

NaraVisuals provides advanced customization and extended functionality to the lightweight LXQt desktop. By integrating a highly performant native C++ panel plugin with a feature-rich Python and PyQt6 daemon, it allows for the embedding of complex UI elements directly into the LXQt panel while maintaining optimal system performance.

## Architecture & Design

Traditional panel widgets are often static and difficult to extend. NaraVisuals modernizes panel applets by utilizing Python for rapid development and API integration.

* **Dynamic Theming:** All widgets automatically inherit and adapt to the active LXQt `QPalette` system, supporting seamless transitions between light and dark themes.
* **Centralized Configuration:** Manual configuration files are deprecated in favor of a unified GUI Settings Hub (`naravisuals-manager`).
* **Client-Server Model:** Widget UI rendering executes within the panel, while heavy processing and data retrieval are offloaded to a headless background Python service to keep the LXQt session responsive.
* **Extensibility:** Developing a new panel widget requires minimal Python code, allowing for rapid integration with system processes and external APIs.

## Included Modules

The repository currently provides 16 widgets, ranging from standard desktop utilities to deep system-level integrations.

### Core Utilities
* **System Monitor:** Real-time tracking of CPU, RAM, Disk, and SWAP.
* **Network Monitor:** Live traffic graphing for specified interfaces (e.g., `eth0`, `wlan0`).
* **Clipboard Manager:** Persistent clipboard history tracking.
* **Quick Notes:** Direct panel-integrated text storage.
* **Pomodoro Timer:** Standardized productivity timer.
* **Media Player:** MPRIS-compatible controls for external media clients.

### System & Hardware Integrations
* **Container Radar:** Live dashboard for monitoring Docker and Podman instances.
* **GPU Matrix:** Direct hooks into `nvidia-smi` for thermal and VRAM utilization tracking.
* **Bluetooth Radar:** D-Bus integrated scanning for nearby Bluetooth devices.
* **Audio Visualizer:** Animated frequency spectrum matrix.
* **System Log Ticker:** Live streaming output of critical `journalctl` panics and errors.
* **Smart Home Toggle:** Configurable webhook execution for endpoints such as Home Assistant.

## Installation

### Arch Linux (AUR)
A `PKGBUILD` is provided for seamless installation on Arch-based distributions:
```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
makepkg -si
```

### Debian, Ubuntu, and Fedora
Ensure the following build dependencies are installed: `cmake`, `lxqt-build-tools`, and `python3-pyqt6`. Then, execute the provided installation script:
```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
PREFIX=/usr ./install.sh
```

## Usage & Configuration

Once the installation is complete, right-click the LXQt panel, select **Add Widgets**, and search for `NaraVisuals`.

To configure widget parameters, launch the unified Settings Hub from your terminal or application launcher:
```bash
naravisuals-manager
```
This interface allows for the configuration of environmental variables such as weather locations, network interfaces, and external API endpoints.

## Roadmap

* Implement complete Wayland migration (Layer Shell and native D-Bus IPC).
* Finalize PyPI distribution packaging (`pip install naravisuals`).
* Integrate `evdev` for the APM Counter widget.
* Implement Pipewire PCM hooks for the Audio Visualizer.
