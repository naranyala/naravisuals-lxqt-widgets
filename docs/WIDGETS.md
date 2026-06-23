# Widgets Reference

Complete documentation for all NaraVisuals widgets.

## System Widgets

### System Monitor

Real-time tracking of CPU, RAM, disk, and network usage.

**Widget ID:** `system-monitor`

**Data Structure:**

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
    "swap_used": "1.2 GB",
    "swap_total": "8.0 GB",
    "net_rate": "1.2 MB/s",
    "temperatures": {"coretemp": 45.0}
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** 2 seconds

**Renderer:** SystemMonitorRenderer (composite bar widget)

---

### Network Monitor

Live network traffic monitoring with interface selection.

**Widget ID:** `network-monitor`

**Data Structure:**

```json
{
    "interface": "all",
    "interfaces": ["eth0", "wlan0", "lo"],
    "bytes_sent": 1234567890,
    "bytes_recv": 9876543210,
    "upload_rate": "1.2 MB/s",
    "download_rate": "5.6 MB/s",
    "total_rate": "6.8 MB/s",
    "packets_sent": 1234567,
    "packets_recv": 9876543
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `interface` | `string` | `"all"` | Network interface to monitor |

**Update Interval:** 1 second

**Renderer:** TextRenderer

---

### Battery Info

Hardware battery status monitoring.

**Widget ID:** `battery`

**Data Structure:**

```json
{
    "available": true,
    "percent": 85.5,
    "charging": false,
    "time_left": "2h 30m"
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** 30 seconds

**Renderer:** IconTextRenderer

---

### Uptime Counter

System uptime display.

**Widget ID:** `uptime`

**Data Structure:**

```json
{
    "days": 5,
    "hours": 12,
    "minutes": 34,
    "seconds": 56,
    "formatted": "5d 12h 34m"
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** 60 seconds

**Renderer:** TextRenderer

---

### Ping Monitor

Network latency monitoring.

**Widget ID:** `ping-monitor`

**Data Structure:**

```json
{
    "host": "8.8.8.8",
    "latency_ms": 12.5,
    "reachable": true
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `host` | `string` | `"8.8.8.8"` | Host to ping |

**Update Interval:** 30 seconds

**Renderer:** TextRenderer

---

### Kernel Version

Active kernel information.

**Widget ID:** `kernel-version`

**Data Structure:**

```json
{
    "kernel": "6.5.0-44-generic",
    "full": "#44-Ubuntu SMP ...",
    "machine": "x86_64"
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** 300 seconds

**Renderer:** TextRenderer

---

### NTFS Mount

Mount/unmount NTFS partitions with pkexec.

**Widget ID:** `ntfs-mount`

**Data Structure:**

```json
{
    "partitions": [
        {
            "name": "/dev/sda1",
            "fstype": "ntfs",
            "size": "500G",
            "label": "Data",
            "uuid": "1234-5678",
            "is_ntfs": true
        }
    ],
    "mounted": [
        {"source": "/dev/sda1", "target": "/media/user/Data"}
    ],
    "mount_base": "/media/user",
    "user": "user"
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** 10 seconds

**Renderer:** Custom widget with mount/unmount buttons

## Productivity Widgets

### Pomodoro Timer

Productivity timer with work/break cycles.

**Widget ID:** `pomodoro`

**Data Structure:**

```json
{
    "state": "running",
    "is_work": true,
    "time_left": "23:45",
    "seconds_left": 1425,
    "pomodoro_count": 3,
    "work_min": 25,
    "break_min": 5
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `work_duration` | `int` | `25` | Work duration in minutes |
| `break_duration` | `int` | `5` | Break duration in minutes |

**Update Interval:** 1 second

**Renderer:** TextRenderer

---

### Quick Notes

Panel-integrated text storage.

**Widget ID:** `quick-notes`

**Data Structure:**

```json
{
    "notes": [
        {"text": "Note 1", "created": "2026-06-22T10:00:00"},
        {"text": "Note 2", "created": "2026-06-22T11:00:00"}
    ],
    "count": 2
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** On change

**Renderer:** TextRenderer

---

### Clipboard Manager

Clipboard history tracking.

**Widget ID:** `clipboard-manager`

**Data Structure:**

```json
{
    "history": ["item1", "item2", "item3"],
    "count": 3
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** On clipboard change

**Renderer:** TextRenderer

---

### Todo List

Task management with priorities.

**Widget ID:** `todo-list`

**Data Structure:**

```json
{
    "todos": [
        {
            "id": 1,
            "text": "Task 1",
            "priority": "high",
            "done": false,
            "created": "2026-06-22T10:00:00"
        }
    ],
    "pending_count": 1,
    "completed_count": 0,
    "total": 1
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** On change

**Renderer:** TextRenderer

## Integration Widgets

### Weather

Location-based meteorological data.

**Widget ID:** `weather`

**Data Structure:**

```json
{
    "city": "London",
    "available": true,
    "temp_c": "18",
    "temp_f": "64",
    "description": "Partly cloudy",
    "humidity": "72",
    "wind_kmph": "15"
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `city` | `string` | `""` | City name |

**Update Interval:** 10 minutes

**Renderer:** IconTextRenderer

---

### Media Player

MPRIS-compatible playback controls.

**Widget ID:** `media-player`

**Data Structure:**

```json
{
    "available": true,
    "playing": true,
    "title": "Song Title",
    "artist": "Artist Name",
    "album": "Album Name"
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** On change

**Renderer:** IconTextRenderer

---

### System Updates

Package update notifications.

**Widget ID:** `system-updates`

**Data Structure:**

```json
{
    "distro": "ubuntu",
    "update_count": 5,
    "has_updates": true
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| - | - | - | No configuration required |

**Update Interval:** 30 minutes

**Renderer:** TextRenderer

---

### Currency Exchange

Real-time exchange rates.

**Widget ID:** `currency`

**Data Structure:**

```json
{
    "base": "USD",
    "rates": {
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 149.5
    },
    "available": true
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `base_currency` | `string` | `"USD"` | Base currency |
| `target_currencies` | `string` | `"EUR,GBP,JPY"` | Target currencies (comma-separated) |

**Update Interval:** 5 minutes

**Renderer:** TextRenderer

---

### Crypto Prices

Cryptocurrency price tracking.

**Widget ID:** `crypto`

**Data Structure:**

```json
{
    "coins": {
        "bitcoin": {"usd": 45000, "change_24h": 2.5},
        "ethereum": {"usd": 3200, "change_24h": -1.2}
    },
    "available": true
}
```

**Configuration:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `coins` | `string` | `"bitcoin,ethereum,litecoin"` | Coins to track (comma-separated) |

**Update Interval:** 1 minute

**Renderer:** TextRenderer

## Native Widgets

### Clock & Calendar

Date/time display with calendar popup.

**Widget ID:** `clock`

**Data Structure:**

```json
{
    "time": "14:30",
    "date": "Mon, Jun 22",
    "datetime": "2026-06-22T14:30:00"
}
```

**Update Interval:** 1 second

**Renderer:** TextWidget

---

### App Menu

Application launcher.

**Widget ID:** `app-menu`

**Renderer:** Custom widget

---

### Volume Control

Audio volume slider.

**Widget ID:** `volume`

**Renderer:** Custom widget

---

### Desktop Pager

Virtual desktop switcher.

**Widget ID:** `pager`

**Renderer:** Custom widget

---

### Taskbar

Window list.

**Widget ID:** `taskbar`

**Renderer:** Custom widget

---

### System Tray

Status notifier icons.

**Widget ID:** `system-tray`

**Renderer:** Custom widget

## Widget Development

### Creating a New Widget

1. Create provider in `naravisuals/data_providers/`:

```python
from naravisuals.daemon.dbus_service import WidgetProvider

class MyProvider(WidgetProvider):
    PROVIDER_ID = "my-widget"
    
    def start(self):
        pass
    
    def get_data(self) -> dict:
        return {"key": "value"}
```

2. Register in `naravisuals/daemon/dbus_service.py`:

```python
from naravisuals.data_providers.my_provider import MyProvider

# Add to _register_providers()
MyProvider,
```

3. Add to widget registry in `naravisuals/manager/control_center.py`:

```python
{"id": "my-widget", "name": "My Widget", "category": "Custom", "description": "..."}
```
