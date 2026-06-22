<div align="center">
  <h1>🌌 NaraVisuals LXQt Widgets</h1>
  <p><strong>Next-Generation, API-Driven Panel Widgets for the LXQt Desktop Environment</strong></p>
  
  [![License: GPL3](https://img.shields.io/badge/License-GPL3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
  [![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
  [![PyQt6](https://img.shields.io/badge/GUI-PyQt6-yellow.svg)](https://riverbankcomputing.com/software/pyqt/)
</div>

<br />

> **NaraVisuals** brings unprecedented power, customization, and aesthetic flair to the lightweight LXQt desktop. By bridging a blazing-fast C++ native panel plugin with a feature-rich Python/PyQt6 daemon, it allows you to embed complex UI elements directly into your LXQt panel—without sacrificing performance.

## ✨ Why NaraVisuals?

Traditional panel widgets are often static, hard to configure, and difficult to extend. NaraVisuals completely revolutionizes panel applets by bringing the power of Python directly to your desktop.

* 🎨 **Dynamic Theming:** All widgets instantly adapt to your active LXQt theme (`QPalette`), supporting flawless light/dark mode transitions out of the box.
* ⚙️ **Unified GUI Settings Hub:** No more manual config files! Tweak your widget settings visually via the beautiful `naravisuals-manager`.
* 🧩 **Client-Server Architecture:** Widgets render seamlessly in the panel but execute in the background via a headless Python service, keeping LXQt fast and responsive.
* 🛠️ **Extensible:** Writing a new panel widget takes just a few lines of Python. Connect to any API or system process effortlessly!

## 🚀 The Widget Arsenal

We ship with **16 powerful widgets**, ranging from essential productivity tools to deep system-level API integrations.

### 💼 Essentials
* **System Monitor:** Real-time CPU, RAM, Disk, and SWAP tracking.
* **Network Monitor:** Live traffic graphs (`eth0`, `wlan0`).
* **Clipboard Manager:** Complete clipboard history tracking.
* **Quick Notes:** Jot down instant sticky notes directly from the panel.
* **Pomodoro Timer:** Beautiful productivity timer.
* **Media Player:** MPRIS-compatible controls for Spotify, VLC, and more.

### 🧪 Experimental & Hardware Integrations
* **🐳 Container Radar:** Live dashboard for running Docker/Podman containers.
* **🎮 GPU Matrix:** Direct `nvidia-smi` hooks for thermal and VRAM utilization tracking.
* **📶 Bluetooth Radar:** D-Bus integrated scanning for nearby devices.
* **🎵 Audio Visualizer:** 20fps animated frequency spectrum matrix.
* **🚨 System Log Ticker:** Live streaming marquee of critical `journalctl` panics and errors.
* **💡 Smart Home Toggle:** One-click webhook executions for Home Assistant.

## 📦 Installation

### Arch Linux (AUR)
We provide a `PKGBUILD` for seamless installation on Arch-based distributions:
```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
makepkg -si
```

### Generic Linux (Debian, Ubuntu, Fedora)
Ensure you have `cmake`, `lxqt-build-tools`, and `python3-pyqt6` installed, then run our universal installer:
```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
PREFIX=/usr ./install.sh
```

## ⚙️ Usage & Configuration

Once installed, simply right-click your LXQt panel -> **Add Widgets...** and search for `NaraVisuals`.

To configure your widgets, launch the unified Settings Hub from your terminal or application launcher:
```bash
naravisuals-manager
```
From here, you can set weather locations, pomodoro durations, network interfaces, and more!

## 🗺️ Roadmap
- [ ] Complete Wayland migration (Layer Shell & D-Bus IPC implementation).
- [ ] PyPI distribution (`pip install naravisuals`).
- [ ] Evdev integration for APM Counter widget.
- [ ] Pipewire PCM hooks for the Audio Visualizer.

---
<div align="center">
  <i>Made with ❤️ for the Linux Desktop Community.</i>
</div>
