# NaraVisuals LXQt Widgets - Future Roadmap & TODOs

This document outlines the planned improvements and future architectural changes for the project.

## 1. Wayland Compatibility & IPC Transition 🚨 (High Priority)
* [ ] **Investigate Wayland embedding limitations:** Research how LXQt handles panel plugins under Wayland (since X11 `WId` embedding via `QWindow::fromWinId` will fail).
* [ ] **Migrate to D-Bus IPC:** Instead of embedding Python UI windows directly into the C++ panel plugin, transition to a model where:
    * The C++ plugin renders the actual UI inside the panel.
    * The Python script acts as a backend data provider, sending UI updates and data via D-Bus.
* [ ] **Layer Shell alternative:** If Python UI rendering is strictly required, explore the `wlr-layer-shell` protocol for Wayland to draw native floating overlays over the panel.

## 2. Process Optimization (Single Daemon Architecture) 🚀
* [ ] **Create `naravisuals-daemon`:** Write a centralized background Python service that starts on login.
* [ ] **Modify Widget Logic:** Update individual widgets (`system_monitor`, `weather`, etc.) to run as modules inside the single daemon rather than standalone processes.
* [ ] **Update C++ Plugin (`naravisuals-plugin.cpp`):**
    * Remove `QProcess` spawning for every widget instance.
    * Replace with local socket or D-Bus communication to request the daemon to render/provide data for the specified widget.
* [ ] **Memory Profiling:** Ensure the new daemon uses significantly less RAM/CPU compared to spawning 5+ independent PyQt6 interpreters.

## 3. Dynamic Theming & Panel Integration 🎨
* [ ] **Read Panel Context:** Modify the C++ plugin to pass current panel properties (height, width, orientation: horizontal/vertical) to the Python widgets.
* [x] **Theme Inheritance:** Read the current LXQt `QPalette` (system colors) and apply them to the PyQt6 widgets so they seamlessly blend with light/dark themes.
* [ ] **Responsive Resizing:** Ensure Python widgets dynamically adjust their layouts when the user resizes the LXQt panel.

## 4. Advanced Configuration UI ⚙️
* [x] **Expand `naravisuals-manager`:** Transform the manager from a simple launcher into a full-fledged Settings Hub.
* [x] **Widget Settings Tabs:** Create configuration pages for specific widgets:
    * *Weather:* Location/ZIP code, Celsius/Fahrenheit toggle.
    * *Pomodoro:* Work/Break duration sliders.
    * *Network:* Interface selection dropdown (e.g., `eth0`, `wlan0`).
* [x] **Configuration Storage:** Implement saving/loading settings in standard Linux paths (`~/.config/naravisuals/config.json` or `.ini`).

## 5. Proper Packaging & Distribution 📦
* [x] **Remove Hardcoded Paths:** Refactor `install.sh` to avoid hardcoding `~/.local/` to allow for system-wide installations (`/usr/local/` or `/usr/`).
* [ ] **Debian Package (`.deb`):** Create a proper `debian/` directory with rules to build a standard `.deb` package.
* [x] **Arch Linux AUR:** Write a `PKGBUILD` script for easy installation on Arch-based systems.
* [x] **PyPI Release:** Update `setup.py` to ensure it works flawlessly when installed via `pip install naravisuals-lxqt-widgets` with appropriate entry points.
