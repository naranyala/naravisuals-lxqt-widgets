import json
import os
from datetime import datetime

import requests
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QLineEdit, QPushButton

from naravisuals.base import PanelWidget


CONFIG_PATH = os.path.expanduser("~/.config/naravisuals/weather.json")


class WeatherWidget(PanelWidget):
    WIDGET_NAME = "Weather"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(600000)
        self._city = self._load_city()
        self._api_key = ""

        self._icon_label = QLabel()
        self._icon_label.setStyleSheet("font-size: 28px;")
        self._info_layout = QVBoxLayout()
        self._city_label = QLabel(self._city or "No city set")
        self._city_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #eee;")
        self._temp_label = QLabel("--°C")
        self._temp_label.setStyleSheet("font-size: 11px; color: #aaa;")
        self._desc_label = QLabel("")
        self._desc_label.setStyleSheet("font-size: 10px; color: #888;")
        self._info_layout.addWidget(self._city_label)
        self._info_layout.addWidget(self._temp_label)
        self._info_layout.addWidget(self._desc_label)
        self._info_layout.addStretch()

        row = QHBoxLayout()
        row.addWidget(self._icon_label)
        row.addLayout(self._info_layout)
        self._layout.addLayout(row)

        self._setup_layout = QHBoxLayout()
        self._city_input = QLineEdit()
        self._city_input.setPlaceholderText("Enter city...")
        self._city_input.setStyleSheet("font-size: 10px;")
        self._save_btn = QPushButton("Set")
        self._save_btn.setStyleSheet("font-size: 10px;")
        self._save_btn.clicked.connect(self._save_city)
        self._setup_layout.addWidget(self._city_input)
        self._setup_layout.addWidget(self._save_btn)
        self._layout.addLayout(self._setup_layout)
        self._setup_widgets = [self._city_input, self._save_btn]

        self.add_action("Set City", self._toggle_setup)

    def _toggle_setup(self):
        vis = self._city_input.isVisible()
        for w in self._setup_widgets:
            w.setVisible(not vis)

    def _on_tick(self):
        if self._city:
            self._fetch_weather()

    def _load_city(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH) as f:
                return json.load(f).get("city", "")
        except Exception:
            return ""

    def _save_city(self):
        city = self._city_input.text().strip()
        if city:
            self._city = city
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump({"city": city}, f)
            self._city_label.setText(city)
            self._toggle_setup()
            self._fetch_weather()

    def _fetch_weather(self):
        try:
            url = f"https://wttr.in/{self._city}?format=j1"
            r = requests.get(url, timeout=5)
            data = r.json()
            cc = data["current_condition"][0]
            temp = cc["temp_C"]
            desc = cc["weatherDesc"][0]["value"]
            self._temp_label.setText(f"{temp}°C")
            self._desc_label.setText(desc)
        except Exception:
            self._temp_label.setText("--°C")
            self._desc_label.setText("offline")


if __name__ == "__main__":
    WeatherWidget.launch_standalone()
