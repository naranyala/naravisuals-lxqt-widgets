# Developer Guide

Guide for developers contributing to NaraVisuals LXQt Widgets.

## Prerequisites

### System Requirements

- Linux (X11 or Wayland)
- Python 3.10+
- Qt 6.5+
- CMake 3.16+
- GCC/G++ 10+ (for C++ plugin)

### Development Dependencies

```bash
# Arch Linux
sudo pacman -S python python-pyqt6 python-psutil python-requests python-dbus python-notify2 \
    cmake lxqt-build-tools gcc

# Debian/Ubuntu
sudo apt install python3 python3-pyqt6 python3-psutil python3-requests python3-dbus python3-notify2 \
    cmake lxqt-build-tools g++

# Fedora/RHEL
sudo dnf install python3 python3-pyqt6 python3-psutil python3-requests python3-dbus-python python3-notify2 \
    cmake lxqt-build-tools gcc-c++
```

### Python Packages

```bash
pip install PyQt6 psutil requests dbus-python notify2
pip install pytest pytest-cov mypy ruff
```

## Project Structure

```
naravisuals-lxqt-widgets/
├── naravisuals/                 # Python package
│   ├── core/                    # Foundation classes
│   │   ├── base_widget.py       # Widget base classes
│   │   ├── theme_engine.py      # Theme engine
│   │   ├── config_manager.py    # Configuration
│   │   └── async_utils.py       # Utilities
│   ├── daemon/                  # D-Bus daemon
│   │   ├── __main__.py          # Entry point
│   │   └── dbus_service.py      # D-Bus interface
│   ├── data_providers/          # Widget data sources
│   │   ├── system.py            # System metrics
│   │   ├── weather.py           # Weather API
│   │   ├── productivity.py      # Pomodoro, notes
│   │   ├── integrations.py      # MPRIS, updates
│   │   ├── todo.py              # Todo list
│   │   ├── financial.py         # Currency, crypto
│   │   └── ntfs_mount.py        # NTFS mounting
│   ├── widgets/                 # Widget implementations
│   │   ├── system/              # System widgets
│   │   ├── productivity/        # Productivity widgets
│   │   ├── integrations/        # Integration widgets
│   │   └── native/              # Native widgets
│   └── manager/                 # GUI manager
│       ├── app.py               # Legacy manager
│       └── control_center.py    # Control center
├── native-plugin/               # C++ plugin
│   ├── naravisuals-plugin.cpp   # Plugin code
│   └── CMakeLists.txt           # Build config
├── tests/                       # Test suite
├── scripts/                     # Utility scripts
├── packaging/                   # Distribution packaging
└── docs/                        # Documentation
```

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/naranyala/naravisuals-lxqt-widgets.git
cd naravisuals-lxqt-widgets
```

### 2. Install in Development Mode

```bash
pip install -e .
```

### 3. Build C++ Plugin

```bash
cd native-plugin
mkdir build && cd build
cmake ..
make
cd ../..
```

### 4. Run Tests

```bash
python -m pytest tests/ -v
```

### 5. Start Daemon

```bash
python -m naravisuals.daemon
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use `ruff` for linting

```bash
# Check style
ruff check naravisuals/

# Format code
ruff format naravisuals/
```

### C++ Style

- Follow LXQt coding style
- Use Qt naming conventions
- Maximum line length: 100 characters

### Import Order

```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import psutil
import requests
from PyQt6.QtCore import Qt

# Local
from naravisuals.core.base_widget import PanelWidget
from naravisuals.core.theme_engine import theme
```

## Adding a New Widget

### Step 1: Create Data Provider

Create `naravisuals/data_providers/my_widget.py`:

```python
"""My widget data provider."""
from typing import Any

from naravisuals.daemon.dbus_service import WidgetProvider


class MyWidgetProvider(WidgetProvider):
    PROVIDER_ID = "my-widget"

    def __init__(self):
        super().__init__()
        self._data = {}

    def start(self):
        """Initialize provider."""
        pass

    def get_data(self) -> dict[str, Any]:
        """Return widget data."""
        return {
            "key": "value",
            "status": "active",
        }
```

### Step 2: Register Provider

Edit `naravisuals/daemon/dbus_service.py`:

```python
# In _register_providers()
from naravisuals.data_providers.my_widget import MyWidgetProvider

# Add to provider list
MyWidgetProvider,
```

### Step 3: Add to Widget Registry

Edit `naravisuals/manager/control_center.py`:

```python
WIDGET_REGISTRY = [
    # ... existing widgets
    {"id": "my-widget", "name": "My Widget", "category": "Custom", "description": "My new widget", "has_config": False},
]
```

### Step 4: Create Standalone Widget (Optional)

Create `naravisuals/widgets/custom/my_widget.py`:

```python
"""My widget standalone implementation."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from naravisuals.core.base_widget import TextWidget


class MyWidget(TextWidget):
    WIDGET_NAME = "My Widget"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(2000)

    def _on_tick(self):
        self.set_text("Hello World")


if __name__ == "__main__":
    MyWidget.launch_standalone()
```

### Step 5: Write Tests

Create `tests/test_my_widget.py`:

```python
"""Tests for my widget provider."""
import pytest


def test_my_widget_provider():
    from naravisuals.data_providers.my_widget import MyWidgetProvider

    provider = MyWidgetProvider()
    provider.start()
    data = provider.get_data()

    assert "key" in data
    assert data["key"] == "value"
```

## Adding Configuration

### Step 1: Define Config Fields

Edit the widget's config page in `naravisuals/manager/control_center.py`:

```python
class WidgetConfigPage(QWidget):
    def setup_fields(self):
        if self.w_id == "my-widget":
            field = QLineEdit(config.get(self.w_id, "setting", "default"))
            self.form_layout.addRow("Setting:", field)
            self.fields["setting"] = field
```

### Step 2: Use Configuration

In your provider:

```python
from naravisuals.core.config_manager import config

class MyProvider(WidgetProvider):
    def get_data(self):
        setting = config.get("my-widget", "setting", "default")
        return {"setting": setting}
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=naravisuals

# Run specific test
python -m pytest tests/test_providers.py::TestSystemProviders::test_system_monitor_provider
```

### Writing Tests

```python
"""Test module."""
import pytest
from unittest.mock import patch, MagicMock


class TestMyProvider:
    def test_basic_functionality(self):
        """Test basic provider functionality."""
        from naravisuals.data_providers.my_widget import MyWidgetProvider

        provider = MyWidgetProvider()
        provider.start()
        data = provider.get_data()

        assert isinstance(data, dict)
        assert "key" in data

    def test_with_mock(self):
        """Test with mocked external dependency."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"result": "ok"}
            
            from naravisuals.data_providers.weather import WeatherProvider
            provider = WeatherProvider()
            # ... test with mock
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug D-Bus

```bash
# Monitor D-Bus traffic
dbus-monitor --session

# Test specific method
dbus-send --session --type=method_call \
    --dest=org.naravisuals.Daemon \
    /org/naravisuals/Daemon \
    org.naravisuals.Daemon.ListWidgets
```

### Debug C++ Plugin

```bash
# Build with debug symbols
cd native-plugin/build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make

# Run with debug output
QT_DEBUG_PLUGINS=1 lxqt-panel
```

## Performance Profiling

### Python

```bash
# Profile daemon
python -m cProfile -o profile.stats -m naravisuals.daemon

# Analyze
python -m pstats profile.stats
```

### Memory

```bash
# Monitor memory
python -m memory_profiler naravisuals.daemon

# Or use psutil
python -c "
import psutil
import os
proc = psutil.Process(os.getpid())
print(f'Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

## Building Releases

### Source Archive

```bash
./archive.sh --output /tmp
```

### RPM Package

```bash
./scripts/build-rpm.sh --setup
./scripts/build-rpm.sh --all
```

### Debian Package

```bash
dpkg-buildpackage -us -uc
```

## Code Review Checklist

- [ ] Tests pass
- [ ] No linting errors
- [ ] Type hints present
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Error handling included
- [ ] Performance considered
- [ ] Security reviewed
