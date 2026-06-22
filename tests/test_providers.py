"""Unit tests for data providers."""
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestSystemProviders:
    def test_system_monitor_provider(self):
        from naravisuals.data_providers.system import SystemMonitorProvider

        provider = SystemMonitorProvider()
        provider.start()
        data = provider.get_data()

        assert "cpu_percent" in data
        assert "ram_percent" in data
        assert "disk_percent" in data
        assert "net_rate" in data
        assert isinstance(data["cpu_percent"], (int, float))
        assert 0 <= data["cpu_percent"] <= 100

    def test_system_monitor_per_core(self):
        from naravisuals.data_providers.system import SystemMonitorProvider

        provider = SystemMonitorProvider()
        provider.start()
        data = provider.get_data()

        assert "cpu_per_core" in data
        assert isinstance(data["cpu_per_core"], list)

    def test_network_monitor_provider(self):
        from naravisuals.data_providers.system import NetworkMonitorProvider

        provider = NetworkMonitorProvider()
        provider.start()
        data = provider.get_data()

        assert "upload_rate" in data
        assert "download_rate" in data
        assert "interfaces" in data
        assert isinstance(data["interfaces"], list)

    def test_network_monitor_interface(self):
        from naravisuals.data_providers.system import NetworkMonitorProvider

        provider = NetworkMonitorProvider()
        provider.start()
        provider.set_interface("lo")
        data = provider.get_data()

        assert data["interface"] == "lo"

    def test_battery_provider(self):
        from naravisuals.data_providers.system import BatteryProvider

        provider = BatteryProvider()
        data = provider.get_data()

        assert "available" in data
        assert "percent" in data
        assert "charging" in data

    def test_uptime_provider(self):
        from naravisuals.data_providers.system import UptimeProvider

        provider = UptimeProvider()
        data = provider.get_data()

        assert "days" in data
        assert "hours" in data
        assert "formatted" in data
        assert isinstance(data["days"], int)

    def test_kernel_provider(self):
        from naravisuals.data_providers.system import KernelProvider

        provider = KernelProvider()
        data = provider.get_data()

        assert "kernel" in data
        assert "machine" in data


class TestWeatherProvider:
    def test_weather_provider_init(self):
        from naravisuals.data_providers.weather import WeatherProvider

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}):
                provider = WeatherProvider()
                provider.start()
                data = provider.get_data()

                assert "available" in data
                assert data["available"] is False  # No city set

    def test_weather_provider_set_city(self):
        from naravisuals.data_providers.weather import WeatherProvider

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}):
                provider = WeatherProvider()
                provider.start()
                provider.set_city("London")
                assert provider._city == "London"


class TestProductivityProviders:
    def test_pomodoro_provider(self):
        from naravisuals.data_providers.productivity import PomodoroProvider

        provider = PomodoroProvider()
        provider.start()
        data = provider.get_data()

        assert "state" in data
        assert "time_left" in data
        assert "pomodoro_count" in data
        assert data["state"] == "idle"

    def test_pomodoro_start_pause(self):
        from naravisuals.data_providers.productivity import PomodoroProvider

        provider = PomodoroProvider()
        provider.start()

        provider.start_timer()
        data = provider.get_data()
        assert data["state"] == "running"

        provider.pause_timer()
        data = provider.get_data()
        assert data["state"] == "paused"

    def test_quick_notes_provider(self):
        from naravisuals.data_providers.productivity import QuickNotesProvider

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}):
                provider = QuickNotesProvider()
                provider.start()

                initial_count = provider.get_data()["count"]
                provider.add_note("Test note")
                data = provider.get_data()
                assert data["count"] == initial_count + 1

    def test_clipboard_provider(self):
        from naravisuals.data_providers.productivity import ClipboardProvider

        provider = ClipboardProvider()
        data = provider.get_data()

        assert "history" in data
        assert "count" in data


class TestFinancialProviders:
    def test_currency_provider_init(self):
        from naravisuals.data_providers.financial import CurrencyProvider

        provider = CurrencyProvider()
        provider.start()
        data = provider.get_data()

        assert "available" in data

    def test_crypto_provider_init(self):
        from naravisuals.data_providers.financial import CryptoProvider

        provider = CryptoProvider()
        provider.start()
        data = provider.get_data()

        assert "available" in data


class TestTodoProvider:
    def test_todo_provider(self):
        from naravisuals.data_providers.todo import TodoListProvider

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}):
                provider = TodoListProvider()
                provider.start()

                initial_count = provider.get_data()["pending_count"]
                provider.add_todo("Test task")
                data = provider.get_data()
                assert data["pending_count"] == initial_count + 1

                # Complete the todo we just added
                todo_id = data["todos"][-1]["id"]
                provider.complete_todo(todo_id)
                data = provider.get_data()
                assert data["completed_count"] >= 1
