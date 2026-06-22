import os
import json
from pathlib import Path

class ConfigManager:
    """Manages saving and loading settings for widgets."""
    
    def __init__(self, app_name="naravisuals"):
        config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        self.config_dir = Path(config_home) / app_name
        self.config_file = self.config_dir / "config.json"
        self._config = {}
        self.load()

    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self._config = json.load(f)
            except json.JSONDecodeError:
                self._config = {}
        else:
            self._config = {}

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=4)

    def get(self, widget_name: str, key: str, default=None):
        widget_cfg = self._config.get(widget_name, {})
        return widget_cfg.get(key, default)

    def set(self, widget_name: str, key: str, value):
        if widget_name not in self._config:
            self._config[widget_name] = {}
        self._config[widget_name][key] = value
        self.save()

# Global configuration instance
config = ConfigManager()
