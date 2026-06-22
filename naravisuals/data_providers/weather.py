"""Weather data provider."""
import json
import os
from pathlib import Path
from typing import Any

from naravisuals.daemon.dbus_service import WidgetProvider


def _get_config_path() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))) / "naravisuals" / "weather.json"


class WeatherProvider(WidgetProvider):
    PROVIDER_ID = "weather"

    def __init__(self):
        super().__init__()
        self._city = ""
        self._last_data: dict[str, Any] = {}

    def start(self):
        self._load_city()

    def get_data(self) -> dict[str, Any]:
        if not self._city:
            return {"city": "", "available": False}

        try:
            import requests

            r = requests.get(f"https://wttr.in/{self._city}?format=j1", timeout=5)
            data = r.json()
            cc = data["current_condition"][0]
            self._last_data = {
                "city": self._city,
                "available": True,
                "temp_c": cc["temp_C"],
                "temp_f": cc["temp_F"],
                "description": cc["weatherDesc"][0]["value"],
                "humidity": cc["humidity"],
                "wind_kmph": cc["windspeedKmph"],
            }
        except Exception:
            self._last_data = {
                "city": self._city,
                "available": False,
                "temp_c": "--",
                "description": "offline",
            }

        return self._last_data

    def set_city(self, city: str):
        self._city = city
        self._save_city()

    def _load_city(self):
        config_path = _get_config_path()
        try:
            if config_path.exists():
                with open(config_path) as f:
                    self._city = json.load(f).get("city", "")
        except Exception:
            self._city = ""

    def _save_city(self):
        config_path = _get_config_path()
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                json.dump({"city": self._city}, f)
        except Exception:
            pass
