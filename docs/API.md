# D-Bus API Reference

This document describes the D-Bus interface exposed by the NaraVisuals daemon.

## Service Information

| Property | Value |
|----------|-------|
| Bus Name | `org.naravisuals.Daemon` |
| Object Path | `/org/naravisuals/Daemon` |
| Interface | `org.naravisuals.Daemon` |
| Bus Type | Session |

## Methods

### GetData

Returns current data for a widget as JSON string.

```python
# Python example
import dbus

bus = dbus.SessionBus()
proxy = bus.get_object('org.naravisuals.Daemon', '/org/naravisuals/Daemon')
iface = dbus.Interface(proxy, 'org.naravisuals.Daemon')

data = iface.GetData('system-monitor')
# Returns: '{"cpu_percent": 45.2, "ram_percent": 67.8, ...}'
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `widget_id` | `string` | Widget identifier |

**Returns:** `string` - JSON-encoded widget data

**Widget IDs:**

| ID | Data Structure |
|----|----------------|
| `system-monitor` | `{"cpu_percent", "cpu_per_core", "ram_percent", "disk_percent", "swap_percent", "net_rate", "temperatures"}` |
| `network-monitor` | `{"interface", "interfaces", "upload_rate", "download_rate", "total_rate"}` |
| `battery` | `{"available", "percent", "charging", "time_left"}` |
| `uptime` | `{"days", "hours", "minutes", "formatted"}` |
| `ping-monitor` | `{"host", "latency_ms", "reachable"}` |
| `kernel-version` | `{"kernel", "full", "machine"}` |
| `weather` | `{"city", "available", "temp_c", "description", "humidity", "wind_kmph"}` |
| `pomodoro` | `{"state", "is_work", "time_left", "pomodoro_count"}` |
| `quick-notes` | `{"notes", "count"}` |
| `clipboard-manager` | `{"history", "count"}` |
| `media-player` | `{"available", "playing", "title", "artist"}` |
| `system-updates` | `{"distro", "update_count", "has_updates"}` |
| `todo-list` | `{"todos", "pending_count", "completed_count"}` |
| `currency` | `{"base", "rates", "available"}` |
| `crypto` | `{"coins", "available"}` |
| `ntfs-mount` | `{"partitions", "mounted", "mount_base"}` |

**Example Response (system-monitor):**

```json
{
    "cpu_percent": 45.2,
    "cpu_per_core": [32.1, 58.3, 41.7, 48.9],
    "cpu_count": 4,
    "ram_percent": 67.8,
    "ram_used": "5.4 GB",
    "ram_total": "8.0 GB",
    "disk_percent": 72.1,
    "disk_used": "180.5 GB",
    "disk_total": "250.0 GB",
    "swap_percent": 12.3,
    "net_rate": "1.2 MB/s",
    "temperatures": {"coretemp": 45.0}
}
```

---

### ListWidgets

Returns list of all registered widget IDs.

```python
widgets = iface.ListWidgets()
# Returns: '["system-monitor", "weather", "pomodoro", ...]'
```

**Returns:** `string` - JSON array of widget IDs

---

### SetConfig

Sets a configuration value for a widget.

```python
iface.SetConfig('weather', 'city', 'London')
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `widget_id` | `string` | Widget identifier |
| `key` | `string` | Configuration key |
| `value` | `string` | Configuration value |

**Returns:** Nothing

---

### GetConfig

Returns all configuration for a widget.

```python
config = iface.GetConfig('weather')
# Returns: '{"city": "London", "unit": "Celsius"}'
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `widget_id` | `string` | Widget identifier |

**Returns:** `string` - JSON object of configuration

---

### ReloadWidget

Reloads a specific widget provider.

```python
iface.ReloadWidget('weather')
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `widget_id` | `string` | Widget identifier |

**Returns:** Nothing

---

### UpdatePanelContext

Updates panel dimensions and orientation.

```python
iface.UpdatePanelContext(48, 1920, 'horizontal', 'top')
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `height` | `int` | Panel height in pixels |
| `width` | `int` | Panel width in pixels |
| `orientation` | `string` | `"horizontal"` or `"vertical"` |
| `position` | `string` | `"top"`, `"bottom"`, `"left"`, or `"right"` |

**Returns:** Nothing

---

### GetTheme

Returns current theme colors as JSON.

```python
theme = iface.GetTheme()
# Returns: '{"background": "#2d2d2d", "foreground": "#ffffff", ...}'
```

**Returns:** `string` - JSON object of theme colors

---

### SetCustomColor

Sets a custom color override.

```python
iface.SetCustomColor('accent', '#ff0000')
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `name` | `string` | Color name (see ThemeColors) |
| `color` | `string` | Hex color code |

**Returns:** Nothing

---

### GetPanelContext

Returns current panel context as JSON.

```python
context = iface.GetPanelContext()
# Returns: '{"height": 48, "width": 1920, "orientation": "horizontal", "position": "top"}'
```

**Returns:** `string` - JSON object of panel context

## Signals

### dataUpdated

Emitted when widget data changes.

```python
# Connect to signal
bus.add_match_string(
    "type='signal',interface='org.naravisuals.Daemon',member='dataUpdated'"
)
bus.process_matching_rules()

def on_data_updated(widget_id, json_data):
    print(f"Widget {widget_id}: {json_data}")

bus.add_message_handler(on_data_updated)
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `widget_id` | `string` | Widget identifier |
| `json_data` | `string` | JSON-encoded widget data |

**Emission Frequency:** Every 2 seconds (configurable)

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `org.freedesktop.DBus.Error.ServiceUnknown` | Daemon not running | Start daemon: `systemctl --user start naravisuals-daemon` |
| `org.freedesktop.DBus.Error.NoReply` | Daemon timeout | Check daemon logs: `journalctl --user -u naravisuals-daemon` |
| `org.freedesktop.DBus.Error.AccessDenied` | Permission denied | Ensure running in user session |

### Python Error Handling

```python
import dbus
from dbus.exceptions importDBusException

try:
    data = iface.GetData('system-monitor')
except dbus.exceptions.DBusException as e:
    if 'ServiceUnknown' in str(e):
        print("Daemon not running")
    else:
        print(f"D-Bus error: {e}")
```

### C++ Error Handling

```cpp
if (!mDBus->isValid()) {
    qWarning("D-Bus connection invalid");
    return;
}

QDBusReply<QString> reply = mDBus->call("GetData", mSelectedWidget);
if (!reply.isValid()) {
    qWarning("D-Bus call failed: %s", reply.error().message());
    return;
}
```

## Usage Examples

### Command Line

```bash
# Get system monitor data
dbus-send --session --type=method_call \
    --dest=org.naravisuals.Daemon \
    /org/naravisuals/Daemon \
    org.naravisuals.Daemon.GetData \
    string:system-monitor

# List widgets
dbus-send --session --type=method_call \
    --dest=org.naravisuals.Daemon \
    /org/naravisuals/Daemon \
    org.naravisuals.Daemon.ListWidgets
```

### Python

```python
import dbus
import json

bus = dbus.SessionBus()
proxy = bus.get_object('org.naravisuals.Daemon', '/org/naravisuals/Daemon')
iface = dbus.Interface(proxy, 'org.naravisuals.Daemon')

# Get data
data = json.loads(iface.GetData('system-monitor'))
print(f"CPU: {data['cpu_percent']}%")
print(f"RAM: {data['ram_percent']}%")
```

### C++

```cpp
#include <QDBusInterface>
#include <QDBusReply>
#include <QJsonDocument>
#include <QJsonObject>

QDBusInterface iface("org.naravisuals.Daemon",
                     "/org/naravisuals/Daemon",
                     "org.naravisuals.Daemon");

QDBusReply<QString> reply = iface.call("GetData", "system-monitor");
if (reply.isValid()) {
    QJsonDocument doc = QJsonDocument::fromJson(reply.value().toUtf8());
    QJsonObject data = doc.object();
    double cpu = data["cpu_percent"].toDouble();
    qDebug() << "CPU:" << cpu << "%";
}
```

### Bash Script

```bash
#!/bin/bash

# Function to get widget data
get_widget_data() {
    dbus-send --session --type=method_call \
        --dest=org.naravisuals.Daemon \
        /org/naravisuals/Daemon \
        org.naravisuals.Daemon.GetData \
        string:"$1" 2>/dev/null | \
        sed 's/.*string "\(.*\)"/\1/'
}

# Get system monitor data
DATA=$(get_widget_data "system-monitor")
echo "System Monitor: $DATA"
```
