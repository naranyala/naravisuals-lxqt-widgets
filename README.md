# NaraVisuals LXQt Widgets

Next-Generation, API-Driven Panel Widgets for the LXQt Desktop Environment.

[![License: GPL3](https://img.shields.io/badge/License-GPL3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-yellow.svg)](https://riverbankcomputing.com/software/pyqt/)

NaraVisuals provides advanced customization and extended functionality to the lightweight LXQt desktop. By integrating a highly performant native C++ panel plugin with a feature-rich Python and PyQt6 daemon, it allows for the embedding of complex UI elements directly into the LXQt panel while maintaining optimal system performance.

## Architecture & Directory Structure

The repository is built upon a scalable, domain-driven architecture designed to separate core logic, configuration, and user interfaces.

* `naravisuals/core/`: Contains the foundational `base_widget` classes, asynchronous execution utilities (`async_utils`), and configuration parsers (`config_manager`).
* `naravisuals/manager/`: Houses the centralized Settings Hub (`naravisuals-manager`) utilized for visually configuring both the native LXQt panel and individual widgets.
* `naravisuals/widgets/`: Contains all widget implementations categorized strictly by their domain (`system/`, `productivity/`, `integrations/`).
* `native-plugin/`: The native C++ bridge responsible for executing and rendering the Python instances directly inside the X11 LXQt panel.

## Included Modules

The repository currently provides 13 highly optimized widgets, structurally categorized for easy maintenance.

### System
* **System Monitor:** Real-time tracking of CPU, RAM, Disk, and SWAP.
* **Network Monitor:** Live traffic graphing for specified interfaces.
* **Battery Info:** Hardware battery percentage and status monitoring.
* **Uptime Counter:** Constant tracking of system uptime parameters.
* **Ping Monitor:** Asynchronous monitoring of internet latency.
* **Kernel Version:** Display of the currently active Linux kernel.

### Productivity
* **Pomodoro Timer:** Standardized productivity timer with configurable intervals.
* **Quick Notes:** Direct panel-integrated text storage.
* **Clipboard Manager:** Persistent clipboard history tracking.

### Integrations
* **Weather:** Configurable location-based meteorological data.
* **Media Player:** MPRIS-compatible controls for external media clients.
* **System Updates:** Background verification of pending package updates.
* **Tray Enhanced:** Extended system tray functionality.

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

To configure widget parameters and global LXQt panel settings, launch the unified Settings Hub from your terminal or application launcher:
```bash
naravisuals-manager
```

## Roadmap

* Implement complete Wayland migration (Layer Shell and native D-Bus IPC).
* Finalize PyPI distribution packaging (`pip install naravisuals`).
* Abstract data providers entirely from the PyQt UI layer.
