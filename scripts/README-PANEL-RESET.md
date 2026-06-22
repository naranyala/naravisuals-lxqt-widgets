# Panel Reset Tool

A CLI and GUI tool to reset the LXQt panel to stock configuration.

## Features

- **Reset to Stock**: Remove all NaraVisuals widgets and restore default LXQt panel
- **Backup & Restore**: Automatically backup before changes, restore from backup
- **Dry Run**: Preview changes without modifying files
- **GUI Integration**: Button in NaraVisuals Settings Hub

## CLI Usage

```bash
# Reset to stock LXQt panel (no NaraVisuals widgets)
naravisuals-panel-reset --stock

# Backup current config, then reset to stock
naravisuals-panel-reset --save-backup --stock

# Restore from last backup
naravisuals-panel-reset --backup

# Preview changes without applying
naravisuals-panel-reset --dry-run --stock
```

## GUI Usage

1. Open NaraVisuals Settings Hub: `naravisuals-manager`
2. Click "Panel Organizer" in the sidebar
3. Click "Reset to Stock" button in the top toolbar
4. Confirm the reset in the dialog

Or use the quick reset button in the sidebar:
- Click "↩ Reset to Stock" button

## Stock Configuration

The stock configuration (`packaging/stock-panel.conf`) includes:

- **Main Menu** (fancymenu or mainmenu)
- **Desktop Switcher**
- **Taskbar**
- **Status Notifier** (system tray)
- **Volume Control**
- **World Clock**
- **Show Desktop**

All NaraVisuals widgets are removed in the stock configuration.

## Backup Location

Backups are stored in:
```
~/.config/lxqt/panel-backups/
```

Files are named: `panel_YYYYMMDD_HHMMSS.conf`

## Files

- `scripts/naravisuals-panel-reset` - CLI tool
- `packaging/stock-panel.conf` - Default panel configuration
- `naravisuals/manager/app.py` - GUI with reset buttons
