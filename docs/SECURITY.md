# Security Considerations

Security model and best practices for NaraVisuals LXQt Widgets.

## Security Model

### Architecture

NaraVisuals follows a least-privilege architecture:

```
User Session
├── naravisuals-daemon (unprivileged)
│   ├── Reads system metrics (psutil)
│   ├── Queries external APIs (requests)
│   └── Manages configuration (JSON files)
├── lxqt-panel (unprivileged)
│   └── Loads NaraVisuals plugin
└── pkexec (privileged, temporary)
    └── Mount/unmount NTFS partitions
```

### Trust Boundaries

| Component | Privileges | Data Access |
|-----------|------------|-------------|
| Daemon | User | System metrics, config files |
| C++ Plugin | User | D-Bus, panel resources |
| NTFS Mount | Root (via pkexec) | Block devices |
| External APIs | Network | Weather, currency, crypto |

## D-Bus Security

### Bus Type

- Session bus only (not system bus)
- User-scoped communication
- No cross-user access

### Access Control

```bash
# Check D-Bus permissions
dbus-send --session --type=method_call \
    --dest=org.freedesktop.DBus \
    /org/freedesktop/DBus \
    org.freedesktop.DBus.ListNames
```

### Method Validation

All D-Bus methods validate input:

```python
def GetData(self, widget_id: str) -> str:
    # Validate widget_id exists
    provider = self.parent.get_provider(widget_id)
    if provider is None:
        return json.dumps({"error": f"Unknown widget: {widget_id}"})
    # ... process request
```

## File System Security

### Configuration Files

| Location | Permissions | Owner |
|----------|-------------|-------|
| `~/.config/naravisuals/` | 700 | User |
| `~/.config/naravisuals/*.json` | 600 | User |
| `~/.config/lxqt/panel.conf` | 600 | User |

### Sensitive Data

NaraVisuals stores minimal sensitive data:

- Weather city name (not API keys)
- Clipboard history (in-memory only)
- Todo items (local JSON)

### File Validation

```python
import os
from pathlib import Path

def validate_config_path(path: Path) -> bool:
    """Ensure config path is safe."""
    # Must be under XDG_CONFIG_HOME
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()
    try:
        path.relative_to(config_home)
        return True
    except ValueError:
        return False
```

## Privilege Escalation

### pkexec Usage

NTFS mounting requires root privileges via pkexec:

```bash
pkexec mount -t ntfs3 /dev/sda1 /media/user/Data
```

### Polkit Policy

NaraVisuals does not install a custom polkit policy. Users must authenticate via the default polkit agent.

### Limitations

- No persistent root privileges
- Authentication required for each mount
- Timeout after authentication

## Network Security

### External APIs

| API | Endpoint | Authentication |
|-----|----------|----------------|
| Weather | `wttr.in` | None |
| Currency | `exchangerate-api.com` | None |
| Crypto | `coingecko.com` | None |

### HTTPS Usage

All external API calls use HTTPS:

```python
import requests

r = requests.get("https://wttr.in/London?format=j1", timeout=5)
```

### Timeout Protection

All network calls have timeouts:

```python
r = requests.get(url, timeout=5)  # 5 second timeout
```

## Input Validation

### Widget IDs

```python
VALID_WIDGETS = {
    "system-monitor", "network-monitor", "battery",
    "weather", "pomodoro", "quick-notes", ...
}

def validate_widget_id(widget_id: str) -> bool:
    return widget_id in VALID_WIDGETS
```

### Configuration Values

```python
def validate_config_value(value: str) -> bool:
    """Basic input validation."""
    # Length check
    if len(value) > 1024:
        return False
    # Null byte check
    if '\x00' in value:
        return False
    return True
```

### JSON Parsing

```python
import json

def safe_parse_json(data: str) -> dict:
    """Safely parse JSON with error handling."""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}
```

## Process Security

### Daemon Isolation

- Runs as user (not root)
- No system-wide D-Bus access
- Limited file system access

### C++ Plugin

- Loaded by lxqt-panel (unprivileged)
- No direct system calls
- D-Bus communication only

## Vulnerability Reporting

### Contact

Report security issues to:
- GitHub Issues (for non-critical)
- Email (for critical): [maintainer email]

### Response Time

- Critical: 24 hours
- High: 72 hours
- Medium: 1 week
- Low: 2 weeks

## Security Checklist

### Installation

- [ ] Verify repository signature
- [ ] Use official packages when available
- [ ] Review install.sh before running
- [ ] Check file permissions after install

### Configuration

- [ ] Validate config files are user-owned
- [ ] Check no world-readable sensitive data
- [ ] Verify D-Bus service is session-scoped

### Runtime

- [ ] Monitor daemon logs for anomalies
- [ ] Keep system updated
- [ ] Use firewall for network access

## Known Limitations

1. **No API key management** - External APIs are unauthenticated
2. **In-memory clipboard** - Clipboard history not encrypted
3. **JSON config** - No encryption at rest
4. **pkexec timeout** - Authentication expires

## Future Improvements

1. Add API key configuration for weather
2. Encrypt sensitive configuration
3. Implement clipboard encryption
4. Add SELinux/AppArmor profiles
