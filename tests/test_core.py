"""Unit tests for naravisuals.core modules."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestConfigManager:
    def test_init_creates_config_dir(self):
        from naravisuals.core.config_manager import ConfigManager

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}):
                cm = ConfigManager("test-app")
                assert cm.config_dir == Path(tmpdir) / "test-app"
                # Directory is created on first save, not on init
                cm.set("test", "key", "value")
                assert cm.config_dir.exists()

    def test_set_and_get(self):
        from naravisuals.core.config_manager import ConfigManager

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}):
                cm = ConfigManager("test-app")
                cm.set("widget1", "key1", "value1")
                assert cm.get("widget1", "key1") == "value1"

    def test_get_default(self):
        from naravisuals.core.config_manager import ConfigManager

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}):
                cm = ConfigManager("test-app")
                assert cm.get("widget1", "nonexistent", "default") == "default"

    def test_persistence(self):
        from naravisuals.core.config_manager import ConfigManager

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmpdir}):
                cm1 = ConfigManager("test-app")
                cm1.set("widget1", "key1", "value1")

                cm2 = ConfigManager("test-app")
                assert cm2.get("widget1", "key1") == "value1"


class TestThemeEngine:
    def test_init(self):
        from naravisuals.core.theme_engine import ThemeEngine

        engine = ThemeEngine()
        assert engine.panel_context is not None
        assert engine.colors is not None

    def test_panel_context(self):
        from naravisuals.core.theme_engine import ThemeEngine, PanelContext

        engine = ThemeEngine()
        ctx = PanelContext(height=64, width=1920, orientation="horizontal")
        engine.update_panel_context(ctx)
        assert engine.panel_context.height == 64

    def test_responsive_font_size(self):
        from naravisuals.core.theme_engine import ThemeEngine, PanelContext

        engine = ThemeEngine()
        engine.update_panel_context(PanelContext(height=48))
        size_48 = engine.get_font_size(10)

        engine.update_panel_context(PanelContext(height=96))
        size_96 = engine.get_font_size(10)

        assert size_96 >= size_48

    def test_dark_mode_detection(self):
        from naravisuals.core.theme_engine import ThemeEngine

        engine = ThemeEngine()
        # Default should be dark
        assert engine.is_dark is True


class TestAsyncUtils:
    def test_format_bytes(self):
        from naravisuals.core.async_utils import format_bytes

        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"

    def test_format_time_mm_ss(self):
        from naravisuals.core.async_utils import format_time_mm_ss

        assert format_time_mm_ss(0) == "00:00"
        assert format_time_mm_ss(61) == "01:01"
        assert format_time_mm_ss(3661) == "61:01"


class TestBaseWidget:
    def test_panel_widget_init(self):
        """Test PanelWidget initialization without QApplication."""
        # This test requires a display, skip in headless CI
        pytest.skip("Requires display server")
