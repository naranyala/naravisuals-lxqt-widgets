"""NaraVisuals Theme Manager - Full desktop theming for LXQt + Labwc/KWin.

Manages labwc themes, KWin effects, LXQt themes, panel layout,
icon themes, fonts, cursor themes, and color schemes.
"""
import sys
import os
import re
import json
import shutil
import subprocess
import configparser
from pathlib import Path
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QStackedWidget, QLabel, QLineEdit,
    QComboBox, QFormLayout, QFrame, QMessageBox, QFileDialog,
    QListWidgetItem, QScrollArea, QGridLayout, QTextEdit,
    QCheckBox, QSpinBox, QGroupBox, QSplitter, QColorDialog,
    QFontComboBox, QSlider, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter

from naravisuals.core.theme_engine import theme

# =============================================================================
# Constants
# =============================================================================

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")))
LABWC_DIR = CONFIG_DIR / "labwc"
LXQT_DIR = CONFIG_DIR / "lxqt"
KVANTUM_DIR = CONFIG_DIR / "Kvantum"
QTCT_DIR = CONFIG_DIR / "qt6ct"

ICON_SEARCH_DIRS = [
    Path.home() / ".local/share/icons",
    Path("/usr/share/icons"),
    Path("/usr/local/share/icons"),
]

FONT_SEARCH_DIRS = [
    Path.home() / ".local/share/fonts",
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
    Path.home() / ".fonts",
]

STORE_DATA = Path(__file__).parent / "data" / "themes.json"


# =============================================================================
# Config Readers
# =============================================================================

class LabwcConfig:
    """Read/write labwc configuration files."""

    def __init__(self):
        self.rc_path = LABWC_DIR / "rc.xml"
        self.themerc_path = LABWC_DIR / "themerc-override"
        self.menu_path = LABWC_DIR / "menu.xml"

    def exists(self) -> bool:
        return self.rc_path.exists()

    def get_theme_name(self) -> str:
        if not self.rc_path.exists():
            return ""
        try:
            content = self.rc_path.read_text()
            match = re.search(r"<name>(.*?)</name>", content)
            return match.group(1) if match else ""
        except Exception:
            return ""

    def set_theme_name(self, name: str):
        if not self.rc_path.exists():
            return
        try:
            content = self.rc_path.read_text()
            content = re.sub(r"<name>.*?</name>", f"<name>{name}</name>", content)
            self.rc_path.write_text(content)
        except Exception:
            pass

    def get_corner_radius(self) -> int:
        if not self.rc_path.exists():
            return 10
        try:
            content = self.rc_path.read_text()
            match = re.search(r"<cornerRadius>(\d+)</cornerRadius>", content)
            return int(match.group(1)) if match else 10
        except Exception:
            return 10

    def set_corner_radius(self, radius: int):
        if not self.rc_path.exists():
            return
        try:
            content = self.rc_path.read_text()
            content = re.sub(r"<cornerRadius>\d+</cornerRadius>",
                           f"<cornerRadius>{radius}</cornerRadius>", content)
            self.rc_path.write_text(content)
        except Exception:
            pass

    def get_gap(self) -> int:
        if not self.rc_path.exists():
            return 0
        try:
            content = self.rc_path.read_text()
            match = re.search(r"<gap>(\d+)</gap>", content)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0

    def set_gap(self, gap: int):
        if not self.rc_path.exists():
            return
        try:
            content = self.rc_path.read_text()
            content = re.sub(r"<gap>\d+</gap>", f"<gap>{gap}</gap>", content)
            self.rc_path.write_text(content)
        except Exception:
            pass

    def get_focus_mode(self) -> str:
        if not self.rc_path.exists():
            return "sloppy"
        try:
            content = self.rc_path.read_text()
            match = re.search(r"<focusMode>(.*?)</focusMode>", content)
            return match.group(1) if match else "sloppy"
        except Exception:
            return "sloppy"

    def set_focus_mode(self, mode: str):
        if not self.rc_path.exists():
            return
        try:
            content = self.rc_path.read_text()
            content = re.sub(r"<focusMode>.*?</focusMode>",
                           f"<focusMode>{mode}</focusMode>", content)
            self.rc_path.write_text(content)
        except Exception:
            pass

    def get_desktop_count(self) -> int:
        if not self.rc_path.exists():
            return 4
        try:
            content = self.rc_path.read_text()
            match = re.search(r"<number>(\d+)</number>")
            return int(match.group(1)) if match else 4
        except Exception:
            return 4

    def set_desktop_count(self, count: int):
        if not self.rc_path.exists():
            return
        try:
            content = self.rc_path.read_text()
            content = re.sub(r"<number>\d+</number>", f"<number>{count}</number>", content)
            self.rc_path.write_text(content)
        except Exception:
            pass

    def get_themerc(self) -> dict[str, str]:
        result = {}
        if not self.themerc_path.exists():
            return result
        try:
            for line in self.themerc_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and ":" in line:
                    key, _, value = line.partition(":")
                    result[key.strip()] = value.strip()
        except Exception:
            pass
        return result

    def set_themerc(self, key: str, value: str):
        lines = []
        found = False
        if self.themerc_path.exists():
            for line in self.themerc_path.read_text().splitlines():
                if line.strip().startswith(key + ":"):
                    lines.append(f"{key}: {value}")
                    found = True
                else:
                    lines.append(line)
        if not found:
            lines.append(f"{key}: {value}")
        self.themerc_path.parent.mkdir(parents=True, exist_ok=True)
        self.themerc_path.write_text("\n".join(lines) + "\n")

    def list_installed_themes(self) -> list[str]:
        themes = []
        # Check labwc theme dirs
        for d in [LABWC_DIR / "themes", Path("/usr/share/themes"),
                  Path.home() / ".local/share/themes",
                  Path.home() / ".themes"]:
            if d.is_dir():
                for t in d.iterdir():
                    if t.is_dir() and t.name not in themes:
                        themes.append(t.name)
        return sorted(themes)

    def reload(self):
        try:
            subprocess.run(["killall", "-USR1", "labwc"], capture_output=True)
        except Exception:
            pass


class LxQtConfig:
    """Read/write LXQt configuration."""

    def __init__(self):
        self.session_path = LXQT_DIR / "session.conf"
        self.lxqt_path = LXQT_DIR / "lxqt.conf"
        self.panel_path = LXQT_DIR / "panel.conf"
        self.appearance_path = LXQT_DIR / "lxqt-config-appearance.conf"

    def _read_ini(self, path: Path) -> configparser.ConfigParser:
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        if path.exists():
            parser.read(str(path))
        return parser

    def _write_ini(self, path: Path, parser: configparser.ConfigParser):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            parser.write(f)

    def get_theme(self) -> str:
        p = self._read_ini(self.session_path)
        return p.get("LXQt", "theme", fallback="Frost")

    def set_theme(self, name: str):
        p = self._read_ini(self.session_path)
        if not p.has_section("LXQt"):
            p.add_section("LXQt")
        p.set("LXQt", "theme", name)
        self._write_ini(self.session_path, p)

    def get_icon_theme(self) -> str:
        p = self._read_ini(self.session_path)
        return p.get("LXQt", "icon_theme", fallback="breeze-dark")

    def set_icon_theme(self, name: str):
        p = self._read_ini(self.session_path)
        if not p.has_section("LXQt"):
            p.add_section("LXQt")
        p.set("LXQt", "icon_theme", name)
        self._write_ini(self.session_path, p)

    def get_font(self) -> str:
        p = self._read_ini(self.session_path)
        return p.get("LXQt", "font", fallback="Noto Sans, 10")

    def set_font(self, font_str: str):
        p = self._read_ini(self.session_path)
        if not p.has_section("LXQt"):
            p.add_section("LXQt")
        p.set("LXQt", "font", font_str)
        self._write_ini(self.session_path, p)

    def get_fixed_font(self) -> str:
        p = self._read_ini(self.session_path)
        return p.get("LXQt", "fixed_font", fallback="Noto Sans Mono, 10")

    def set_fixed_font(self, font_str: str):
        p = self._read_ini(self.session_path)
        if not p.has_section("LXQt"):
            p.add_section("LXQt")
        p.set("LXQt", "fixed_font", font_str)
        self._write_ini(self.session_path, p)

    def get_cursor_theme(self) -> str:
        p = self._read_ini(self.session_path)
        return p.get("Cursor", "cursor_theme", fallback="breeze_cursors")

    def set_cursor_theme(self, name: str):
        p = self._read_ini(self.session_path)
        if not p.has_section("Cursor"):
            p.add_section("Cursor")
        p.set("Cursor", "cursor_theme", name)
        self._write_ini(self.session_path, p)

    def get_cursor_size(self) -> int:
        p = self._read_ini(self.session_path)
        return p.getint("Cursor", "cursor_size", fallback=24)

    def set_cursor_size(self, size: int):
        p = self._read_ini(self.session_path)
        if not p.has_section("Cursor"):
            p.add_section("Cursor")
        p.set("Cursor", "cursor_size", str(size))
        self._write_ini(self.session_path, p)

    def get_gtk_theme(self) -> str:
        p = self._read_ini(self.session_path)
        return p.get("Environment", "GTK_THEME", fallback="Adwaita-dark")

    def set_gtk_theme(self, name: str):
        p = self._read_ini(self.session_path)
        if not p.has_section("Environment"):
            p.add_section("Environment")
        p.set("Environment", "GTK_THEME", name)
        self._write_ini(self.session_path, p)

    def get_window_manager(self) -> str:
        p = self._read_ini(self.session_path)
        return p.get("Session", "window_manager", fallback="labwc")

    def list_themes(self) -> list[str]:
        themes = []
        for d in [LXQT_DIR / "themes", Path("/usr/share/lxqt/themes"),
                  Path.home() / ".local/share/lxqt/themes"]:
            if d.is_dir():
                for t in d.iterdir():
                    if t.is_dir() and t.name not in themes:
                        themes.append(t.name)
        return sorted(themes) if themes else ["Frost", "Dark", "Light"]

    def list_icon_themes(self) -> list[str]:
        themes = []
        for d in ICON_SEARCH_DIRS:
            if d.is_dir():
                for t in d.iterdir():
                    if t.is_dir() and (t / "index.theme").exists() and t.name not in themes:
                        themes.append(t.name)
        return sorted(themes) if themes else ["breeze-dark", "breeze", "Adwaita"]

    def list_gtk_themes(self) -> list[str]:
        themes = []
        for d in [Path("/usr/share/themes"), Path.home() / ".themes",
                  Path.home() / ".local/share/themes"]:
            if d.is_dir():
                for t in d.iterdir():
                    if t.is_dir() and t.name not in themes:
                        themes.append(t.name)
        return sorted(themes) if themes else ["Adwaita", "Adwaita-dark"]

    def list_cursor_themes(self) -> list[str]:
        themes = []
        for d in [Path("/usr/share/icons"), Path.home() / ".local/share/icons"]:
            if d.is_dir():
                for t in d.iterdir():
                    if t.is_dir() and (t / "cursors").exists() and t.name not in themes:
                        themes.append(t.name)
        return sorted(themes) if themes else ["breeze_cursors", "Adwaita"]


class PanelConfig:
    """Read/write LXQt panel configuration."""

    def __init__(self):
        self.path = LXQT_DIR / "panel.conf"

    def exists(self) -> bool:
        return self.path.exists()

    def _read(self) -> configparser.ConfigParser:
        p = configparser.ConfigParser(interpolation=None)
        p.optionxform = str
        if self.path.exists():
            p.read(str(self.path))
        return p

    def _write(self, p: configparser.ConfigParser):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            p.write(f)

    def get_panels(self) -> list[str]:
        p = self._read()
        if "general" in p and "panels" in p["general"]:
            return [x.strip() for x in p["general"]["panels"].split(",") if x.strip()]
        return [s for s in p.sections() if s.startswith("panel")]

    def get_panel_config(self, panel: str) -> dict:
        p = self._read()
        if panel in p:
            return dict(p[panel])
        return {}

    def set_panel_config(self, panel: str, key: str, value: str):
        p = self._read()
        if panel not in p:
            p.add_section(panel)
        p.set(panel, key, value)
        self._write(p)

    def get_panel_size(self, panel: str) -> int:
        cfg = self.get_panel_config(panel)
        return int(cfg.get("line_size", cfg.get("height", "40")))

    def set_panel_size(self, panel: str, size: int):
        self.set_panel_config(panel, "line_size", str(size))

    def get_panel_position(self, panel: str) -> str:
        cfg = self.get_panel_config(panel)
        return cfg.get("position", "bottom")

    def set_panel_position(self, panel: str, position: str):
        self.set_panel_config(panel, "position", position)

    def get_panel_plugins(self, panel: str) -> list[str]:
        cfg = self.get_panel_config(panel)
        plugins = cfg.get("plugins", "")
        return [p.strip() for p in plugins.split(",") if p.strip()]

    def set_panel_plugins(self, panel: str, plugins: list[str]):
        self.set_panel_config(panel, "plugins", ", ".join(plugins))

    def get_panel_alignment(self, panel: str) -> str:
        cfg = self.get_panel_config(panel)
        return cfg.get("alignment", "left")

    def set_panel_alignment(self, panel: str, alignment: str):
        self.set_panel_config(panel, "alignment", alignment)

    def get_icon_size(self, panel: str) -> int:
        cfg = self.get_panel_config(panel)
        return int(cfg.get("icon_size", "32"))

    def set_icon_size(self, panel: str, size: int):
        self.set_panel_config(panel, "icon_size", str(size))


class FontManager:
    """Discover and manage system fonts."""

    def __init__(self):
        self._fonts: dict[str, str] = {}

    def discover_fonts(self) -> dict[str, str]:
        self._fonts.clear()
        for font_dir in FONT_SEARCH_DIRS:
            if not font_dir.is_dir():
                continue
            for f in font_dir.rglob("*"):
                if f.suffix.lower() in (".ttf", ".otf", ".ttc"):
                    name = f.stem
                    if name not in self._fonts:
                        self._fonts[name] = str(f)
        return self._fonts

    def get_font_names(self) -> list[str]:
        if not self._fonts:
            self.discover_fonts()
        return sorted(self._fonts.keys())

    def get_font_path(self, name: str) -> Optional[str]:
        return self._fonts.get(name)


class IconThemeManager:
    """Discover and manage icon themes."""

    def __init__(self):
        self._themes: dict[str, list[str]] = {}

    def discover_themes(self) -> dict[str, list[str]]:
        self._themes.clear()
        for icon_dir in ICON_SEARCH_DIRS:
            if not icon_dir.is_dir():
                continue
            for d in icon_dir.iterdir():
                if d.is_dir() and (d / "index.theme").exists():
                    name = d.name
                    if name not in self._themes:
                        self._themes[name] = self._scan_icons(d)
        return self._themes

    def _scan_icons(self, theme_dir: Path) -> list[str]:
        icons = []
        for f in theme_dir.rglob("*.png"):
            icons.append(f.stem)
        for f in theme_dir.rglob("*.svg"):
            icons.append(f.stem)
        return list(set(icons))[:100]

    def get_theme_names(self) -> list[str]:
        if not self._themes:
            self.discover_themes()
        return sorted(self._themes.keys())

    def get_theme_icons(self, name: str) -> list[str]:
        return self._themes.get(name, [])


# =============================================================================
# Pages
# =============================================================================

class LabwcPage(QWidget):
    """Labwc compositor theme manager."""

    def __init__(self):
        super().__init__()
        self._config = LabwcConfig()
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("<h2>Labwc Compositor</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444466; background: #1a1a2e; }
            QTabBar::tab { background: #2a2a3e; color: #cccccc; padding: 8px 16px; border: 1px solid #444466; }
            QTabBar::tab:selected { background: #3daee9; color: white; }
        """)

        # Theme tab
        theme_tab = QWidget()
        theme_layout = QVBoxLayout(theme_tab)

        theme_group = QGroupBox("Window Theme")
        theme_form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self._config.list_installed_themes())
        theme_form.addRow("Theme:", self.theme_combo)

        self.corner_spin = QSpinBox()
        self.corner_spin.setRange(0, 50)
        theme_form.addRow("Corner Radius:", self.corner_spin)

        self.gap_spin = QSpinBox()
        self.gap_spin.setRange(0, 50)
        theme_form.addRow("Window Gap:", self.gap_spin)

        self.focus_combo = QComboBox()
        self.focus_combo.addItems(["sloppy", "click", "follow"])
        theme_form.addRow("Focus Mode:", self.focus_combo)

        theme_group.setLayout(theme_form)
        theme_layout.addWidget(theme_group)
        theme_layout.addStretch()
        tabs.addTab(theme_tab, "Theme")

        # Colors tab
        colors_tab = QWidget()
        colors_layout = QVBoxLayout(colors_tab)

        colors_group = QGroupBox("Window Colors")
        colors_form = QFormLayout()

        self.active_bg = QLineEdit()
        colors_form.addRow("Active Title BG:", self.active_bg)

        self.active_fg = QLineEdit()
        colors_form.addRow("Active Title FG:", self.active_fg)

        self.inactive_bg = QLineEdit()
        colors_form.addRow("Inactive Title BG:", self.inactive_bg)

        self.inactive_fg = QLineEdit()
        colors_form.addRow("Inactive Title FG:", self.inactive_fg)

        self.active_border = QLineEdit()
        colors_form.addRow("Active Border:", self.active_border)

        self.inactive_border = QLineEdit()
        colors_form.addRow("Inactive Border:", self.inactive_border)

        colors_group.setLayout(colors_form)
        colors_layout.addWidget(colors_group)

        # Button colors
        btn_group = QGroupBox("Button Colors")
        btn_form = QFormLayout()

        self.close_color = QLineEdit()
        btn_form.addRow("Close Button:", self.close_color)

        self.maximize_color = QLineEdit()
        btn_form.addRow("Maximize Button:", self.maximize_color)

        self.iconify_color = QLineEdit()
        btn_form.addRow("Iconify Button:", self.iconify_color)

        btn_group.setLayout(btn_form)
        colors_layout.addWidget(btn_group)
        colors_layout.addStretch()
        tabs.addTab(colors_tab, "Colors")

        # Menu tab
        menu_tab = QWidget()
        menu_layout = QVBoxLayout(menu_tab)

        menu_group = QGroupBox("Menu Appearance")
        menu_form = QFormLayout()

        self.menu_bg = QLineEdit()
        menu_form.addRow("Menu BG:", self.menu_bg)

        self.menu_fg = QLineEdit()
        menu_form.addRow("Menu FG:", self.menu_fg)

        self.menu_active_bg = QLineEdit()
        menu_form.addRow("Menu Active BG:", self.menu_active_bg)

        self.menu_active_fg = QLineEdit()
        menu_form.addRow("Menu Active FG:", self.menu_active_fg)

        self.menu_separator = QLineEdit()
        menu_form.addRow("Separator Color:", self.menu_separator)

        menu_group.setLayout(menu_form)
        menu_layout.addWidget(menu_group)
        menu_layout.addStretch()
        tabs.addTab(menu_tab, "Menu")

        # OSD tab
        osd_tab = QWidget()
        osd_layout = QVBoxLayout(osd_tab)

        osd_group = QGroupBox("On-Screen Display")
        osd_form = QFormLayout()

        self.osd_bg = QLineEdit()
        osd_form.addRow("OSD BG:", self.osd_bg)

        self.osd_fg = QLineEdit()
        osd_form.addRow("OSD FG:", self.osd_fg)

        self.osd_border = QLineEdit()
        osd_form.addRow("OSD Border:", self.osd_border)

        osd_group.setLayout(osd_form)
        osd_layout.addWidget(osd_group)
        osd_layout.addStretch()
        tabs.addTab(osd_tab, "OSD")

        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px 24px;")
        apply_btn.clicked.connect(self._apply)
        btn_layout.addWidget(apply_btn)

        reload_btn = QPushButton("Reload Labwc")
        reload_btn.clicked.connect(self._reload)
        btn_layout.addWidget(reload_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _load(self):
        self.theme_combo.setCurrentText(self._config.get_theme_name())
        self.corner_spin.setValue(self._config.get_corner_radius())
        self.gap_spin.setValue(self._config.get_gap())
        self.focus_combo.setCurrentText(self._config.get_focus_mode())

        themerc = self._config.get_themerc()
        self.active_bg.setText(themerc.get("window.active.title.bg", "#3b4252"))
        self.active_fg.setText(themerc.get("window.active.title.fg", "#eceff4"))
        self.inactive_bg.setText(themerc.get("window.inactive.title.bg", "#2e3440"))
        self.inactive_fg.setText(themerc.get("window.inactive.title.fg", "#4c566a"))
        self.active_border.setText(themerc.get("window.active.border.color", "#81a1c1"))
        self.inactive_border.setText(themerc.get("window.border.color", "#2e3440"))
        self.close_color.setText(themerc.get("window.active.button.close.fg", "#bf616a"))
        self.maximize_color.setText(themerc.get("window.active.button.maximize.fg", "#a3be8c"))
        self.iconify_color.setText(themerc.get("window.active.button.iconify.fg", "#ebcb8b"))
        self.menu_bg.setText(themerc.get("menu.items.bg", "#2e3440"))
        self.menu_fg.setText(themerc.get("menu.items.fg", "#d8dee9"))
        self.menu_active_bg.setText(themerc.get("menu.items.active.bg", "#81a1c1"))
        self.menu_active_fg.setText(themerc.get("menu.items.active.fg", "#2e3440"))
        self.menu_separator.setText(themerc.get("menu.separator.color", "#4c566a"))
        self.osd_bg.setText(themerc.get("osd.bg", "#2e3440"))
        self.osd_fg.setText(themerc.get("osd.fg", "#d8dee9"))
        self.osd_border.setText(themerc.get("osd.border.color", "#81a1c1"))

    def _apply(self):
        self._config.set_theme_name(self.theme_combo.currentText())
        self._config.set_corner_radius(self.corner_spin.value())
        self._config.set_gap(self.gap_spin.value())
        self._config.set_focus_mode(self.focus_combo.currentText())

        self._config.set_themerc("window.active.title.bg", self.active_bg.text())
        self._config.set_themerc("window.active.title.fg", self.active_fg.text())
        self._config.set_themerc("window.active.title.bg.color", self.active_bg.text())
        self._config.set_themerc("window.active.label.fg", self.active_fg.text())
        self._config.set_themerc("window.active.label.bg", self.active_bg.text())
        self._config.set_themerc("window.active.label.bg.color", self.active_bg.text())
        self._config.set_themerc("window.inactive.title.bg", self.inactive_bg.text())
        self._config.set_themerc("window.inactive.title.fg", self.inactive_fg.text())
        self._config.set_themerc("window.inactive.title.bg.color", self.inactive_bg.text())
        self._config.set_themerc("window.inactive.label.fg", self.inactive_fg.text())
        self._config.set_themerc("window.inactive.label.bg", self.inactive_bg.text())
        self._config.set_themerc("window.inactive.label.bg.color", self.inactive_bg.text())
        self._config.set_themerc("window.active.border.color", self.active_border.text())
        self._config.set_themerc("window.border.color", self.inactive_border.text())

        self._config.set_themerc("window.active.button.close.fg", self.close_color.text())
        self._config.set_themerc("window.active.button.close.bg", self.active_bg.text())
        self._config.set_themerc("window.active.button.maximize.fg", self.maximize_color.text())
        self._config.set_themerc("window.active.button.maximize.bg", self.active_bg.text())
        self._config.set_themerc("window.active.button.iconify.fg", self.iconify_color.text())
        self._config.set_themerc("window.active.button.iconify.bg", self.active_bg.text())
        self._config.set_themerc("window.inactive.button.bg", self.inactive_bg.text())
        self._config.set_themerc("window.inactive.button.bg.color", self.inactive_bg.text())

        self._config.set_themerc("menu.items.bg", self.menu_bg.text())
        self._config.set_themerc("menu.items.fg", self.menu_fg.text())
        self._config.set_themerc("menu.items.bg.color", self.menu_bg.text())
        self._config.set_themerc("menu.items.active.bg", self.menu_active_bg.text())
        self._config.set_themerc("menu.items.active.fg", self.menu_active_fg.text())
        self._config.set_themerc("menu.items.active.bg.color", self.menu_active_bg.text())
        self._config.set_themerc("menu.title.bg", self.active_bg.text())
        self._config.set_themerc("menu.title.fg", self.active_fg.text())
        self._config.set_themerc("menu.title.bg.color", self.active_bg.text())
        self._config.set_themerc("menu.separator.color", self.menu_separator.text())

        self._config.set_themerc("osd.bg", self.osd_bg.text())
        self._config.set_themerc("osd.fg", self.osd_fg.text())
        self._config.set_themerc("osd.bg.color", self.osd_bg.text())
        self._config.set_themerc("osd.border.color", self.osd_border.text())
        self._config.set_themerc("osd.label.fg", self.osd_fg.text())
        self._config.set_themerc("osd.label.bg", self.osd_bg.text())
        self._config.set_themerc("osd.label.bg.color", self.osd_bg.text())

        QMessageBox.information(self, "Applied", "Labwc theme applied.\nClick 'Reload Labwc' to see changes.")

    def _reload(self):
        self._config.reload()
        QMessageBox.information(self, "Reloaded", "Labwc config reloaded.")


class LxQtPage(QWidget):
    """LXQt theme, icon, and cursor manager."""

    def __init__(self):
        super().__init__()
        self._config = LxQtConfig()
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("<h2>LXQt Appearance</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #444466; background: #1a1a2e; }
            QTabBar::tab { background: #2a2a3e; color: #cccccc; padding: 8px 16px; border: 1px solid #444466; }
            QTabBar::tab:selected { background: #3daee9; color: white; }
        """)

        # Theme tab
        theme_tab = QWidget()
        theme_layout = QVBoxLayout(theme_tab)

        theme_group = QGroupBox("LXQt Theme")
        theme_form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self._config.list_themes())
        theme_form.addRow("Widget Theme:", self.theme_combo)

        theme_group.setLayout(theme_form)
        theme_layout.addWidget(theme_group)

        icon_group = QGroupBox("Icon Theme")
        icon_form = QFormLayout()

        self.icon_combo = QComboBox()
        self.icon_combo.addItems(self._config.list_icon_themes())
        icon_form.addRow("Icon Theme:", self.icon_combo)

        icon_group.setLayout(icon_form)
        theme_layout.addWidget(icon_group)

        gtk_group = QGroupBox("GTK Theme")
        gtk_form = QFormLayout()

        self.gtk_combo = QComboBox()
        self.gtk_combo.addItems(self._config.list_gtk_themes())
        gtk_form.addRow("GTK Theme:", self.gtk_combo)

        gtk_group.setLayout(gtk_form)
        theme_layout.addWidget(gtk_group)

        theme_layout.addStretch()
        tabs.addTab(theme_tab, "Theme & Icons")

        # Fonts tab
        fonts_tab = QWidget()
        fonts_layout = QVBoxLayout(fonts_tab)

        font_group = QGroupBox("Fonts")
        font_form = QFormLayout()

        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self._config.get_font().split(",")[0].strip()))
        font_form.addRow("UI Font:", self.font_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 48)
        font_form.addRow("Font Size:", self.font_size_spin)

        self.mono_font_combo = QFontComboBox()
        self.mono_font_combo.setCurrentFont(QFont(self._config.get_fixed_font().split(",")[0].strip()))
        font_form.addRow("Monospace Font:", self.mono_font_combo)

        self.mono_size_spin = QSpinBox()
        self.mono_size_spin.setRange(6, 48)
        font_form.addRow("Mono Size:", self.mono_size_spin)

        font_group.setLayout(font_form)
        fonts_layout.addWidget(font_group)

        fonts_layout.addStretch()
        tabs.addTab(fonts_tab, "Fonts")

        # Cursor tab
        cursor_tab = QWidget()
        cursor_layout = QVBoxLayout(cursor_tab)

        cursor_group = QGroupBox("Cursor Theme")
        cursor_form = QFormLayout()

        self.cursor_combo = QComboBox()
        self.cursor_combo.addItems(self._config.list_cursor_themes())
        cursor_form.addRow("Cursor Theme:", self.cursor_combo)

        self.cursor_size_spin = QSpinBox()
        self.cursor_size_spin.setRange(8, 64)
        self.cursor_size_spin.setSingleStep(2)
        cursor_form.addRow("Cursor Size:", self.cursor_size_spin)

        cursor_group.setLayout(cursor_form)
        cursor_layout.addWidget(cursor_group)

        cursor_layout.addStretch()
        tabs.addTab(cursor_tab, "Cursor")

        # Environment tab
        env_tab = QWidget()
        env_layout = QVBoxLayout(env_tab)

        env_group = QGroupBox("Environment")
        env_form = QFormLayout()

        self.wm_combo = QComboBox()
        self.wm_combo.addItems(["labwc", "kwin_wayland", "kwin_x11", "openbox", "sway", "hyprland"])
        env_form.addRow("Window Manager:", self.wm_combo)

        env_group.setLayout(env_form)
        env_layout.addWidget(env_group)

        env_layout.addStretch()
        tabs.addTab(env_tab, "Environment")

        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px 24px;")
        apply_btn.clicked.connect(self._apply)
        btn_layout.addWidget(apply_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _load(self):
        self.theme_combo.setCurrentText(self._config.get_theme())
        self.icon_combo.setCurrentText(self._config.get_icon_theme())
        self.gtk_combo.setCurrentText(self._config.get_gtk_theme())
        self.cursor_combo.setCurrentText(self._config.get_cursor_theme())
        self.cursor_size_spin.setValue(self._config.get_cursor_size())
        self.wm_combo.setCurrentText(self._config.get_window_manager())

        font = self._config.get_font()
        parts = font.split(",")
        if len(parts) >= 2:
            self.font_size_spin.setValue(int(parts[1].strip()))

        mono = self._config.get_fixed_font()
        parts = mono.split(",")
        if len(parts) >= 2:
            self.mono_size_spin.setValue(int(parts[1].strip()))

    def _apply(self):
        font_str = f"{self.font_combo.currentFont().family()}, {self.font_size_spin.value()}"
        mono_str = f"{self.mono_font_combo.currentFont().family()}, {self.mono_size_spin.value()}"

        self._config.set_theme(self.theme_combo.currentText())
        self._config.set_icon_theme(self.icon_combo.currentText())
        self._config.set_gtk_theme(self.gtk_combo.currentText())
        self._config.set_cursor_theme(self.cursor_combo.currentText())
        self._config.set_cursor_size(self.cursor_size_spin.value())
        self._config.set_font(font_str)
        self._config.set_fixed_font(mono_str)

        QMessageBox.information(self, "Applied", "LXQt appearance updated.\nRestart LXQt session to apply.")


class PanelPage(QWidget):
    """LXQt panel layout manager."""

    def __init__(self):
        super().__init__()
        self._config = PanelConfig()
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("<h2>Panel Configuration</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        # Panel selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Panel:"))
        self.panel_combo = QComboBox()
        self.panel_combo.currentTextChanged.connect(self._load_panel)
        selector_layout.addWidget(self.panel_combo)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        # Settings
        settings_group = QGroupBox("Panel Settings")
        settings_form = QFormLayout()

        self.size_spin = QSpinBox()
        self.size_spin.setRange(16, 128)
        settings_form.addRow("Height/Width:", self.size_spin)

        self.position_combo = QComboBox()
        self.position_combo.addItems(["top", "bottom", "left", "right"])
        settings_form.addRow("Position:", self.position_combo)

        self.alignment_combo = QComboBox()
        self.alignment_combo.addItems(["left", "center", "right"])
        settings_form.addRow("Alignment:", self.alignment_combo)

        self.icon_size_spin = QSpinBox()
        self.icon_size_spin.setRange(8, 128)
        settings_form.addRow("Icon Size:", self.icon_size_spin)

        settings_group.setLayout(settings_form)
        layout.addWidget(settings_group)

        # Plugins
        plugins_group = QGroupBox("Active Plugins")
        plugins_layout = QVBoxLayout()

        self.plugins_list = QListWidget()
        self.plugins_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        plugins_layout.addWidget(self.plugins_list)

        plugins_btn_layout = QHBoxLayout()
        move_up_btn = QPushButton("Move Up")
        move_up_btn.clicked.connect(self._move_up)
        plugins_btn_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton("Move Down")
        move_down_btn.clicked.connect(self._move_down)
        plugins_btn_layout.addWidget(move_down_btn)

        plugins_btn_layout.addStretch()
        plugins_layout.addLayout(plugins_btn_layout)

        plugins_group.setLayout(plugins_layout)
        layout.addWidget(plugins_group)

        # Buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px 24px;")
        apply_btn.clicked.connect(self._apply)
        btn_layout.addWidget(apply_btn)

        restart_btn = QPushButton("Restart Panel")
        restart_btn.clicked.connect(self._restart_panel)
        btn_layout.addWidget(restart_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _load(self):
        self.panel_combo.clear()
        panels = self._config.get_panels()
        self.panel_combo.addItems(panels)
        if panels:
            self._load_panel(panels[0])

    def _load_panel(self, panel: str):
        if not panel:
            return
        self.size_spin.setValue(self._config.get_panel_size(panel))
        self.position_combo.setCurrentText(self._config.get_panel_position(panel))
        self.alignment_combo.setCurrentText(self._config.get_panel_alignment(panel))
        self.icon_size_spin.setValue(self._config.get_icon_size(panel))

        self.plugins_list.clear()
        for plugin in self._config.get_panel_plugins(panel):
            self.plugins_list.addItem(plugin)

    def _move_up(self):
        row = self.plugins_list.currentRow()
        if row > 0:
            item = self.plugins_list.takeItem(row)
            self.plugins_list.insertItem(row - 1, item)
            self.plugins_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.plugins_list.currentRow()
        if row < self.plugins_list.count() - 1 and row >= 0:
            item = self.plugins_list.takeItem(row)
            self.plugins_list.insertItem(row + 1, item)
            self.plugins_list.setCurrentRow(row + 1)

    def _apply(self):
        panel = self.panel_combo.currentText()
        if not panel:
            return

        self._config.set_panel_size(panel, self.size_spin.value())
        self._config.set_panel_position(panel, self.position_combo.currentText())
        self._config.set_panel_alignment(panel, self.alignment_combo.currentText())
        self._config.set_icon_size(panel, self.icon_size_spin.value())

        plugins = [self.plugins_list.item(i).text() for i in range(self.plugins_list.count())]
        self._config.set_panel_plugins(panel, plugins)

        QMessageBox.information(self, "Applied", "Panel settings saved.\nRestart panel to apply.")

    def _restart_panel(self):
        subprocess.Popen("killall lxqt-panel; sleep 1; lxqt-panel &", shell=True)
        QMessageBox.information(self, "Restarted", "Panel restarted.")


class ColorSchemePage(QWidget):
    """Color scheme manager for the full desktop."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("<h2>Color Scheme</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        desc = QLabel("Define the complete color palette for your desktop. Colors apply to Labwc, LXQt, and widget themes.")
        desc.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Color groups
        colors_group = QGroupBox("Desktop Colors")
        colors_form = QFormLayout()

        self.bg_color = QLineEdit(theme.colors.background)
        colors_form.addRow("Background:", self.bg_color)

        self.fg_color = QLineEdit(theme.colors.foreground)
        colors_form.addRow("Foreground:", self.fg_color)

        self.accent_color = QLineEdit(theme.colors.accent)
        colors_form.addRow("Accent:", self.accent_color)

        self.border_color = QLineEdit(theme.colors.border)
        colors_form.addRow("Border:", self.border_color)

        self.text_primary = QLineEdit(theme.colors.text_primary)
        colors_form.addRow("Text Primary:", self.text_primary)

        self.text_secondary = QLineEdit(theme.colors.text_secondary)
        colors_form.addRow("Text Secondary:", self.text_secondary)

        colors_group.setLayout(colors_form)
        layout.addWidget(colors_group)

        # Bar colors
        bar_group = QGroupBox("Monitor Bar Colors")
        bar_form = QFormLayout()

        self.bar_cpu = QLineEdit(theme.colors.bar_cpu)
        bar_form.addRow("CPU:", self.bar_cpu)

        self.bar_ram = QLineEdit(theme.colors.bar_ram)
        bar_form.addRow("RAM:", self.bar_ram)

        self.bar_disk = QLineEdit(theme.colors.bar_disk)
        bar_form.addRow("Disk:", self.bar_disk)

        self.bar_network = QLineEdit(theme.colors.bar_network)
        bar_form.addRow("Network:", self.bar_network)

        bar_group.setLayout(bar_form)
        layout.addWidget(bar_group)

        # Preview
        preview_group = QGroupBox("Preview")
        preview_inner = QVBoxLayout()

        self.preview_frame = QFrame()
        self.preview_frame.setFixedHeight(80)
        self.preview_frame.setStyleSheet(f"""
            background-color: {self.bg_color.text()};
            border: 2px solid {self.border_color.text()};
            border-radius: 8px;
        """)
        preview_layout = QHBoxLayout(self.preview_frame)
        preview_label = QLabel("Sample Widget")
        preview_label.setStyleSheet(f"color: {self.fg_color.text()}; font-size: 14px;")
        preview_layout.addWidget(preview_label)
        preview_btn = QPushButton("Accent Button")
        preview_btn.setStyleSheet(f"""
            background-color: {self.accent_color.text()};
            color: {self.fg_color.text()};
            border-radius: 4px;
            padding: 4px 12px;
        """)
        preview_layout.addWidget(preview_btn)
        preview_inner.addWidget(self.preview_frame)

        # Connect for live preview
        self.bg_color.textChanged.connect(self._update_preview)
        self.fg_color.textChanged.connect(self._update_preview)
        self.accent_color.textChanged.connect(self._update_preview)
        self.border_color.textChanged.connect(self._update_preview)

        preview_group.setLayout(preview_inner)
        layout.addWidget(preview_group)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply Colors")
        apply_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px 24px;")
        apply_btn.clicked.connect(self._apply)
        btn_layout.addWidget(apply_btn)

        reset_btn = QPushButton("Reset to System")
        reset_btn.clicked.connect(self._reset)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _update_preview(self):
        self.preview_frame.setStyleSheet(f"""
            background-color: {self.bg_color.text()};
            border: 2px solid {self.border_color.text()};
            border-radius: 8px;
        """)

    def _apply(self):
        theme.set_custom_color("background", self.bg_color.text())
        theme.set_custom_color("foreground", self.fg_color.text())
        theme.set_custom_color("accent", self.accent_color.text())
        theme.set_custom_color("border", self.border_color.text())
        theme.set_custom_color("text_primary", self.text_primary.text())
        theme.set_custom_color("text_secondary", self.text_secondary.text())
        theme.set_custom_color("bar_cpu", self.bar_cpu.text())
        theme.set_custom_color("bar_ram", self.bar_ram.text())
        theme.set_custom_color("bar_disk", self.bar_disk.text())
        theme.set_custom_color("bar_network", self.bar_network.text())
        theme.save_custom_colors()
        theme.update_from_palette()
        QMessageBox.information(self, "Applied", "Color scheme applied to NaraVisuals widgets.")

    def _reset(self):
        theme._custom_colors.clear()
        theme.save_custom_colors()
        theme.update_from_palette()
        self.bg_color.setText(theme.colors.background)
        self.fg_color.setText(theme.colors.foreground)
        self.accent_color.setText(theme.colors.accent)
        self.border_color.setText(theme.colors.border)
        self.text_primary.setText(theme.colors.text_primary)
        self.text_secondary.setText(theme.colors.text_secondary)
        self.bar_cpu.setText(theme.colors.bar_cpu)
        self.bar_ram.setText(theme.colors.bar_ram)
        self.bar_disk.setText(theme.colors.bar_disk)
        self.bar_network.setText(theme.colors.bar_network)
        QMessageBox.information(self, "Reset", "Colors reset to system defaults.")


class BrowseThemesPage(QWidget):
    """Browse and install curated theme presets."""

    theme_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._themes: list[dict] = []
        self._load_catalog()
        self._setup_ui()
        self._load_themes()

    def _load_catalog(self):
        try:
            with open(STORE_DATA) as f:
                self._themes = json.load(f).get("themes", [])
        except Exception:
            self._themes = []

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        header = QLabel("<h2>Theme Presets</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search presets...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        self.category_combo = QComboBox()
        cats = set(t.get("category", "") for t in self._themes)
        self.category_combo.addItems(["All"] + sorted(cats))
        self.category_combo.currentTextChanged.connect(self._on_search)
        search_layout.addWidget(self.category_combo)

        layout.addLayout(search_layout)

        # Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.scroll.setWidget(self.grid_widget)
        layout.addWidget(self.scroll)

    def _load_themes(self, themes: Optional[list[dict]] = None):
        if themes is None:
            themes = self._themes

        while self.grid_layout.count():
            w = self.grid_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

        for i, t in enumerate(themes):
            card = self._make_card(t)
            row, col = divmod(i, 4)
            self.grid_layout.addWidget(card, row, col)

    def _make_card(self, theme_data: dict) -> QFrame:
        card = QFrame()
        card.setFixedSize(200, 160)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame { background-color: #2a2a3e; border: 1px solid #444466; border-radius: 8px; }
            QFrame:hover { border-color: #3daee9; }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Color strip
        colors = theme_data.get("preview_colors", {})
        strip = QFrame()
        strip.setFixedHeight(30)
        strip.setStyleSheet(f"background: {colors.get('background', '#333')}; border-radius: 4px;")
        layout.addWidget(strip)

        name = QLabel(theme_data.get("name", ""))
        name.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        cat = QLabel(theme_data.get("category", ""))
        cat.setStyleSheet("color: #888888; font-size: 10px;")
        cat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(cat)

        apply_btn = QPushButton("Apply")
        apply_btn.setFixedHeight(24)
        apply_btn.setStyleSheet("background-color: #3daee9; color: white; font-size: 10px; padding: 2px;")
        apply_btn.clicked.connect(lambda checked, td=theme_data: self._apply_preset(td))
        layout.addWidget(apply_btn)

        return card

    def _on_search(self):
        query = self.search_input.text().lower()
        cat = self.category_combo.currentText()
        filtered = self._themes
        if cat != "All":
            filtered = [t for t in filtered if t.get("category") == cat]
        if query:
            filtered = [t for t in filtered if query in t.get("name", "").lower()
                        or query in t.get("description", "").lower()
                        or any(query in tag for tag in t.get("tags", []))]
        self._load_themes(filtered)

    def _apply_preset(self, theme_data: dict):
        colors = theme_data.get("preview_colors", {})
        components = theme_data.get("components", {})

        # Apply Labwc theme
        labwc_theme = components.get("labwc_theme", "")
        if labwc_theme and labwc_theme != "None":
            config = LabwcConfig()
            config.set_theme_name(labwc_theme)

        # Apply LXQt theme
        lxqt_theme = components.get("lxqt_theme", "")
        if lxqt_theme:
            config = LxQtConfig()
            config.set_theme(lxqt_theme)

        # Apply Kvantum
        kvantum_theme = components.get("kvantum_theme", "")
        if kvantum_theme and kvantum_theme != "None":
            KVANTUM_DIR.mkdir(parents=True, exist_ok=True)
            (KVANTUM_DIR / "kvantum.conf").write_text(f"[General]\nTheme={kvantum_theme}\n")

        # Apply colors
        if colors:
            theme.set_custom_color("background", colors.get("background", ""))
            theme.set_custom_color("foreground", colors.get("foreground", ""))
            theme.set_custom_color("accent", colors.get("accent", ""))
            theme.set_custom_color("border", colors.get("border", ""))
            theme.save_custom_colors()
            theme.update_from_palette()

        QMessageBox.information(self, "Applied", f"Preset '{theme_data['name']}' applied.")


# =============================================================================
# Main Window
# =============================================================================

class ThemeManagerWindow(QMainWindow):
    """Comprehensive theme manager for LXQt desktop."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NaraVisuals Theme Manager")
        self.setGeometry(100, 100, 1100, 750)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #1a1a2e;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        logo = QLabel("Theme\nManager")
        logo.setStyleSheet("color: #3daee9; font-size: 18px; font-weight: bold; padding: 20px 15px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)

        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget { background-color: #1a1a2e; color: #cccccc; border: none; font-size: 13px; }
            QListWidget::item { padding: 12px 15px; border-bottom: 1px solid #222244; }
            QListWidget::item:selected { background-color: #3daee9; color: white; }
            QListWidget::item:hover { background-color: #222244; }
        """)
        sidebar_layout.addWidget(self.nav_list)

        sidebar_layout.addStretch()

        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; padding: 10px; border: none; margin: 10px; border-radius: 4px; }
            QPushButton:hover { background-color: #c0392b; }
        """)
        exit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(exit_btn)

        main_layout.addWidget(sidebar)

        # Content
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        pages_data = [
            ("Browse Presets", BrowseThemesPage),
            ("Labwc", LabwcPage),
            ("LXQt", LxQtPage),
            ("Panel", PanelPage),
            ("Colors", ColorSchemePage),
        ]

        for name, cls in pages_data:
            self.nav_list.addItem(name)
            page = cls()
            self.pages.addWidget(page)

        self.nav_list.currentRowChanged.connect(self.pages.setCurrentIndex)
        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)

        self.statusBar().showMessage("Ready")


# =============================================================================
# Entry Point
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setStyleSheet("""
        QMainWindow { background-color: #12121f; }
        QWidget { background-color: #12121f; color: #ffffff; }
        QGroupBox { border: 1px solid #555555; border-radius: 5px; margin-top: 10px; padding-top: 10px; font-weight: bold; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QPushButton { background-color: #3daee9; color: white; border: none; padding: 8px 16px; border-radius: 4px; }
        QPushButton:hover { background-color: #2980b9; }
        QLineEdit, QSpinBox, QComboBox { background-color: #2a2a3e; color: white; border: 1px solid #444466; padding: 6px; border-radius: 4px; }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border: 1px solid #3daee9; }
        QListWidget { background-color: #1a1a2e; color: white; border: 1px solid #444466; }
        QScrollArea { border: none; background: transparent; }
        QStatusBar { background-color: #1a1a2e; color: #888888; }
        QFontComboBox { background-color: #2a2a3e; color: white; border: 1px solid #444466; padding: 6px; }
    """)

    win = ThemeManagerWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
