"""NaraVisuals Desktop Manager - Browse, create, and manage .desktop files.

Centralized GUI for managing application launchers across all standard
XDG directories: user, system, flatpak, snap, and more.
"""
import sys
import os
import stat
import shutil
import configparser
from pathlib import Path
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QStackedWidget, QLabel, QLineEdit,
    QComboBox, QFormLayout, QFrame, QMessageBox, QFileDialog,
    QListWidgetItem, QScrollArea, QGridLayout, QTextEdit,
    QProgressBar, QCheckBox, QSlider, QSizePolicy, QSpinBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMenu, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QFont, QIcon, QColor, QPixmap, QPainter


# =============================================================================
# Constants
# =============================================================================

DESKTOP_DIRS = [
    Path.home() / ".local/share/applications",
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications"),
    Path.home() / ".local/share/flatpak/exports/share/applications",
    Path("/var/lib/flatpak/exports/share/applications"),
    Path("/var/lib/snapd/desktop/applications"),
]

ICON_DIRS = [
    Path.home() / ".local/share/icons",
    Path("/usr/share/icons"),
    Path("/usr/local/share/icons"),
]

AUTOSTART_DIR = Path.home() / ".config/autostart"

CATEGORIES = [
    "AudioVideo", "Audio", "Video", "Development", "Education",
    "Game", "Graphics", "Network", "Office", "Science",
    "Settings", "System", "Utility"
]

KNOWN_EXECUTABLE_PATHS = [
    "/usr/bin", "/usr/local/bin", "/usr/sbin",
    "/usr/local/sbin", "/snap/bin", "/var/lib/flatpak/exports/bin",
    str(Path.home() / ".local/bin"),
    str(Path.home() / ".cargo/bin"),
    str(Path.home() / ".npm-global/bin"),
]

COMMON_MIMETYPES = [
    "application/pdf", "application/json", "text/plain",
    "image/png", "image/jpeg", "video/mp4", "audio/mpeg",
    "inode/directory", "x-scheme-handler/http", "x-scheme-handler/https",
]


# =============================================================================
# Desktop Entry Parser
# =============================================================================

class DesktopEntry:
    """Parsed representation of a .desktop file."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.optionxform = str
        self._load()

    def _load(self):
        try:
            self.config.read(str(self.filepath), encoding="utf-8")
        except Exception:
            try:
                self.config.read(str(self.filepath), encoding="latin-1")
            except Exception:
                pass

    @property
    def section(self) -> str:
        for s in self.config.sections():
            if s.lower() == "desktop entry":
                return s
        return "Desktop Entry" if self.config.has_section("Desktop Entry") else ""

    def get(self, key: str, fallback: str = "") -> str:
        if self.section:
            return self.config.get(self.section, key, fallback=fallback)
        return fallback

    def set(self, key: str, value: str):
        if not self.config.has_section("Desktop Entry"):
            self.config.add_section("Desktop Entry")
        self.config.set("Desktop Entry", key, value)

    @property
    def name(self) -> str:
        return self.get("Name", self.filepath.stem)

    @property
    def exec_command(self) -> str:
        return self.get("Exec", "")

    @property
    def icon(self) -> str:
        return self.get("Icon", "")

    @property
    def comment(self) -> str:
        return self.get("Comment", "")

    @property
    def categories(self) -> str:
        return self.get("Categories", "")

    @property
    def terminal(self) -> bool:
        return self.get("Terminal", "false").lower() == "true"

    @property
    def nodisplay(self) -> bool:
        return self.get("NoDisplay", "false").lower() == "true"

    @property
    def hidden(self) -> bool:
        return self.get("Hidden", "false").lower() == "true"

    @property
    def type(self) -> str:
        return self.get("Type", "Application")

    @property
    def mimetype(self) -> str:
        return self.get("MimeType", "")

    @property
    def keywords(self) -> str:
        return self.get("Keywords", "")

    @property
    def startup_notify(self) -> bool:
        return self.get("StartupNotify", "false").lower() == "true"

    @property
    def location(self) -> str:
        parts = []
        for d in DESKTOP_DIRS:
            if self.filepath.parent == d or str(self.filepath.parent).endswith(str(d)):
                parts.append(d.name if d != AUTOSTART_DIR else "autostart")
                break
        if not parts:
            parts.append(self.filepath.parent.name)
        return "/".join(parts) if parts else "unknown"

    @property
    def source_dir(self) -> str:
        for d in DESKTOP_DIRS:
            try:
                if self.filepath.resolve().is_relative_to(d.resolve()):
                    return str(d)
            except (ValueError, OSError):
                continue
        return str(self.filepath.parent)

    def is_user_editable(self) -> bool:
        user_dir = Path.home() / ".local/share/applications"
        try:
            return self.filepath.resolve().is_relative_to(user_dir.resolve())
        except (ValueError, OSError):
            return False

    def is_executable(self) -> bool:
        try:
            return os.access(self.filepath, os.X_OK)
        except Exception:
            return False

    def set_executable(self, executable: bool):
        try:
            st = os.stat(self.filepath)
            if executable:
                os.chmod(self.filepath, st.st_mode | stat.S_IEXEC)
            else:
                os.chmod(self.filepath, st.st_mode & ~stat.S_IEXEC)
        except Exception:
            pass

    def save(self):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            self.config.write(f)

    def to_dict(self) -> dict:
        return {
            "filepath": str(self.filepath),
            "name": self.name,
            "exec": self.exec_command,
            "icon": self.icon,
            "comment": self.comment,
            "categories": self.categories,
            "terminal": self.terminal,
            "nodisplay": self.nodisplay,
            "hidden": self.hidden,
            "type": self.type,
            "mimetype": self.mimetype,
            "keywords": self.keywords,
            "location": self.location,
            "source_dir": self.source_dir,
            "editable": self.is_user_editable(),
            "executable": self.is_executable(),
        }


# =============================================================================
# Desktop File Scanner
# =============================================================================

class DesktopScanner:
    """Scans system directories for .desktop files."""

    def __init__(self):
        self._cache: dict[str, DesktopEntry] = {}

    def scan_all(self) -> list[DesktopEntry]:
        self._cache.clear()
        for d in DESKTOP_DIRS:
            if d.is_dir():
                for f in d.glob("*.desktop"):
                    try:
                        entry = DesktopEntry(f)
                        self._cache[str(f)] = entry
                    except Exception:
                        pass
        return list(self._cache.values())

    def scan_directory(self, path: Path) -> list[DesktopEntry]:
        results = []
        if path.is_dir():
            for f in path.glob("*.desktop"):
                try:
                    entry = DesktopEntry(f)
                    results.append(entry)
                except Exception:
                    pass
        return results

    def get_by_path(self, filepath: str) -> Optional[DesktopEntry]:
        return self._cache.get(filepath)

    def search(self, query: str) -> list[DesktopEntry]:
        q = query.lower()
        return [
            e for e in self._cache.values()
            if q in e.name.lower()
            or q in e.exec_command.lower()
            or q in e.comment.lower()
            or q in e.keywords.lower()
            or q in e.categories.lower()
        ]

    def filter_by_category(self, category: str) -> list[DesktopEntry]:
        return [
            e for e in self._cache.values()
            if category in e.categories
        ]

    def filter_by_type(self, entry_type: str) -> list[DesktopEntry]:
        return [e for e in self._cache.values() if e.type == entry_type]

    def get_by_location(self, location: str) -> list[DesktopEntry]:
        return [e for e in self._cache.values() if location in e.location]

    def get_hidden(self) -> list[DesktopEntry]:
        return [e for e in self._cache.values() if e.hidden or e.nodisplay]

    def get_editable(self) -> list[DesktopEntry]:
        return [e for e in self._cache.values() if e.is_user_editable()]

    def get_non_executable(self) -> list[DesktopEntry]:
        return [e for e in self._cache.values() if not e.is_executable()]


# =============================================================================
# Icon Finder
# =============================================================================

class IconFinder:
    """Find and manage icons for desktop entries."""

    def __init__(self):
        self._icon_cache: dict[str, str] = {}

    def find_icon(self, icon_name: str) -> Optional[str]:
        if not icon_name:
            return None

        # Absolute path
        if os.path.isabs(icon_name) and os.path.isfile(icon_name):
            return icon_name

        # Search in standard icon dirs
        for icon_dir in ICON_DIRS:
            if not icon_dir.is_dir():
                continue
            for ext in [".png", ".svg", ".xpm"]:
                # Direct lookup
                candidate = icon_dir / f"{icon_name}{ext}"
                if candidate.is_file():
                    return str(candidate)
                # Hicolor theme lookup
                for size in ["16x16", "22x22", "24x24", "32x32", "48x48", "64x64", "128x128", "256x256", "scalable"]:
                    candidate = icon_dir / "hicolor" / size / "apps" / f"{icon_name}{ext}"
                    if candidate.is_file():
                        return str(candidate)

        # Fallback: try xdg-icon-resource
        return None

    def get_icon_pixmap(self, icon_name: str, size: int = 48) -> QPixmap:
        path = self.find_icon(icon_name)
        if path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
        return self._create_placeholder(icon_name, size)

    def _create_placeholder(self, name: str, size: int) -> QPixmap:
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor("#2a2a3e"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#888888"))
        painter.setFont(QFont("Monospace", 8))
        text = name[:2].upper() if name else "??"
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        return pixmap

    def list_available_icons(self) -> list[str]:
        icons = set()
        for icon_dir in ICON_DIRS:
            if not icon_dir.is_dir():
                continue
            for f in icon_dir.rglob("*.png"):
                icons.add(f.stem)
            for f in icon_dir.rglob("*.svg"):
                icons.add(f.stem)
        return sorted(icons)


# =============================================================================
# Pages
# =============================================================================

class BrowsePage(QWidget):
    """Browse and manage all .desktop files."""

    entry_selected = pyqtSignal(str)

    def __init__(self, scanner: DesktopScanner, icon_finder: IconFinder):
        super().__init__()
        self._scanner = scanner
        self._icon_finder = icon_finder
        self._all_entries: list[DesktopEntry] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header
        header = QLabel("<h2>Desktop Entries</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, exec, comment, keywords...")
        self.search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_input)

        self.location_combo = QComboBox()
        self.location_combo.addItems(["All Locations", "User", "System", "Flatpak", "Snap", "Autostart"])
        self.location_combo.currentTextChanged.connect(self._on_filter_changed)
        self.location_combo.setFixedWidth(140)
        toolbar.addWidget(self.location_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Types", "Application", "Link", "Directory"])
        self.type_combo.currentTextChanged.connect(self._on_filter_changed)
        self.type_combo.setFixedWidth(120)
        toolbar.addWidget(self.type_combo)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        toolbar.addWidget(refresh_btn)

        layout.addLayout(toolbar)

        # Stats bar
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.stats_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["", "Name", "Exec", "Location", "Type", "Status", "File"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._context_menu)
        self.table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

        # Action bar
        action_bar = QHBoxLayout()

        self.enable_btn = QPushButton("Enable")
        self.enable_btn.clicked.connect(self._enable_entry)
        action_bar.addWidget(self.enable_btn)

        self.disable_btn = QPushButton("Disable")
        self.disable_btn.clicked.connect(self._disable_entry)
        action_bar.addWidget(self.disable_btn)

        self.exec_btn = QPushButton("Set Executable")
        self.exec_btn.clicked.connect(self._toggle_executable)
        action_bar.addWidget(self.exec_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background-color: #e74c3c;")
        self.delete_btn.clicked.connect(self._delete_entry)
        action_bar.addWidget(self.delete_btn)

        action_bar.addStretch()

        self.count_label = QLabel("0 entries")
        self.count_label.setStyleSheet("color: #888888;")
        action_bar.addWidget(self.count_label)

        layout.addLayout(action_bar)

        self._refresh()

    def _refresh(self):
        self._all_entries = self._scanner.scan_all()
        self._apply_filters()

    def _apply_filters(self):
        query = self.search_input.text().strip().lower()
        location = self.location_combo.currentText()
        entry_type = self.type_combo.currentText()

        entries = self._all_entries

        if query:
            entries = [e for e in entries if query in e.name.lower() or query in e.exec_command.lower()
                       or query in e.comment.lower() or query in e.keywords.lower()]

        if location != "All Locations":
            location_map = {
                "User": ".local",
                "System": "/usr/",
                "Flatpak": "flatpak",
                "Snap": "snap",
                "Autostart": "autostart",
            }
            loc_filter = location_map.get(location, "")
            entries = [e for e in entries if loc_filter in str(e.filepath)]

        if entry_type != "All Types":
            entries = [e for e in entries if e.type == entry_type]

        self._populate_table(entries)

    def _populate_table(self, entries: list[DesktopEntry]):
        self.table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            # Icon
            icon_item = QTableWidgetItem()
            pixmap = self._icon_finder.get_icon_pixmap(entry.icon, 24)
            icon_item.setIcon(QIcon(pixmap))
            self.table.setItem(i, 0, icon_item)

            # Name
            name_item = QTableWidgetItem(entry.name)
            name_item.setData(Qt.ItemDataRole.UserRole, str(entry.filepath))
            self.table.setItem(i, 1, name_item)

            # Exec
            self.table.setItem(i, 2, QTableWidgetItem(entry.exec_command[:60]))

            # Location
            self.table.setItem(i, 3, QTableWidgetItem(entry.location))

            # Type
            self.table.setItem(i, 4, QTableWidgetItem(entry.type))

            # Status
            status_parts = []
            if entry.hidden:
                status_parts.append("Hidden")
            if entry.nodisplay:
                status_parts.append("NoDisplay")
            if entry.terminal:
                status_parts.append("Terminal")
            if not entry.is_executable():
                status_parts.append("Not Exec")
            status = ", ".join(status_parts) if status_parts else "OK"
            status_item = QTableWidgetItem(status)
            if status != "OK":
                status_item.setForeground(QColor("#f39c12"))
            self.table.setItem(i, 5, status_item)

            # File
            self.table.setItem(i, 6, QTableWidgetItem(entry.filepath.name))

        self.count_label.setText(f"{len(entries)} entries")
        self._update_stats()

    def _update_stats(self):
        total = len(self._all_entries)
        user = len([e for e in self._all_entries if e.is_user_editable()])
        hidden = len([e for e in self._all_entries if e.hidden or e.nodisplay])
        non_exec = len([e for e in self._all_entries if not e.is_executable()])
        self.stats_label.setText(
            f"Total: {total} | User: {user} | Hidden: {hidden} | Non-executable: {non_exec}"
        )

    def _on_search(self):
        self._apply_filters()

    def _on_filter_changed(self):
        self._apply_filters()

    def _get_selected_entry(self) -> Optional[DesktopEntry]:
        row = self.table.currentRow()
        if row >= 0:
            filepath = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)
            if filepath:
                return self._scanner.get_by_path(filepath)
        return None

    def _on_double_click(self):
        entry = self._get_selected_entry()
        if entry:
            self.entry_selected.emit(str(entry.filepath))

    def _enable_entry(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        if not entry.is_user_editable():
            QMessageBox.warning(self, "Read Only", "This entry is in a system directory and cannot be modified.\nCopy it to ~/.local/share/applications/ first.")
            return
        entry.set("Hidden", "false")
        entry.set("NoDisplay", "false")
        entry.save()
        self._refresh()

    def _disable_entry(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        if not entry.is_user_editable():
            QMessageBox.warning(self, "Read Only", "This entry is in a system directory and cannot be modified.")
            return
        entry.set("Hidden", "true")
        entry.save()
        self._refresh()

    def _toggle_executable(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        current = entry.is_executable()
        entry.set_executable(not current)
        self._refresh()

    def _delete_entry(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        if not entry.is_user_editable():
            QMessageBox.warning(self, "Read Only", "Cannot delete system entries.")
            return
        reply = QMessageBox.question(
            self, "Delete Entry",
            f"Delete '{entry.name}'?\n\n{entry.filepath}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                entry.filepath.unlink()
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete:\n{e}")

    def _context_menu(self, pos):
        entry = self._get_selected_entry()
        if not entry:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2a2a3e;
                color: white;
                border: 1px solid #444466;
            }
            QMenu::item:selected {
                background-color: #3daee9;
            }
        """)

        open_action = menu.addAction("Open File Location")
        open_action.triggered.connect(lambda: self._open_location(entry))

        copy_action = menu.addAction("Copy to User Directory")
        copy_action.triggered.connect(lambda: self._copy_to_user(entry))

        menu.addSeparator()

        exec_action = menu.addAction("Toggle Executable")
        exec_action.triggered.connect(lambda: self._toggle_executable())

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _open_location(self, entry: DesktopEntry):
        subprocess.Popen(["xdg-open", str(entry.filepath.parent)])

    def _copy_to_user(self, entry: DesktopEntry):
        dest = Path.home() / ".local/share/applications" / entry.filepath.name
        if dest.exists():
            reply = QMessageBox.question(
                self, "Overwrite",
                f"'{entry.filepath.name}' already exists in user directory.\nOverwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        shutil.copy2(str(entry.filepath), str(dest))
        self._refresh()
        QMessageBox.information(self, "Copied", f"Copied to:\n{dest}")


class CreatePage(QWidget):
    """Create new .desktop entries."""

    entry_created = pyqtSignal(str)

    def __init__(self, scanner: DesktopScanner, icon_finder: IconFinder):
        super().__init__()
        self._scanner = scanner
        self._icon_finder = icon_finder
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("<h2>Create Desktop Entry</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        # Form
        form_group = QGroupBox("Basic Info")
        form_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Application")
        form.addRow("Name:", self.name_input)

        self.exec_input = QLineEdit()
        self.exec_input.setPlaceholderText("/usr/bin/my-app %U")
        form.addRow("Exec:", self.exec_input)

        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("A brief description")
        form.addRow("Comment:", self.comment_input)

        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("icon-name or /path/to/icon.png")
        browse_icon_btn = QPushButton("Browse")
        browse_icon_btn.setFixedWidth(60)
        browse_icon_btn.clicked.connect(self._browse_icon)
        icon_row = QHBoxLayout()
        icon_row.addWidget(self.icon_input)
        icon_row.addWidget(browse_icon_btn)
        icon_widget = QWidget()
        icon_widget.setLayout(icon_row)
        form.addRow("Icon:", icon_widget)

        self.terminal_check = QCheckBox("Run in terminal")
        form.addRow("Terminal:", self.terminal_check)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Application", "Link", "Directory"])
        form.addRow("Type:", self.type_combo)

        form_group.setLayout(form)
        layout.addWidget(form_group)

        # Categories
        cat_group = QGroupBox("Categories")
        cat_group.setStyleSheet(form_group.styleSheet())
        cat_layout = QHBoxLayout()

        self.category_list = QListWidget()
        self.category_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for cat in CATEGORIES:
            self.category_list.addItem(cat)
        cat_layout.addWidget(self.category_list)

        cat_group.setLayout(cat_layout)
        layout.addWidget(cat_group)

        # Keywords
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("keyword1;keyword2;keyword3")
        layout.addWidget(QLabel("Keywords:"))
        layout.addWidget(self.keywords_input)

        # Save location
        location_group = QGroupBox("Save Location")
        location_group.setStyleSheet(form_group.styleSheet())
        location_form = QFormLayout()

        self.save_dir_combo = QComboBox()
        for d in DESKTOP_DIRS:
            if d.is_dir() or d == Path.home() / ".local/share/applications":
                self.save_dir_combo.addItem(str(d), str(d))
        self.save_dir_combo.addItem(str(AUTOSTART_DIR), str(AUTOSTART_DIR))
        location_form.addRow("Directory:", self.save_dir_combo)

        self.autostart_check = QCheckBox("Add to autostart")
        location_form.addRow("Autostart:", self.autostart_check)

        location_group.setLayout(location_form)
        layout.addWidget(location_group)

        # Preview
        preview_group = QGroupBox("Preview")
        preview_group.setStyleSheet(form_group.styleSheet())
        preview_layout = QVBoxLayout()

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(120)
        self.preview_text.setStyleSheet("background-color: #1a1a2e; color: #00ff00; font-family: monospace; font-size: 11px;")
        preview_layout.addWidget(self.preview_text)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Connect changes to preview
        self.name_input.textChanged.connect(self._update_preview)
        self.exec_input.textChanged.connect(self._update_preview)
        self.comment_input.textChanged.connect(self._update_preview)
        self.icon_input.textChanged.connect(self._update_preview)
        self.terminal_check.stateChanged.connect(self._update_preview)
        self.type_combo.currentTextChanged.connect(self._update_preview)

        # Action buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Desktop Entry")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 24px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        clear_btn = QPushButton("Clear Form")
        clear_btn.clicked.connect(self._clear)
        btn_layout.addWidget(clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

    def _update_preview(self):
        name = self.name_input.text() or "Application Name"
        exec_cmd = self.exec_input.text() or "/usr/bin/app"
        comment = self.comment_input.text() or "Description"
        icon = self.icon_input.text() or "application-x-executable"
        terminal = "true" if self.terminal_check.isChecked() else "false"
        type_val = self.type_combo.currentText()
        categories = ";".join([item.text() for item in self.category_list.selectedItems()])
        keywords = self.keywords_input.text()

        preview = f"""[Desktop Entry]
Type={type_val}
Name={name}
Exec={exec_cmd}
Icon={icon}
Comment={comment}
Terminal={terminal}
Categories={categories};
Keywords={keywords}
"""
        self.preview_text.setPlainText(preview)

    def _browse_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Icon", "/usr/share/icons",
            "Images (*.png *.svg *.xpm);;All Files (*)"
        )
        if path:
            self.icon_input.setText(path)

    def _clear(self):
        self.name_input.clear()
        self.exec_input.clear()
        self.comment_input.clear()
        self.icon_input.clear()
        self.terminal_check.setChecked(False)
        self.type_combo.setCurrentIndex(0)
        self.category_list.clearSelection()
        self.keywords_input.clear()

    def _save(self):
        name = self.name_input.text().strip()
        exec_cmd = self.exec_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Name Required", "Please enter a name.")
            return
        if not exec_cmd:
            QMessageBox.warning(self, "Exec Required", "Please enter an exec command.")
            return

        # Build filename
        filename = name.lower().replace(" ", "-").replace("/", "-")
        filename = "".join(c for c in filename if c.isalnum() or c in "-_")
        if not filename.endswith(".desktop"):
            filename += ".desktop"

        # Determine save path
        if self.autostart_check.isChecked():
            save_dir = AUTOSTART_DIR
        else:
            save_dir = Path(self.save_dir_combo.currentData())

        save_path = save_dir / filename

        if save_path.exists():
            reply = QMessageBox.question(
                self, "Overwrite",
                f"'{filename}' already exists.\nOverwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Build entry
        entry = DesktopEntry(save_path)
        entry.set("Type", self.type_combo.currentText())
        entry.set("Name", name)
        entry.set("Exec", exec_cmd)
        entry.set("Icon", self.icon_input.text() or "application-x-executable")
        entry.set("Comment", self.comment_input.text())
        entry.set("Terminal", "true" if self.terminal_check.isChecked() else "false")

        categories = [item.text() for item in self.category_list.selectedItems()]
        if categories:
            entry.set("Categories", ";".join(categories) + ";")

        keywords = self.keywords_input.text().strip()
        if keywords:
            entry.set("Keywords", keywords)

        try:
            entry.save()
            entry.set_executable(True)
            self.entry_created.emit(str(save_path))
            QMessageBox.information(self, "Saved", f"Desktop entry saved to:\n{save_path}")
            self._clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")


class EditPage(QWidget):
    """Edit an existing .desktop entry."""

    entry_saved = pyqtSignal(str)

    def __init__(self, scanner: DesktopScanner, icon_finder: IconFinder):
        super().__init__()
        self._scanner = scanner
        self._icon_finder = icon_finder
        self._current_entry: Optional[DesktopEntry] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.header = QLabel("<h2>Edit Desktop Entry</h2>")
        self.header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(self.header)

        self.file_label = QLabel("")
        self.file_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.file_label)

        # Form
        form_group = QGroupBox("Properties")
        form_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        form = QFormLayout()

        self.name_input = QLineEdit()
        form.addRow("Name:", self.name_input)

        self.exec_input = QLineEdit()
        form.addRow("Exec:", self.exec_input)

        self.comment_input = QLineEdit()
        form.addRow("Comment:", self.comment_input)

        self.icon_input = QLineEdit()
        form.addRow("Icon:", self.icon_input)

        self.terminal_check = QCheckBox("Run in terminal")
        form.addRow("Terminal:", self.terminal_check)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Application", "Link", "Directory"])
        form.addRow("Type:", self.type_combo)

        self.categories_input = QLineEdit()
        form.addRow("Categories:", self.categories_input)

        self.keywords_input = QLineEdit()
        form.addRow("Keywords:", self.keywords_input)

        self.mimetype_input = QLineEdit()
        form.addRow("MimeType:", self.mimetype_input)

        self.hidden_check = QCheckBox("Hidden")
        form.addRow("Hidden:", self.hidden_check)

        self.nodisplay_check = QCheckBox("NoDisplay")
        form.addRow("NoDisplay:", self.nodisplay_check)

        self.startup_check = QCheckBox("StartupNotify")
        form.addRow("StartupNotify:", self.startup_check)

        form_group.setLayout(form)
        layout.addWidget(form_group)

        # Raw editor
        raw_group = QGroupBox("Raw Editor")
        raw_group.setStyleSheet(form_group.styleSheet())
        raw_layout = QVBoxLayout()

        self.raw_text = QTextEdit()
        self.raw_text.setStyleSheet("background-color: #1a1a2e; color: #00ff00; font-family: monospace; font-size: 11px;")
        raw_layout.addWidget(self.raw_text)

        raw_group.setLayout(raw_layout)
        layout.addWidget(raw_group)

        # Action buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 24px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        reload_btn = QPushButton("Reload from File")
        reload_btn.clicked.connect(self._reload)
        btn_layout.addWidget(reload_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

    def load_entry(self, filepath: str):
        entry = DesktopEntry(Path(filepath))
        self._current_entry = entry

        self.header.setText(f"<h2>Edit: {entry.name}</h2>")
        self.file_label.setText(str(filepath))

        self.name_input.setText(entry.name)
        self.exec_input.setText(entry.exec_command)
        self.comment_input.setText(entry.comment)
        self.icon_input.setText(entry.icon)
        self.terminal_check.setChecked(entry.terminal)

        idx = self.type_combo.findText(entry.type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)

        self.categories_input.setText(entry.categories)
        self.keywords_input.setText(entry.keywords)
        self.mimetype_input.setText(entry.mimetype)
        self.hidden_check.setChecked(entry.hidden)
        self.nodisplay_check.setChecked(entry.nodisplay)
        self.startup_check.setChecked(entry.startup_notify)

        # Load raw
        try:
            self.raw_text.setPlainText(entry.filepath.read_text(encoding="utf-8"))
        except Exception:
            self.raw_text.setPlainText("")

    def _reload(self):
        if self._current_entry:
            self.load_entry(str(self._current_entry.filepath))

    def _save(self):
        if not self._current_entry:
            return

        entry = self._current_entry

        if not entry.is_user_editable():
            reply = QMessageBox.question(
                self, "System Entry",
                "This is a system entry. Save a copy to user directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                dest = Path.home() / ".local/share/applications" / entry.filepath.name
                entry = DesktopEntry(dest)
                self._current_entry = entry
            else:
                return

        entry.set("Name", self.name_input.text())
        entry.set("Exec", self.exec_input.text())
        entry.set("Comment", self.comment_input.text())
        entry.set("Icon", self.icon_input.text())
        entry.set("Terminal", "true" if self.terminal_check.isChecked() else "false")
        entry.set("Type", self.type_combo.currentText())
        entry.set("Categories", self.categories_input.text())
        entry.set("Keywords", self.keywords_input.text())
        entry.set("MimeType", self.mimetype_input.text())
        entry.set("Hidden", "true" if self.hidden_check.isChecked() else "false")
        entry.set("NoDisplay", "true" if self.nodisplay_check.isChecked() else "false")
        entry.set("StartupNotify", "true" if self.startup_check.isChecked() else "false")

        try:
            entry.save()
            self.entry_saved.emit(str(entry.filepath))
            QMessageBox.information(self, "Saved", f"Saved to:\n{entry.filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")


class ShortcutsPage(QWidget):
    """Manage keyboard shortcuts via .desktop files in autostart."""

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("<h2>Autostart Entries</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        desc = QLabel("Manage applications that start automatically on login.")
        desc.setStyleSheet("color: #aaaaaa; font-size: 13px;")
        layout.addWidget(desc)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Exec", "Enabled", "File"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Actions
        btn_layout = QHBoxLayout()

        enable_btn = QPushButton("Enable Selected")
        enable_btn.clicked.connect(self._enable)
        btn_layout.addWidget(enable_btn)

        disable_btn = QPushButton("Disable Selected")
        disable_btn.clicked.connect(self._disable)
        btn_layout.addWidget(disable_btn)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("background-color: #e74c3c;")
        delete_btn.clicked.connect(self._delete)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

    def _refresh(self):
        AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
        entries = list(AUTOSTART_DIR.glob("*.desktop"))

        self.table.setRowCount(len(entries))
        for i, f in enumerate(entries):
            entry = DesktopEntry(f)
            self.table.setItem(i, 0, QTableWidgetItem(entry.name))
            self.table.setItem(i, 1, QTableWidgetItem(entry.exec_command[:50]))

            enabled = not entry.hidden
            enabled_item = QTableWidgetItem("Yes" if enabled else "No")
            enabled_item.setForeground(QColor("#2ecc71") if enabled else QColor("#e74c3c"))
            self.table.setItem(i, 2, enabled_item)

            name_item = QTableWidgetItem(f.name)
            name_item.setData(Qt.ItemDataRole.UserRole, str(f))
            self.table.setItem(i, 3, name_item)

    def _get_selected(self) -> Optional[Path]:
        row = self.table.currentRow()
        if row >= 0:
            return Path(self.table.item(row, 3).data(Qt.ItemDataRole.UserRole))
        return None

    def _enable(self):
        path = self._get_selected()
        if path:
            entry = DesktopEntry(path)
            entry.set("Hidden", "false")
            entry.save()
            self._refresh()

    def _disable(self):
        path = self._get_selected()
        if path:
            entry = DesktopEntry(path)
            entry.set("Hidden", "true")
            entry.save()
            self._refresh()

    def _delete(self):
        path = self._get_selected()
        if path:
            reply = QMessageBox.question(
                self, "Delete",
                f"Delete '{path.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                path.unlink()
                self._refresh()


class LocationsPage(QWidget):
    """View and manage .desktop file directories."""

    def __init__(self, scanner: DesktopScanner):
        super().__init__()
        self._scanner = scanner
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("<h2>Desktop Entry Locations</h2>")
        header.setStyleSheet("color: #ffffff; font-size: 20px;")
        layout.addWidget(header)

        # Directory list
        self.dir_tree = QTreeWidget()
        self.dir_tree.setHeaderLabels(["Directory", "Entries", "Writable", "Status"])
        self.dir_tree.setRootIsDecorated(False)
        self.dir_tree.setAlternatingRowColors(True)
        layout.addWidget(self.dir_tree)

        # Actions
        btn_layout = QHBoxLayout()

        open_btn = QPushButton("Open Selected")
        open_btn.clicked.connect(self._open_selected)
        btn_layout.addWidget(open_btn)

        create_btn = QPushButton("Create User Dir")
        create_btn.clicked.connect(self._create_user_dir)
        btn_layout.addWidget(create_btn)

        btn_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

    def _refresh(self):
        self.dir_tree.clear()
        for d in DESKTOP_DIRS + [AUTOSTART_DIR]:
            item = QTreeWidgetItem()
            item.setText(0, str(d))
            exists = d.is_dir()
            if exists:
                count = len(list(d.glob("*.desktop")))
                item.setText(1, str(count))
            else:
                item.setText(1, "-")

            writable = os.access(d, os.W_OK) if exists else False
            item.setText(2, "Yes" if writable else "No")

            if not exists:
                item.setText(3, "Missing")
                item.setForeground(3, QColor("#e74c3c"))
            elif writable:
                item.setText(3, "OK")
                item.setForeground(3, QColor("#2ecc71"))
            else:
                item.setText(3, "Read-only")
                item.setForeground(3, QColor("#f39c12"))

            self.dir_tree.addTopLevelItem(item)

    def _open_selected(self):
        item = self.dir_tree.currentItem()
        if item:
            path = item.text(0)
            if os.path.isdir(path):
                subprocess.Popen(["xdg-open", path])

    def _create_user_dir(self):
        user_dir = Path.home() / ".local/share/applications"
        user_dir.mkdir(parents=True, exist_ok=True)
        QMessageBox.information(self, "Created", f"Created:\n{user_dir}")
        self._refresh()


# =============================================================================
# Main Window
# =============================================================================

import subprocess


class DesktopManagerWindow(QMainWindow):
    """Main window for NaraVisuals Desktop Manager."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NaraVisuals Desktop Manager")
        self.setGeometry(100, 100, 1100, 700)

        self._scanner = DesktopScanner()
        self._icon_finder = IconFinder()
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

        logo = QLabel("Desktop\nManager")
        logo.setStyleSheet("color: #3daee9; font-size: 18px; font-weight: bold; padding: 20px 15px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)

        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a2e;
                color: #cccccc;
                border: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #222244;
            }
            QListWidget::item:selected {
                background-color: #3daee9;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #222244;
            }
        """)
        sidebar_layout.addWidget(self.nav_list)

        sidebar_layout.addStretch()

        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border: none;
                margin: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        exit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(exit_btn)

        main_layout.addWidget(sidebar)

        # Content
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        # Pages
        self.browse_page = BrowsePage(self._scanner, self._icon_finder)
        self.browse_page.entry_selected.connect(self._open_editor)
        self.pages.addWidget(self.browse_page)
        self.nav_list.addItem("Browse")

        self.create_page = CreatePage(self._scanner, self._icon_finder)
        self.pages.addWidget(self.create_page)
        self.nav_list.addItem("Create")

        self.edit_page = EditPage(self._scanner, self._icon_finder)
        self.pages.addWidget(self.edit_page)
        self.nav_list.addItem("Edit")

        self.shortcuts_page = ShortcutsPage()
        self.pages.addWidget(self.shortcuts_page)
        self.nav_list.addItem("Autostart")

        self.locations_page = LocationsPage(self._scanner)
        self.pages.addWidget(self.locations_page)
        self.nav_list.addItem("Locations")

        self.nav_list.currentRowChanged.connect(self._on_nav)

        self.statusBar().showMessage("Ready")

    def _on_nav(self, index: int):
        self.pages.setCurrentIndex(index)
        if index == 0:
            self.browse_page._refresh()
        elif index == 3:
            self.shortcuts_page._refresh()
        elif index == 4:
            self.locations_page._refresh()

    def _open_editor(self, filepath: str):
        self.edit_page.load_entry(filepath)
        self.nav_list.setCurrentRow(2)
        self.pages.setCurrentIndex(2)


# =============================================================================
# Entry Point
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setStyleSheet("""
        QMainWindow {
            background-color: #12121f;
        }
        QWidget {
            background-color: #12121f;
            color: #ffffff;
        }
        QGroupBox {
            border: 1px solid #555555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton {
            background-color: #3daee9;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #1f6fa5;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #2a2a3e;
            color: white;
            border: 1px solid #444466;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border: 1px solid #3daee9;
        }
        QListWidget {
            background-color: #1a1a2e;
            color: white;
            border: 1px solid #444466;
        }
        QTableWidget {
            background-color: #1a1a2e;
            color: white;
            border: 1px solid #444466;
            gridline-color: #333355;
        }
        QHeaderView::section {
            background-color: #2a2a3e;
            color: white;
            padding: 6px;
            border: 1px solid #444466;
        }
        QTreeWidget {
            background-color: #1a1a2e;
            color: white;
            border: 1px solid #444466;
        }
        QTreeWidget::item {
            padding: 4px;
        }
        QTreeWidget::item:selected {
            background-color: #3daee9;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        QTextEdit {
            background-color: #1a1a2e;
            color: #00ff00;
            border: 1px solid #444466;
        }
        QStatusBar {
            background-color: #1a1a2e;
            color: #888888;
        }
    """)

    win = DesktopManagerWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
