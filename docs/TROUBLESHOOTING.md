# Troubleshooting Guide

This guide covers common issues and their solutions when installing or running NaraVisuals LXQt Widgets.

## Quick Diagnostics

Run the diagnostic tool first:

```bash
naravisuals-doctor
```

For LXQt-specific configuration checks:

```bash
# Validate LXQt configuration
naravisuals-lxqt-validator

# Scan and fix LXQt configuration issues
naravisuals-lxqt-scanner
naravisuals-lxqt-scanner --fix   # Auto-fix issues
```

This will check:
- System information
- Installation status
- Dependencies
- Service status
- Configuration
- Runtime environment
- LXQt panel configuration
- LXQt theme settings

## Common Issues

### 1. Installation Fails

**Symptom:** `install.sh` exits with errors

**Solutions:**

```bash
# Check if you have write permissions
ls -la ~/.local/

# Try with explicit PREFIX
PREFIX=$HOME/.local ./install.sh

# For system-wide install
sudo PREFIX=/usr/local ./install.sh
```

### 2. Python Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'naravisuals'`

**Solutions:**

```bash
# Check if naravisuals is in your Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Add to path temporarily
export PYTHONPATH=$HOME/.local/lib/naravisuals:$PYTHONPATH

# Or create a symlink
ln -s ~/.local/lib/naravisuals /usr/lib/python3/dist-packages/naravisuals
```

### 3. PyQt6 Not Found

**Symptom:** `ModuleNotFoundError: No module named 'PyQt6'`

**Solutions:**

```bash
# Install PyQt6
# Debian/Ubuntu
sudo apt install python3-pyqt6

# Fedora/RHEL
sudo dnf install python3-pyqt6

# Arch
sudo pacman -S python-pyqt6

# Via pip (not recommended for system packages)
pip install PyQt6
```

### 4. D-Bus Connection Errors

**Symptom:** `Cannot connect to D-Bus session bus`

**Solutions:**

```bash
# Check D-Bus is running
echo $DBUS_SESSION_BUS_ADDRESS

# Start D-Bus if not running
eval $(dbus-launch)

# Check D-Bus service
dbus-send --session --type=method_call --dest=org.freedesktop.DBus \
    /org/freedesktop/DBus org.freedesktop.DBus.ListNames
```

### 5. Daemon Won't Start

**Symptom:** `systemctl --user start naravisuals-daemon` fails

**Solutions:**

```bash
# Check service status
systemctl --user status naravisuals-daemon

# View logs
journalctl --user -u naravisuals-daemon -n 50

# Start manually for debugging
naravisuals-daemon

# Check if port is in use
dbus-send --session --type=method_call --dest=org.naravisuals.Daemon \
    /org/naravisuals/Daemon org.naravisuals.Daemon.ListWidgets
```

### 6. Widgets Not Appearing in Panel

**Symptom:** NaraVisuals widgets don't appear in "Add Widgets" list

**Solutions:**

```bash
# Check desktop files are installed
ls ~/.local/share/applications/naravisuals-*

# Update desktop database
update-desktop-database ~/.local/share/applications/

# Restart lxqt-panel
killall lxqt-panel
lxqt-panel &

# Check panel config
cat ~/.config/lxqt/panel.conf | grep naravisuals
```

### 7. Widget Shows "No Data"

**Symptom:** Widget appears but shows no data or "offline"

**Solutions:**

```bash
# Check daemon is running
systemctl --user status naravisuals-daemon

# Test D-Bus connection
dbus-send --session --type=method_call --dest=org.naravisuals.Daemon \
    /org/naravisuals/Daemon org.naravisuals.Daemon.GetData \
    string:system-monitor

# Restart daemon
systemctl --user restart naravisuals-daemon
```

### 8. Panel Reset Doesn't Work

**Symptom:** Panel reset tool fails or doesn't apply changes

**Solutions:**

```bash
# Check backup exists
ls ~/.config/lxqt/panel-backups/

# Reset manually
cp ~/.config/lxqt/panel-backups/panel_*.conf ~/.config/lxqt/panel.conf

# Restart panel
killall lxqt-panel
lxqt-panel &

# Or use the tool with dry-run first
naravisuals-panel-reset --dry-run --stock
```

### 9. Theme Not Applying

**Symptom:** Widgets don't match system theme

**Solutions:**

```bash
# Check theme config
cat ~/.config/naravisuals/theme.json

# Reset to system theme
rm ~/.config/naravisuals/theme.json

# Open manager and apply theme
naravisuals-manager
```

### 10. NTFS Mount Fails

**Symptom:** NTFS partition mount fails with permission error

**Solutions:**

```bash
# Check pkexec is available
which pkexec

# Test pkexec
pkexec echo "pkexec works"

# Check ntfs-3g is installed
# Debian/Ubuntu
sudo apt install ntfs-3g

# Fedora/RHEL
sudo dnf install ntfs-3g

# Arch
sudo pacman -S ntfs-3g
```

## Log Analysis

### Viewing Logs

```bash
# View recent logs
naravisuals-logs

# Follow logs in real-time
naravisuals-logs -f

# Show only errors
naravisuals-logs -e

# Filter by pattern
naravisuals-logs -g "D-Bus"
```

### Log Locations

| Log Type | Location |
|----------|----------|
| Daemon logs | `journalctl --user -u naravisuals-daemon` |
| System logs | `journalctl -xe` |
| LXQt panel | `journalctl -u lxqt-panel` |

## Getting Help

### Run Diagnostics

```bash
naravisuals-doctor
```

### Collect System Info

```bash
# System info
uname -a
cat /etc/os-release

# Python info
python3 --version
pip3 list | grep -E "PyQt6|psutil|requests|dbus"

# Service status
systemctl --user status naravisuals-daemon

# Recent logs
journalctl --user -u naravisuals-daemon -n 100
```

### Report Issues

When reporting issues, include:

1. Output of `naravisuals-doctor`
2. Output of `systemctl --user status naravisuals-daemon`
3. Recent logs: `journalctl --user -u naravisuals-daemon -n 50`
4. Your distribution and version
5. Steps to reproduce the issue

## Uninstallation

If you need to completely remove NaraVisuals:

```bash
# 1. Stop and disable daemon
systemctl --user stop naravisuals-daemon
systemctl --user disable naravisuals-daemon

# 2. Reset panel to stock
naravisuals-panel-reset --stock

# 3. Remove files
rm -rf ~/.local/lib/naravisuals
rm -rf ~/.local/bin/naravisuals-*
rm -rf ~/.local/share/applications/naravisuals-*
rm -rf ~/.config/naravisuals
rm -rf ~/.config/autostart/naravisuals-*

# 4. Remove systemd service
rm ~/.local/share/systemd/user/naravisuals-daemon.service

# 5. Remove D-Bus service
rm ~/.local/share/dbus-1/services/org.naravisuals.Daemon.service
```
