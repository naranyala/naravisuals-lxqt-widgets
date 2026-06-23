# Deployment Guide

Guide for deploying NaraVisuals LXQt Widgets in various environments.

## Installation Methods

### 1. From Source (Recommended)

```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets

# User-only installation
./install.sh

# System-wide installation
sudo PREFIX=/usr/local ./install.sh
```

### 2. PyPI

```bash
pip install naravisuals-lxqt-widgets
```

### 3. Arch Linux (AUR)

```bash
makepkg -si
```

### 4. Fedora/RHEL (RPM)

```bash
./scripts/build-rpm.sh --setup
./scripts/build-rpm.sh --all
sudo ./scripts/build-rpm.sh --install
```

### 5. Debian/Ubuntu

```bash
dpkg-buildpackage -us -uc
sudo dpkg -i ../naravisuals-lxqt-widgets_*.deb
```

### 6. Flatpak

```bash
flatpak-builder --user --install --force-clean build-dir packaging/flatpak/org.naravisuals.lxqt-widgets.yml
```

## Post-Installation

### 1. Start Daemon

```bash
# Start now
systemctl --user start naravisuals-daemon

# Enable auto-start
systemctl --user enable naravisuals-daemon
```

### 2. Add Widgets to Panel

1. Right-click LXQt panel
2. Select "Add Widgets..."
3. Search for "NaraVisuals"
4. Add desired widgets

### 3. Configure Widgets

```bash
naravisuals-manager
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PREFIX` | `~/.local` | Installation prefix |
| `XDG_CONFIG_HOME` | `~/.config` | Configuration directory |
| `DBUS_SESSION_BUS_ADDRESS` | (auto) | D-Bus session bus |

## Systemd Service

### Service File

Location: `~/.local/share/systemd/user/naravisuals-daemon.service`

### Manual Control

```bash
# Start
systemctl --user start naravisuals-daemon

# Stop
systemctl --user stop naravisuals-daemon

# Restart
systemctl --user restart naravisuals-daemon

# Status
systemctl --user status naravisuals-daemon

# Logs
journalctl --user -u naravisuals-daemon -f
```

### Service Configuration

Edit service file:

```bash
systemctl --user edit naravisuals-daemon
```

Add overrides:

```ini
[Service]
Environment="PYTHONPATH=/custom/path"
Restart=on-failure
RestartSec=5
```

## D-Bus Configuration

### Service File

Location: `~/.local/share/dbus-1/services/org.naravisuals.Daemon.service`

### Manual Registration

```bash
dbus-send --session --type=method_call \
    --dest=org.freedesktop.DBus \
    /org/freedesktop/DBus \
    org.freedesktop.DBus.RequestName \
    string:org.naravisuals.Daemon \
    uint32:0
```

## Autostart

### Desktop Entry

Location: `~/.config/autostart/naravisuals-daemon.desktop`

### Disable Autostart

```bash
rm ~/.config/autostart/naravisuals-daemon.desktop
```

## Multi-User Setup

### System-Wide Installation

```bash
sudo PREFIX=/usr/local ./install.sh
```

### Per-User Configuration

Each user needs:

1. D-Bus session bus
2. Systemd user instance
3. LXQt panel

### Shared Configuration

```bash
# Share config between users
sudo ln -s /etc/naravisuals ~/.config/naravisuals
```

## Container Deployment

### Docker

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pyqt6 python3-psutil python3-requests python3-dbus \
    lxqt-panel dbus-x11

COPY . /opt/naravisuals
WORKDIR /opt/naravisuals

RUN pip install -e .

CMD ["naravisuals-daemon"]
```

### Podman

```bash
podman build -t naravisuals .
podman run -it naravisuals
```

## Remote Deployment

### Ansible Playbook

```yaml
- name: Install NaraVisuals
  hosts: lxqt-servers
  become: yes
  tasks:
    - name: Clone repository
      git:
        repo: https://github.com/naranyala/naravisuals-lxqt-widgets.git
        dest: /opt/naravisuals

    - name: Install dependencies
      package:
        name:
          - python3-pyqt6
          - python3-psutil
          - python3-requests
          - python3-dbus
        state: present

    - name: Install NaraVisuals
      shell: PREFIX=/usr/local ./install.sh
      args:
        chdir: /opt/naravisuals

    - name: Enable daemon
      systemd:
        name: naravisuals-daemon
        enabled: yes
        scope: user
```

### SSH Deployment

```bash
# Deploy to remote host
ssh user@host "cd /opt/naravisuals && git pull && ./install.sh"
```

## Monitoring

### Health Check

```bash
# Check daemon status
systemctl --user is-active naravisuals-daemon

# Check D-Bus service
dbus-send --session --type=method_call \
    --dest=org.naravisuals.Daemon \
    /org/naravisuals/Daemon \
    org.naravisuals.Daemon.ListWidgets
```

### Metrics

```bash
# Memory usage
ps aux | grep naravisuals-daemon

# CPU usage
top -p $(pgrep -f naravisuals-daemon)
```

## Backup

### Configuration Backup

```bash
# Backup config
tar czf naravisuals-config-backup.tar.gz ~/.config/naravisuals/

# Restore config
tar xzf naravisuals-config-backup.tar.gz -C ~/
```

### Panel Backup

```bash
# Create backup
naravisuals-panel-reset --save-backup

# List backups
ls ~/.config/lxqt/panel-backups/

# Restore backup
naravisuals-panel-reset --backup
```

## Upgrade

### From Source

```bash
cd naravisuals-lxqt-widgets
git pull
./install.sh
systemctl --user restart naravisuals-daemon
```

### From Package

```bash
# Arch
sudo pacman -Syu naravisuals-lxqt-widgets

# Fedora
sudo dnf upgrade naravisuals-lxqt-widgets

# Debian
sudo apt upgrade naravisuals-lxqt-widgets
```

## Rollback

### Previous Version

```bash
# Stop daemon
systemctl --user stop naravisuals-daemon

# Restore panel
naravisuals-panel-reset --backup

# Reinstall previous version
git checkout v1.0.0
./install.sh

# Start daemon
systemctl --user start naravisuals-daemon
```

## Uninstall

### Complete Removal

```bash
# Stop and disable daemon
systemctl --user stop naravisuals-daemon
systemctl --user disable naravisuals-daemon

# Reset panel
naravisuals-panel-reset --stock

# Remove files
rm -rf ~/.local/lib/naravisuals
rm -rf ~/.local/bin/naravisuals-*
rm -rf ~/.local/share/applications/naravisuals-*
rm -rf ~/.config/naravisuals
rm -rf ~/.config/autostart/naravisuals-*

# Remove systemd files
rm ~/.local/share/systemd/user/naravisuals-daemon.service
rm ~/.local/share/dbus-1/services/org.naravisuals.Daemon.service

# Reload systemd
systemctl --user daemon-reload
```
