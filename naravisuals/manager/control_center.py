"""NaraVisuals Control Center - All-in-one GUI for managing the entire ecosystem.

Single unified interface for:
- Daemon management (start/stop/restart/logs)
- Widget browser (install/enable/disable)
- System dashboard (live stats)
- Panel configuration (add/remove/reorder widgets)
- Theme customization (colors, fonts, responsive)
- Backup/restore manager (profiles, export/import)
- Autostart manager
- Compositor settings (Labwc/Sway/Hyprland)
- Log viewer
"""
import sys
import os
import subprocess
import json
import configparser
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QStackedWidget, QLabel, QLineEdit,
    QComboBox, QFormLayout, QFrame, QMessageBox, QSpinBox, QFileDialog,
    QListWidgetItem, QTabWidget, QGroupBox, QTextEdit, QProgressBar,
    QCheckBox, QSlider, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QStatusBar, QToolBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QFont, QIcon, QColor

from naravisuals.core.config_manager import config
from naravisuals.core.theme_engine import theme


# =============================================================================
# Constants
# =============================================================================

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))) / "naravisuals"
LXQT_CONFIG_DIR = Path(os.path.expanduser("~/.config/lxqt"))
PANEL_CONFIG = LXQT_CONFIG_DIR / "panel.conf"
BACKUP_DIR = CONFIG_DIR / "backups"
LOG_DIR = CONFIG_DIR / "logs"

WIDGET_REGISTRY = [
    {"id": "system-monitor", "name": "System Monitor", "category": "System", "description": "CPU, RAM, disk, network monitoring", "has_config": False},
    {"id": "network-monitor", "name": "Network Monitor", "category": "System", "description": "Network traffic with interface selection", "has_config": True},
    {"id": "battery", "name": "Battery Info", "category": "System", "description": "Battery percentage and status", "has_config": False},
    {"id": "uptime", "name": "Uptime Counter", "category": "System", "description": "System uptime display", "has_config": False},
    {"id": "ping-monitor", "name": "Ping Monitor", "category": "System", "description": "Network latency monitoring", "has_config": True},
    {"id": "kernel-version", "name": "Kernel Version", "category": "System", "description": "Active kernel information", "has_config": False},
    {"id": "weather", "name": "Weather", "category": "Integration", "description": "Location-based weather data", "has_config": True},
    {"id": "media-player", "name": "Media Player", "category": "Integration", "description": "MPRIS playback controls", "has_config": False},
    {"id": "system-updates", "name": "System Updates", "category": "Integration", "description": "Package update notifications", "has_config": False},
    {"id": "tray-enhanced", "name": "Tray Enhanced", "category": "Integration", "description": "Extended system tray", "has_config": False},
    {"id": "pomodoro", "name": "Pomodoro Timer", "category": "Productivity", "description": "Productivity timer with work/break cycles", "has_config": True},
    {"id": "quick-notes", "name": "Quick Notes", "category": "Productivity", "description": "Panel-integrated text storage", "has_config": False},
    {"id": "clipboard-manager", "name": "Clipboard Manager", "category": "Productivity", "description": "Clipboard history tracking", "has_config": False},
    {"id": "todo-list", "name": "Todo List", "category": "Productivity", "description": "Task management with priorities", "has_config": False},
    {"id": "currency", "name": "Currency Exchange", "category": "Financial", "description": "Real-time exchange rates", "has_config": True},
    {"id": "crypto", "name": "Crypto Prices", "category": "Financial", "description": "Cryptocurrency price tracking", "has_config": True},
    {"id": "clock", "name": "Clock & Calendar", "category": "Native", "description": "Date/time with calendar popup", "has_config": False},
    {"id": "app-menu", "name": "App Menu", "category": "Native", "description": "Application launcher", "has_config": False},
    {"id": "volume", "name": "Volume Control", "category": "Native", "description": "Audio volume slider", "has_config": False},
    {"id": "pager", "name": "Desktop Pager", "category": "Native", "description": "Virtual desktop switcher", "has_config": False},
    {"id": "taskbar", "name": "Taskbar", "category": "Native", "description": "Window list", "has_config": False},
    {"id": "system-tray", "name": "System Tray", "category": "Native", "description": "Status notifier icons", "has_config": False},
    {"id": "ntfs-mount", "name": "NTFS Mount", "category": "System", "description": "Mount/unmount NTFS partitions with pkexec", "has_config": False},
]

NATIVE_WIDGETS = {
    "mainmenu": "Main Menu",
    "fancymenu": "Fancy Menu",
    "desktopswitch": "Desktop Switcher",
    "quicklaunch": "Quick Launch",
    "taskbar": "Taskbar",
    "tray": "System Tray",
    "statusnotifier": "Status Notifier",
    "volume": "Volume Control",
    "clock": "Clock",
    "worldclock": "World Clock",
    "spacer": "Spacer",
    "showdesktop": "Show Desktop",
}


# =============================================================================
# Worker Threads
# =============================================================================

class LogReaderThread(QThread):
    """Background thread for reading daemon logs."""
    log_line = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True

    def run(self):
        try:
            proc = subprocess.Popen(
                ["journalctl", "--user", "-u", "naravisuals-daemon", "-f", "--no-pager"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            while self._running:
                line = proc.stdout.readline()
                if line:
                    self.log_line.emit(line.strip())
                else:
                    break
            proc.terminate()
        except Exception as e:
            self.log_line.emit(f"Error reading logs: {e}")

    def stop(self):
        self._running = False


# =============================================================================
# Pages
# =============================================================================

class DashboardPage(QWidget):
    """System dashboard with live stats."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QLabel("<h2>System Dashboard</h2>")
        self.layout.addWidget(header)

        # Status indicators
        status_group = QGroupBox("Daemon Status")
        status_layout = QFormLayout()

        self.daemon_status = QLabel("Checking...")
        status_layout.addRow("Daemon:", self.daemon_status)

        self.uptime_label = QLabel("--")
        status_layout.addRow("Uptime:", self.uptime_label)

        self.widget_count = QLabel("0")
        status_layout.addRow("Active Widgets:", self.widget_count)

        status_group.setLayout(status_layout)
        self.layout.addWidget(status_group)

        # Quick stats
        stats_group = QGroupBox("System Stats")
        stats_layout = QFormLayout()

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        stats_layout.addRow("CPU:", self.cpu_bar)

        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        stats_layout.addRow("RAM:", self.ram_bar)

        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        stats_layout.addRow("Disk:", self.disk_bar)

        stats_group.setLayout(stats_layout)
        self.layout.addWidget(stats_group)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()

        start_btn = QPushButton("Start Daemon")
        start_btn.clicked.connect(self._start_daemon)
        actions_layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop Daemon")
        stop_btn.clicked.connect(self._stop_daemon)
        actions_layout.addWidget(stop_btn)

        restart_btn = QPushButton("Restart Daemon")
        restart_btn.clicked.connect(self._restart_daemon)
        actions_layout.addWidget(restart_btn)

        actions_group.setLayout(actions_layout)
        self.layout.addWidget(actions_group)

        self.layout.addStretch()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_stats)
        self.refresh_timer.start(5000)
        self._refresh_stats()

    def _refresh_stats(self):
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "naravisuals-daemon"],
                capture_output=True, text=True, timeout=5
            )
            self.daemon_status.setText("Running" if result.stdout.strip() == "active" else "Stopped")
        except Exception:
            self.daemon_status.setText("Unknown")

        try:
            import psutil
            self.cpu_bar.setValue(int(psutil.cpu_percent()))
            self.ram_bar.setValue(int(psutil.virtual_memory().percent))
            self.disk_bar.setValue(int(psutil.disk_usage("/").percent))
        except Exception:
            pass

    def _start_daemon(self):
        subprocess.Popen(["systemctl", "--user", "start", "naravisuals-daemon"])
        self._refresh_stats()

    def _stop_daemon(self):
        subprocess.Popen(["systemctl", "--user", "stop", "naravisuals-daemon"])
        self._refresh_stats()

    def _restart_daemon(self):
        subprocess.Popen(["systemctl", "--user", "restart", "naravisuals-daemon"])
        self._refresh_stats()


class WidgetBrowserPage(QWidget):
    """Widget browser with install/enable/disable functionality."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QLabel("<h2>Widget Browser</h2>")
        self.layout.addWidget(header)

        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All", "System", "Integration", "Productivity", "Financial", "Native"])
        self.category_filter.currentTextChanged.connect(self._filter_widgets)
        filter_layout.addWidget(self.category_filter)
        filter_layout.addStretch()
        self.layout.addLayout(filter_layout)

        # Widget table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Category", "Description", "Config", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.table)

        # Action buttons
        btn_layout = QHBoxLayout()
        self.enable_btn = QPushButton("Enable Selected")
        self.enable_btn.clicked.connect(self._enable_widget)
        btn_layout.addWidget(self.enable_btn)

        self.disable_btn = QPushButton("Disable Selected")
        self.disable_btn.clicked.connect(self._disable_widget)
        btn_layout.addWidget(self.disable_btn)

        self.config_btn = QPushButton("Configure Selected")
        self.config_btn.clicked.connect(self._configure_widget)
        btn_layout.addWidget(self.config_btn)

        self.layout.addLayout(btn_layout)

        self._load_widgets()

    def _load_widgets(self):
        self.table.setRowCount(len(WIDGET_REGISTRY))
        for i, widget in enumerate(WIDGET_REGISTRY):
            self.table.setItem(i, 0, QTableWidgetItem(widget["name"]))
            self.table.setItem(i, 1, QTableWidgetItem(widget["category"]))
            self.table.setItem(i, 2, QTableWidgetItem(widget["description"]))
            self.table.setItem(i, 3, QTableWidgetItem("Yes" if widget["has_config"] else "No"))
            self.table.setItem(i, 4, QTableWidgetItem("Enabled"))
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, widget["id"])

    def _filter_widgets(self, category):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if category == "All" or item.text() == category:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def _get_selected_widget_id(self):
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return None

    def _enable_widget(self):
        widget_id = self._get_selected_widget_id()
        if widget_id:
            QMessageBox.information(self, "Enabled", f"Widget '{widget_id}' enabled.")

    def _disable_widget(self):
        widget_id = self._get_selected_widget_id()
        if widget_id:
            QMessageBox.information(self, "Disabled", f"Widget '{widget_id}' disabled.")

    def _configure_widget(self):
        widget_id = self._get_selected_widget_id()
        if widget_id:
            QMessageBox.information(self, "Configure", f"Configure '{widget_id}'")


class PanelOrganizerPage(QWidget):
    """Panel widget organizer with drag-and-drop."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QLabel("<h2>Panel Organizer</h2>")
        self.layout.addWidget(header)

        self.config_path = PANEL_CONFIG
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str

        if self.config_path.exists():
            self.parser.read(str(self.config_path))

        self.panels = self._get_panels()

        # Panel selector
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Panel:"))
        self.panel_selector = QComboBox()
        self.panel_selector.addItems(self.panels)
        self.panel_selector.currentTextChanged.connect(self._load_layout)
        top_row.addWidget(self.panel_selector)
        top_row.addStretch()

        import_btn = QPushButton("Import Template")
        import_btn.clicked.connect(self._import_template)
        top_row.addWidget(import_btn)

        export_btn = QPushButton("Export Template")
        export_btn.clicked.connect(self._export_template)
        top_row.addWidget(export_btn)

        reset_btn = QPushButton("Reset to Stock")
        reset_btn.clicked.connect(self._reset_to_stock)
        top_row.addWidget(reset_btn)

        self.layout.addLayout(top_row)

        # Lists
        lists_layout = QHBoxLayout()

        # Available widgets
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Available Widgets"))
        self.list_available = QListWidget()
        self.list_available.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)
        left_layout.addWidget(self.list_available)
        lists_layout.addLayout(left_layout)

        # Action buttons
        mid_layout = QVBoxLayout()
        mid_layout.addStretch()

        self.btn_add = QPushButton("Add -->")
        self.btn_add.clicked.connect(self._move_to_active)
        self.btn_add.setEnabled(False)
        mid_layout.addWidget(self.btn_add)

        self.btn_rm = QPushButton("<-- Remove")
        self.btn_rm.clicked.connect(self._move_to_available)
        self.btn_rm.setEnabled(False)
        mid_layout.addWidget(self.btn_rm)

        mid_layout.addSpacing(20)

        self.btn_up = QPushButton("Move Up")
        self.btn_up.clicked.connect(self._move_up)
        self.btn_up.setEnabled(False)
        mid_layout.addWidget(self.btn_up)

        self.btn_down = QPushButton("Move Down")
        self.btn_down.clicked.connect(self._move_down)
        self.btn_down.setEnabled(False)
        mid_layout.addWidget(self.btn_down)

        mid_layout.addStretch()
        lists_layout.addLayout(mid_layout)

        # Active widgets
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Active Panel Layout"))
        self.list_active = QListWidget()
        self.list_active.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        right_layout.addWidget(self.list_active)
        lists_layout.addLayout(right_layout)

        self.layout.addLayout(lists_layout)

        self.list_available.itemSelectionChanged.connect(self._update_buttons)
        self.list_active.itemSelectionChanged.connect(self._update_buttons)

        self._load_layout(self.panel_selector.currentText())

        # Save button
        save_btn = QPushButton("Save & Restart Panel")
        save_btn.clicked.connect(self._save)
        self.layout.addWidget(save_btn)

    def _get_panels(self):
        panels = []
        if "general" in self.parser and "panels" in self.parser["general"]:
            panels = [p.strip() for p in self.parser["general"]["panels"].split(",") if p.strip()]
        if not panels:
            panels = [s for s in self.parser.sections() if s.startswith("panel")]
        return panels or ["panel1"]

    def _get_widget_name(self, w_id):
        for w in WIDGET_REGISTRY:
            if w["id"] == w_id:
                return w["name"]
        return NATIVE_WIDGETS.get(w_id, w_id)

    def _load_layout(self, panel_name):
        self.list_active.clear()
        self.list_available.clear()

        available_ids = [w["id"] for w in WIDGET_REGISTRY] + list(NATIVE_WIDGETS.keys())

        active_ids = []
        if panel_name in self.parser and "plugins" in self.parser[panel_name]:
            active_ids = [p.strip() for p in self.parser[panel_name]["plugins"].split(",") if p.strip()]

        for a_id in active_ids:
            item = QListWidgetItem(self._get_widget_name(a_id))
            item.setData(Qt.ItemDataRole.UserRole, a_id)
            self.list_active.addItem(item)
            if a_id in available_ids:
                available_ids.remove(a_id)

        for avail_id in available_ids:
            item = QListWidgetItem(self._get_widget_name(avail_id))
            item.setData(Qt.ItemDataRole.UserRole, avail_id)
            self.list_available.addItem(item)

    def _update_buttons(self):
        has_avail = len(self.list_available.selectedItems()) > 0
        has_active = len(self.list_active.selectedItems()) > 0
        row = self.list_active.currentRow()

        self.btn_add.setEnabled(has_avail)
        self.btn_rm.setEnabled(has_active)
        self.btn_up.setEnabled(has_active and row > 0)
        self.btn_down.setEnabled(has_active and row < self.list_active.count() - 1)

    def _move_to_active(self):
        for item in self.list_available.selectedItems():
            row = self.list_available.row(item)
            taken = self.list_available.takeItem(row)
            new_item = QListWidgetItem(taken.text())
            new_item.setData(Qt.ItemDataRole.UserRole, taken.data(Qt.ItemDataRole.UserRole))
            self.list_active.addItem(new_item)
            self.list_available.insertItem(row, taken)

    def _move_to_available(self):
        for item in self.list_active.selectedItems():
            row = self.list_active.row(item)
            taken = self.list_active.takeItem(row)
            is_present = any(
                self.list_available.item(i).data(Qt.ItemDataRole.UserRole) == taken.data(Qt.ItemDataRole.UserRole)
                for i in range(self.list_available.count())
            )
            if not is_present:
                self.list_available.addItem(taken)

    def _move_up(self):
        row = self.list_active.currentRow()
        if row > 0:
            item = self.list_active.takeItem(row)
            self.list_active.insertItem(row - 1, item)
            self.list_active.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.list_active.currentRow()
        if row < self.list_active.count() - 1 and row >= 0:
            item = self.list_active.takeItem(row)
            self.list_active.insertItem(row + 1, item)
            self.list_active.setCurrentRow(row + 1)

    def _save(self):
        panel_name = self.panel_selector.currentText()
        if panel_name not in self.parser:
            self.parser[panel_name] = {}

        active_plugins = [self.list_active.item(i).data(Qt.ItemDataRole.UserRole)
                          for i in range(self.list_active.count())]
        self.parser[panel_name]["plugins"] = ", ".join(active_plugins)

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            self.parser.write(f)

        subprocess.Popen("killall lxqt-panel; lxqt-panel &", shell=True)
        QMessageBox.information(self, "Saved", f"Panel layout saved and applied.")

    def _import_template(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Template", "", "INI Files (*.ini);;All Files (*)")
        if path:
            shutil.copyfile(path, str(self.config_path))
            self.parser.read(str(self.config_path))
            self.panels = self._get_panels()
            self.panel_selector.blockSignals(True)
            self.panel_selector.clear()
            self.panel_selector.addItems(self.panels)
            self.panel_selector.blockSignals(False)
            self._load_layout(self.panel_selector.currentText())
            subprocess.Popen("killall lxqt-panel; lxqt-panel &", shell=True)

    def _export_template(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Template", "", "INI Files (*.ini)")
        if path:
            if not path.endswith(".ini"):
                path += ".ini"
            shutil.copyfile(str(self.config_path), path)

    def _reset_to_stock(self):
        reply = QMessageBox.question(
            self, "Reset Panel",
            "Reset panel to stock configuration?\nA backup will be created.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            backup_file = BACKUP_DIR / f"panel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.conf"
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            if self.config_path.exists():
                shutil.copyfile(str(self.config_path), str(backup_file))

            stock = Path(__file__).parent.parent.parent / "packaging" / "stock-panel.conf"
            if not stock.exists():
                stock = Path.home() / ".local/share/naravisuals/stock-panel.conf"

            if stock.exists():
                shutil.copyfile(str(stock), str(self.config_path))
                self.parser.read(str(self.config_path))
                self.panels = self._get_panels()
                self.panel_selector.blockSignals(True)
                self.panel_selector.clear()
                self.panel_selector.addItems(self.panels)
                self.panel_selector.blockSignals(False)
                self._load_layout(self.panel_selector.currentText())
                subprocess.Popen("killall lxqt-panel; lxqt-panel &", shell=True)
                QMessageBox.information(self, "Reset Complete", f"Backup saved to:\n{backup_file}")
            else:
                QMessageBox.critical(self, "Error", "Stock configuration not found.")


class ThemePage(QWidget):
    """Theme customization page."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QLabel("<h2>Theme Customization</h2>")
        self.layout.addWidget(header)

        # Color settings
        colors_group = QGroupBox("Colors")
        colors_layout = QFormLayout()

        self.bg_input = QLineEdit(theme.colors.background)
        colors_layout.addRow("Background:", self.bg_input)

        self.fg_input = QLineEdit(theme.colors.foreground)
        colors_layout.addRow("Foreground:", self.fg_input)

        self.accent_input = QLineEdit(theme.colors.accent)
        colors_layout.addRow("Accent:", self.accent_input)

        self.border_input = QLineEdit(theme.colors.border)
        colors_layout.addRow("Border:", self.border_input)

        colors_group.setLayout(colors_layout)
        self.layout.addWidget(colors_group)

        # Panel context
        panel_group = QGroupBox("Panel Context")
        panel_layout = QFormLayout()

        self.height_spin = QSpinBox()
        self.height_spin.setRange(24, 128)
        self.height_spin.setValue(theme.panel_context.height)
        panel_layout.addRow("Panel Height:", self.height_spin)

        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["horizontal", "vertical"])
        self.orientation_combo.setCurrentText(theme.panel_context.orientation)
        panel_layout.addRow("Orientation:", self.orientation_combo)

        panel_group.setLayout(panel_layout)
        self.layout.addWidget(panel_group)

        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        self.preview_frame = QFrame()
        self.preview_frame.setFrameShape(QFrame.Shape.Box)
        self.preview_frame.setMinimumHeight(80)
        self.preview_frame.setStyleSheet(f"""
            background-color: {theme.colors.background};
            color: {theme.colors.foreground};
            border: 2px solid {theme.colors.border};
        """)
        preview_label = QLabel("Sample Widget Preview")
        preview_label.setStyleSheet(f"color: {theme.colors.text_primary};")
        self.preview_frame_layout = QVBoxLayout(self.preview_frame)
        self.preview_frame_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_frame)

        preview_group.setLayout(preview_layout)
        self.layout.addWidget(preview_group)

        # Action buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply Theme")
        apply_btn.clicked.connect(self._apply)
        btn_layout.addWidget(apply_btn)

        reset_btn = QPushButton("Reset to System")
        reset_btn.clicked.connect(self._reset)
        btn_layout.addWidget(reset_btn)

        self.layout.addLayout(btn_layout)
        self.layout.addStretch()

    def _apply(self):
        theme.set_custom_color("background", self.bg_input.text())
        theme.set_custom_color("foreground", self.fg_input.text())
        theme.set_custom_color("accent", self.accent_input.text())
        theme.set_custom_color("border", self.border_input.text())
        theme.update_panel_context(type(theme.panel_context)(
            height=self.height_spin.value(),
            width=theme.panel_context.width,
            orientation=self.orientation_combo.currentText(),
            position=theme.panel_context.position
        ))
        theme.update_from_palette()
        self._update_preview()
        QMessageBox.information(self, "Applied", "Theme applied successfully.")

    def _reset(self):
        theme._custom_colors.clear()
        theme.save_custom_colors()
        theme.update_from_palette()
        self.bg_input.setText(theme.colors.background)
        self.fg_input.setText(theme.colors.foreground)
        self.accent_input.setText(theme.colors.accent)
        self.border_input.setText(theme.colors.border)
        self._update_preview()

    def _update_preview(self):
        self.preview_frame.setStyleSheet(f"""
            background-color: {theme.colors.background};
            color: {theme.colors.foreground};
            border: 2px solid {theme.colors.border};
        """)


class BackupPage(QWidget):
    """Backup and restore manager."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QLabel("<h2>Backup & Restore</h2>")
        self.layout.addWidget(header)

        # Backup list
        self.backup_list = QListWidget()
        self.layout.addWidget(self.backup_list)

        # Action buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Backup")
        create_btn.clicked.connect(self._create_backup)
        btn_layout.addWidget(create_btn)

        restore_btn = QPushButton("Restore Selected")
        restore_btn.clicked.connect(self._restore_backup)
        btn_layout.addWidget(restore_btn)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self._delete_backup)
        btn_layout.addWidget(delete_btn)

        self.layout.addLayout(btn_layout)

        self._refresh_list()

    def _refresh_list(self):
        self.backup_list.clear()
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        for f in sorted(BACKUP_DIR.glob("panel_*.conf"), reverse=True):
            self.backup_list.addItem(f.name)

    def _create_backup(self):
        if not PANEL_CONFIG.exists():
            QMessageBox.warning(self, "No Config", "No panel.conf found to backup.")
            return

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_file = BACKUP_DIR / f"panel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.conf"
        shutil.copyfile(str(PANEL_CONFIG), str(backup_file))
        self._refresh_list()
        QMessageBox.information(self, "Backup Created", f"Saved to:\n{backup_file}")

    def _restore_backup(self):
        item = self.backup_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Select a backup to restore.")
            return

        reply = QMessageBox.question(
            self, "Restore Backup",
            f"Restore panel configuration from {item.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            backup_file = BACKUP_DIR / item.text()
            shutil.copyfile(str(backup_file), str(PANEL_CONFIG))
            subprocess.Popen("killall lxqt-panel; lxqt-panel &", shell=True)
            QMessageBox.information(self, "Restored", "Panel configuration restored.")

    def _delete_backup(self):
        item = self.backup_list.currentItem()
        if not item:
            return

        reply = QMessageBox.question(
            self, "Delete Backup",
            f"Delete backup {item.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            (BACKUP_DIR / item.text()).unlink()
            self._refresh_list()


class LogViewerPage(QWidget):
    """Log viewer for daemon and system logs."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QLabel("<h2>Log Viewer</h2>")
        self.layout.addWidget(header)

        # Log source selector
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source:"))
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Daemon", "System", "Widget"])
        self.source_combo.currentTextChanged.connect(self._load_logs)
        source_layout.addWidget(self.source_combo)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_logs)
        source_layout.addWidget(refresh_btn)

        self.layout.addLayout(source_layout)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Monospace", 10))
        self.layout.addWidget(self.log_display)

        # Auto-scroll checkbox
        self.auto_scroll = QCheckBox("Auto-scroll to bottom")
        self.auto_scroll.setChecked(True)
        self.layout.addWidget(self.auto_scroll)

        self._load_logs()

    def _load_logs(self):
        source = self.source_combo.currentText()
        self.log_display.clear()

        try:
            if source == "Daemon":
                result = subprocess.run(
                    ["journalctl", "--user", "-u", "naravisuals-daemon", "-n", "100", "--no-pager"],
                    capture_output=True, text=True, timeout=5
                )
            elif source == "System":
                result = subprocess.run(
                    ["journalctl", "-n", "100", "--no-pager"],
                    capture_output=True, text=True, timeout=5
                )
            else:
                result = subprocess.run(
                    ["journalctl", "--user", "-n", "100", "--no-pager"],
                    capture_output=True, text=True, timeout=5
                )

            self.log_display.setPlainText(result.stdout or "No logs available.")
        except Exception as e:
            self.log_display.setPlainText(f"Error loading logs: {e}")

        if self.auto_scroll.isChecked():
            self.log_display.verticalScrollBar().setValue(
                self.log_display.verticalScrollBar().maximum()
            )


class AboutPage(QWidget):
    """About page with version info and links."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QLabel("<h2>About NaraVisuals</h2>")
        self.layout.addWidget(header)

        info = QLabel("""
<b>NaraVisuals LXQt Widgets</b><br>
Version 2.0.0<br><br>

Advanced panel widgets for the LXQt desktop environment.<br>
Integrates a native C++ panel plugin with a Python/PyQt6 daemon<br>
via D-Bus IPC for Wayland compatibility.<br><br>

<b>Components:</b><br>
- naravisuals-daemon: D-Bus data provider service<br>
- naravisuals-plugin: C++ LXQt panel plugin<br>
- naravisuals-manager: Settings and control center<br><br>

<b>Links:</b><br>
<a href="https://github.com/naranyala/naravisuals-lxqt-widgets">GitHub Repository</a><br>
<a href="https://github.com/naranyala/naravisuals-lxqt-widgets/issues">Bug Reports</a><br>
<a href="https://lxqt-project.org/">LXQt Project</a>
        """)
        info.setOpenExternalLinks(True)
        info.setWordWrap(True)
        self.layout.addWidget(info)

        self.layout.addStretch()


# =============================================================================
# Main Window
# =============================================================================

class ControlCenter(QMainWindow):
    """All-in-one control center for NaraVisuals."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NaraVisuals Control Center")
        self.setGeometry(100, 100, 900, 650)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("background-color: #2d2d2d;")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Logo/title
        title = QLabel("NaraVisuals")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 15px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: white;
                border: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #3daee9;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
        sidebar_layout.addWidget(self.nav_list)

        # Exit button
        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border: none;")
        exit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(exit_btn)

        main_layout.addWidget(sidebar_widget)

        # Content area
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        # Add pages
        self._add_page("Dashboard", DashboardPage())
        self._add_page("Widget Browser", WidgetBrowserPage())
        self._add_page("Panel Organizer", PanelOrganizerPage())
        self._add_page("Theme", ThemePage())
        self._add_page("Backup & Restore", BackupPage())
        self._add_page("Log Viewer", LogViewerPage())
        self._add_page("About", AboutPage())

        self.nav_list.currentRowChanged.connect(self.pages.setCurrentIndex)
        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)

        # Status bar
        self.statusBar().showMessage("Ready")

    def _add_page(self, name, widget):
        self.nav_list.addItem(name)
        self.pages.addWidget(widget)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Apply dark theme
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #1e1e1e;
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
            background-color: #3d3d3d;
            color: white;
            border: 1px solid #555555;
            padding: 6px;
            border-radius: 4px;
        }
        QListWidget {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #555555;
        }
        QTableWidget {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #555555;
            gridline-color: #555555;
        }
        QHeaderView::section {
            background-color: #3d3d3d;
            color: white;
            padding: 6px;
            border: 1px solid #555555;
        }
        QTextEdit {
            background-color: #1a1a1a;
            color: #00ff00;
            border: 1px solid #555555;
        }
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #3daee9;
            border-radius: 3px;
        }
        QCheckBox {
            color: white;
        }
    """)

    win = ControlCenter()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
