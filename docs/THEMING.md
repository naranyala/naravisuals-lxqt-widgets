# Theming Guide

Complete guide to customizing NaraVisuals widget appearance.

## Overview

NaraVisuals includes a theme engine that:
- Auto-detects dark/light mode from system QPalette
- Provides responsive layouts based on panel dimensions
- Allows custom color overrides
- Integrates with LXQt panel theming

## Theme Engine

### Location

`naravisuals/core/theme_engine.py`

### Global Instance

```python
from naravisuals.core.theme_engine import theme
```

## Color Properties

### Default Colors

| Property | Default | Description |
|----------|---------|-------------|
| `background` | `#2d2d2d` | Widget background |
| `foreground` | `#ffffff` | Primary text color |
| `accent` | `#3daee9` | Accent/highlight color |
| `border` | `#555555` | Border color |
| `text_primary` | `#ffffff` | Primary text |
| `text_secondary` | `#aaaaaa` | Secondary text |
| `bar_cpu` | `#2ecc71` | CPU usage bar |
| `bar_ram` | `#3498db` | RAM usage bar |
| `bar_disk` | `#9b59b6` | Disk usage bar |
| `bar_swap` | `#e74c3c` | Swap usage bar |
| `bar_network` | `#f39c12` | Network traffic bar |

### Color Format

Colors use standard hex notation:
- Short: `#fff`
- Long: `#ffffff`
- With alpha: `#ffffff80` (not supported)

## Configuration

### Config File

Location: `~/.config/naravisuals/theme.json`

### Example Configuration

```json
{
    "background": "#1a1a2e",
    "foreground": "#eaeaea",
    "accent": "#e94560",
    "border": "#16213e",
    "text_primary": "#eaeaea",
    "text_secondary": "#a0a0a0",
    "bar_cpu": "#0f3460",
    "bar_ram": "#533483",
    "bar_disk": "#e94560",
    "bar_swap": "#ff6b6b",
    "bar_network": "#feca57"
}
```

### Setting Custom Colors

**Via GUI:**

1. Open `naravisuals-manager`
2. Navigate to "Theme" page
3. Edit color values
4. Click "Apply Theme"

**Via D-Bus:**

```python
import dbus

bus = dbus.SessionBus()
proxy = bus.get_object('org.naravisuals.Daemon', '/org/naravisuals/Daemon')
iface = dbus.Interface(proxy, 'org.naravisuals.Daemon')

iface.SetCustomColor('accent', '#ff0000')
```

**Via Command Line:**

```bash
dbus-send --session --type=method_call \
    --dest=org.naravisuals.Daemon \
    /org/naravisuals/Daemon \
    org.naravisuals.Daemon.SetCustomColor \
    string:accent string:#ff0000
```

**Via Python:**

```python
from naravisuals.core.theme_engine import theme

theme.set_custom_color('accent', '#ff0000')
```

### Resetting to System Defaults

**Via GUI:**

1. Open `naravisuals-manager`
2. Navigate to "Theme" page
3. Click "Reset to System"

**Via Python:**

```python
from naravisuals.core.theme_engine import theme

theme._custom_colors.clear()
theme.save_custom_colors()
theme.update_from_palette()
```

## Panel Context

### Dimensions

The theme engine adapts to panel dimensions:

| Panel Height | Font Size | Bar Height | Icon Size | Spacing |
|--------------|-----------|------------|-----------|---------|
| 32px | 7px | 12px | 15px | 3px |
| 48px | 10px | 18px | 22px | 4px |
| 64px | 13px | 24px | 29px | 5px |
| 96px | 20px | 36px | 44px | 8px |

### Setting Panel Context

**Via D-Bus:**

```python
iface.UpdatePanelContext(48, 1920, 'horizontal', 'top')
```

**Via Python:**

```python
from naravisuals.core.theme_engine import theme, PanelContext

ctx = PanelContext(height=64, width=1920, orientation='horizontal', position='top')
theme.update_panel_context(ctx)
```

### Responsive Calculations

```python
# Font size scales with panel height
font_size = theme.get_font_size(base=10)  # Returns 7-20 based on height

# Bar height is 37.5% of panel height
bar_height = theme.get_bar_height()  # Returns 12-48

# Icon size is 46% of panel height
icon_size = theme.get_icon_size()  # Returns 15-44

# Spacing is 8% of panel height
spacing = theme.get_spacing()  # Returns 3-8
```

## Dark/Light Mode

### Auto-Detection

The theme engine automatically detects dark/light mode:

```python
from naravisuals.core.theme_engine import theme

# Check current mode
if theme.is_dark:
    print("Dark mode")
else:
    print("Light mode")
```

### How It Works

1. Reads `QPalette.ColorRole.Window` color
2. Calculates lightness (0-255)
3. If lightness < 128: dark mode
4. If lightness >= 128: light mode

### Manual Override

Override by setting custom colors:

```python
theme.set_custom_color('background', '#ffffff')  # Force light
theme.set_custom_color('background', '#000000')  # Force dark
```

## Applying Themes to Widgets

### Automatic Application

Widgets automatically apply theme on start:

```python
class MyWidget(PanelWidget):
    def start(self):
        self._apply_theme()  # Called automatically
        super().start()
```

### Manual Application

```python
from naravisuals.core.theme_engine import theme

# Apply to any widget
theme.apply_to_widget(my_widget)

# Get stylesheet
stylesheet = theme.get_stylesheet()
my_widget.setStyleSheet(stylesheet)
```

### Custom Styles

Override specific elements:

```python
my_widget.setStyleSheet("""
    QWidget {
        background-color: #ff0000;
        color: #ffffff;
    }
    QLabel {
        font-size: 14px;
        font-weight: bold;
    }
""")
```

## Theme Presets

### Nord Theme

```json
{
    "background": "#2e3440",
    "foreground": "#d8dee9",
    "accent": "#88c0d0",
    "border": "#3b4252",
    "text_primary": "#d8dee9",
    "text_secondary": "#a0a0a0",
    "bar_cpu": "#a3be8c",
    "bar_ram": "#81a1c1",
    "bar_disk": "#b48ead",
    "bar_swap": "#bf616a",
    "bar_network": "#ebcb8b"
}
```

### Dracula Theme

```json
{
    "background": "#282a36",
    "foreground": "#f8f8f2",
    "accent": "#bd93f9",
    "border": "#44475a",
    "text_primary": "#f8f8f2",
    "text_secondary": "#6272a4",
    "bar_cpu": "#50fa7b",
    "bar_ram": "#8be9fd",
    "bar_disk": "#bd93f9",
    "bar_swap": "#ff5555",
    "bar_network": "#f1fa8c"
}
```

### Gruvbox Theme

```json
{
    "background": "#282828",
    "foreground": "#ebdbb2",
    "accent": "#d79921",
    "border": "#3c3836",
    "text_primary": "#ebdbb2",
    "text_secondary": "#928374",
    "bar_cpu": "#b8bb26",
    "bar_ram": "#83a598",
    "bar_disk": "#d3869b",
    "bar_swap": "#fb4934",
    "bar_network": "#fabd2f"
}
```

### Catppuccin Mocha

```json
{
    "background": "#1e1e2e",
    "foreground": "#cdd6f4",
    "accent": "#cba6f7",
    "border": "#313244",
    "text_primary": "#cdd6f4",
    "text_secondary": "#6c7086",
    "bar_cpu": "#a6e3a1",
    "bar_ram": "#89b4fa",
    "bar_disk": "#cba6f7",
    "bar_swap": "#f38ba8",
    "bar_network": "#f9e2af"
}
```

## Troubleshooting

### Theme Not Applying

1. Check config file exists:
   ```bash
   cat ~/.config/naravisuals/theme.json
   ```

2. Restart daemon:
   ```bash
   systemctl --user restart naravisuals-daemon
   ```

3. Check for JSON errors:
   ```bash
   python3 -c "import json; json.load(open('~/.config/naravisuals/theme.json'))"
   ```

### Colors Not Matching

1. Ensure hex format is correct: `#rrggbb`
2. Check QPalette integration:
   ```python
   from PyQt6.QtWidgets import QApplication
   app = QApplication.instance()
   palette = app.palette()
   print(palette.color(palette.ColorRole.Window).name())
   ```

### Panel Context Not Updating

1. Verify D-Bus connection:
   ```bash
   dbus-send --session --type=method_call \
       --dest=org.naravisuals.Daemon \
       /org/naravisuals/Daemon \
       org.naravisuals.Daemon.GetPanelContext
   ```

2. Check panel height in LXQt settings
