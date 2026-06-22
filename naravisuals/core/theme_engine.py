"""Theme engine for NaraVisuals widgets.

Provides dynamic theming based on system QPalette, panel dimensions,
and user preferences. Supports dark/light mode auto-detection and
responsive layouts.
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication


@dataclass
class PanelContext:
    """Panel dimensions and orientation."""
    height: int = 48
    width: int = 1920
    orientation: str = "horizontal"  # horizontal or vertical
    position: str = "top"  # top, bottom, left, right


@dataclass
class ThemeColors:
    """Resolved theme colors."""
    background: str = "#2d2d2d"
    foreground: str = "#ffffff"
    accent: str = "#3daee9"
    border: str = "#555555"
    text_primary: str = "#ffffff"
    text_secondary: str = "#aaaaaa"
    bar_cpu: str = "#2ecc71"
    bar_ram: str = "#3498db"
    bar_disk: str = "#9b59b6"
    bar_swap: str = "#e74c3c"
    bar_network: str = "#f39c12"


class ThemeEngine:
    """Manages widget theming and panel context."""

    def __init__(self):
        self._panel_context = PanelContext()
        self._colors = ThemeColors()
        self._is_dark = True
        self._custom_colors: dict[str, str] = {}
        self._load_custom_colors()

    @property
    def panel_context(self) -> PanelContext:
        return self._panel_context

    @property
    def colors(self) -> ThemeColors:
        return self._colors

    @property
    def is_dark(self) -> bool:
        return self._is_dark

    def update_from_palette(self, palette: Optional[QPalette] = None):
        """Update theme colors from system QPalette."""
        if palette is None:
            app = QApplication.instance()
            if app:
                palette = app.palette()
            else:
                return

        bg = palette.color(QPalette.ColorRole.Window)
        fg = palette.color(QPalette.ColorRole.WindowText)
        accent = palette.color(QPalette.ColorRole.Highlight)

        self._is_dark = bg.lightness() < 128

        self._colors.background = bg.name()
        self._colors.foreground = fg.name()
        self._colors.accent = accent.name()
        self._colors.border = palette.color(QPalette.ColorRole.Mid).name()
        self._colors.text_primary = fg.name()
        self._colors.text_secondary = palette.color(QPalette.ColorRole.PlaceholderText).name()

        # Apply custom overrides
        self._colors.__dict__.update(self._custom_colors)

    def update_panel_context(self, context: PanelContext):
        """Update panel dimensions and orientation."""
        self._panel_context = context

    def get_font_size(self, base: int = 10) -> int:
        """Get responsive font size based on panel height."""
        scale = self._panel_context.height / 48.0
        return max(8, int(base * scale))

    def get_bar_height(self) -> int:
        """Get responsive bar height based on panel height."""
        return max(12, int(self._panel_context.height * 0.375))

    def get_icon_size(self) -> int:
        """Get responsive icon size based on panel height."""
        return max(16, int(self._panel_context.height * 0.46))

    def get_spacing(self) -> int:
        """Get responsive spacing based on panel height."""
        return max(2, int(self._panel_context.height * 0.08))

    def get_margins(self) -> tuple[int, int, int, int]:
        """Get responsive margins (left, top, right, bottom)."""
        s = self.get_spacing()
        return (s, s, s, s)

    def apply_to_widget(self, widget):
        """Apply theme to a QWidget."""
        s = self._colors
        margins = self.get_margins()
        font_size = self.get_font_size()

        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {s.background};
                color: {s.foreground};
                font-size: {font_size}px;
            }}
            QLabel {{
                color: {s.text_primary};
                background: transparent;
            }}
            QPushButton {{
                background-color: {s.accent};
                color: {s.foreground};
                border: 1px solid {s.border};
                border-radius: 3px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {s.accent}dd;
            }}
        """)

    def get_stylesheet(self) -> str:
        """Get full stylesheet for widget."""
        s = self._colors
        font_size = self.get_font_size()

        return f"""
            QWidget {{
                background-color: {s.background};
                color: {s.foreground};
                font-size: {font_size}px;
            }}
            QLabel {{
                color: {s.text_primary};
                background: transparent;
            }}
            QToolTip {{
                background-color: {s.background};
                color: {s.foreground};
                border: 1px solid {s.border};
            }}
        """

    def _load_custom_colors(self):
        """Load custom color overrides from config."""
        config_path = Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))) / "naravisuals" / "theme.json"
        try:
            if config_path.exists():
                with open(config_path) as f:
                    self._custom_colors = json.load(f)
        except Exception:
            self._custom_colors = {}

    def save_custom_colors(self):
        """Save custom color overrides to config."""
        config_dir = Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))) / "naravisuals"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "theme.json"
        try:
            with open(config_file, "w") as f:
                json.dump(self._custom_colors, f, indent=2)
        except Exception:
            pass

    def set_custom_color(self, name: str, color: str):
        """Set a custom color override."""
        if hasattr(self._colors, name):
            self._custom_colors[name] = color
            setattr(self._colors, name, color)
            self.save_custom_colors()


# Global theme engine instance
theme = ThemeEngine()
