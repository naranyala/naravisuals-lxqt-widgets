# Fedora / RHEL Installation Guide

This guide covers installing NaraVisuals LXQt Widgets on RPM-based distributions.

## Supported Distributions

- Fedora 38+
- RHEL 8/9
- CentOS Stream 8/9
- Rocky Linux 8/9
- AlmaLinux 8/9
- Oracle Linux 8/9

## Prerequisites

### Install Build Dependencies

```bash
# Fedora
sudo dnf install -y \
    cmake \
    gcc-c++ \
    make \
    qt6-qtbase-devel \
    lxqt-build-tools-devel \
    python3-devel \
    python3-setuptools

# RHEL/CentOS (enable EPEL first)
sudo dnf install -y epel-release
sudo dnf install -y \
    cmake \
    gcc-c++ \
    make \
    qt6-qtbase-devel \
    lxqt-build-tools-devel \
    python3-devel \
    python3-setuptools
```

### Install Runtime Dependencies

```bash
# Fedora
sudo dnf install -y \
    python3-pyqt6 \
    python3-psutil \
    python3-requests \
    python3-dbus-python \
    python3-notify2 \
    lxqt-panel

# RHEL/CentOS
sudo dnf install -y \
    python3-pyqt6 \
    python3-psutil \
    python3-requests \
    python3-dbus-python \
    python3-notify2 \
    lxqt-panel
```

## Installation Methods

### Method 1: From Source (Recommended)

```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets

# Install to /usr/local (system-wide)
sudo PREFIX=/usr/local ./install.sh

# Or install to ~/.local (user-only)
./install.sh
```

### Method 2: Build RPM Package

```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets

# Setup build environment
./scripts/build-rpm.sh --setup

# Build RPM
./scripts/build-rpm.sh --all

# Install RPM
./scripts/build-rpm.sh --install
```

### Method 3: PyPI (Python Package)

```bash
pip install naravisuals-lxqt-widgets
```

## Post-Installation

### 1. Start the Daemon

```bash
# Start now
systemctl --user start naravisuals-daemon

# Enable auto-start on login
systemctl --user enable naravisuals-daemon
```

### 2. Add Widgets to Panel

1. Right-click on the LXQt panel
2. Select "Add Widgets..."
3. Search for "NaraVisuals"
4. Add desired widgets

### 3. Configure Widgets

```bash
# Open the Settings Hub
naravisuals-manager
```

## Troubleshooting

### Daemon won't start

```bash
# Check daemon status
systemctl --user status naravisuals-daemon

# Check logs
journalctl --user -u naravisuals-daemon

# Manual start for debugging
naravisuals-daemon
```

### D-Bus errors

```bash
# Verify D-Bus session
dbus-send --session --type=method_call --dest=org.naravisuals.Daemon \
    /org/naravisuals/Daemon org.naravisuals.Daemon.ListWidgets
```

### Panel doesn't show widgets

```bash
# Restart panel
killall lxqt-panel
lxqt-panel &

# Check panel config
cat ~/.config/lxqt/panel.conf
```

## Uninstall

### From Source Installation

```bash
# Reset panel to stock first
naravisuals-panel-reset --stock

# Remove files
rm -rf ~/.local/bin/naravisuals-*
rm -rf ~/.local/lib/naravisuals
rm -rf ~/.local/share/applications/naravisuals-*
rm -rf ~/.config/autostart/naravisuals-*

# Stop daemon
systemctl --user stop naravisuals-daemon
systemctl --user disable naravisuals-daemon
```

### From RPM Package

```bash
# Reset panel to stock first
naravisuals-panel-reset --stock

# Remove RPM
sudo rpm -e naravisuals-lxqt-widgets
```

## Building Your Own RPM

See [scripts/build-rpm.sh](scripts/build-rpm.sh) for the RPM build script.

### Custom RPM Build

```bash
# Initialize build environment
./scripts/build-rpm.sh --setup

# Build only source RPM
./scripts/build-rpm.sh --srpm

# Build only binary RPM
./scripts/build-rpm.sh --rpm

# Clean build directory
./scripts/build-rpm.sh --clean
```

## Fedora COPR (Coming Soon)

A COPR repository is planned for easy installation:

```bash
sudo dnf copr enable naranyala/naravisuals
sudo dnf install naravisuals-lxqt-widgets
```

## Links

- [GitHub Repository](https://github.com/naranyala/naravisuals-lxqt-widgets)
- [Bug Reports](https://github.com/naranyala/naravisuals-lxqt-widgets/issues)
- [LXQt Project](https://lxqt-project.org/)
