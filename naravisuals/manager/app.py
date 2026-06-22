import sys
import os
import configparser
import subprocess
import importlib
import shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QListWidget, QStackedWidget, QLabel, QLineEdit, 
    QComboBox, QFormLayout, QFrame, QMessageBox, QSpinBox, QFileDialog,
    QListWidgetItem
)
from PyQt6.QtCore import Qt
from naravisuals.core.config_manager import config

WIDGETS = [
    ("system_monitor", "System Monitor", "naravisuals.widgets.system.system_monitor", "SystemMonitor"),
    ("weather", "Weather", "naravisuals.widgets.integrations.weather", "WeatherWidget"),
    ("quick_notes", "Quick Notes", "naravisuals.widgets.productivity.quick_notes", "QuickNotes"),
    ("clipboard_manager", "Clipboard Manager", "naravisuals.widgets.productivity.clipboard_manager", "ClipboardManager"),
    ("pomodoro", "Pomodoro Timer", "naravisuals.widgets.productivity.pomodoro", "PomodoroTimer"),
    ("network_monitor", "Network Monitor", "naravisuals.widgets.system.network_monitor", "NetworkMonitor"),
    ("tray_enhanced", "Tray Enhanced", "naravisuals.widgets.integrations.tray_enhanced", "TrayEnhanced"),
    ("media_player", "Media Player", "naravisuals.widgets.integrations.media_player", "MediaPlayerController"),
    ("battery", "Battery Info", "naravisuals.widgets.system.battery", "BatteryInfo"),
    ("uptime", "Uptime Counter", "naravisuals.widgets.system.uptime", "UptimeWidget"),
    ("ping_monitor", "Ping Monitor", "naravisuals.widgets.system.ping_monitor", "PingMonitor"),
    ("system_updates", "System Updates", "naravisuals.widgets.integrations.system_updates", "SystemUpdates"),
    ("kernel_version", "Kernel Version", "naravisuals.widgets.system.kernel_version", "KernelVersion"),
    # Native Replacements
    ("clock", "Native: Clock & Calendar", "naravisuals.widgets.native.clock", "ClockWidget"),
    ("app_menu", "Native: App Menu", "naravisuals.widgets.native.app_menu", "AppMenuWidget"),
    ("volume", "Native: Volume Control", "naravisuals.widgets.native.volume", "VolumeWidget"),
    ("pager", "Native: Desktop Pager", "naravisuals.widgets.native.pager", "DesktopPagerWidget"),
    ("taskbar", "Native: Taskbar", "naravisuals.widgets.native.taskbar", "TaskbarWidget"),
    ("system_tray", "Native: System Tray", "naravisuals.widgets.native.system_tray", "SystemTrayWidget"),
]

class LXQtPanelConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        header = QLabel("<h2>⚙️ Panel Organizer</h2>")
        self.layout.addWidget(header)
        
        self.config_path = os.path.expanduser("~/.config/lxqt/panel.conf")
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str
        
        if os.path.exists(self.config_path):
            self.parser.read(self.config_path)
            
        self.panels = []
        if "general" in self.parser and "panels" in self.parser["general"]:
            self.panels = [p.strip() for p in self.parser["general"]["panels"].split(",") if p.strip()]
        if not self.panels:
            self.panels = [s for s in self.parser.sections() if s.startswith("panel")]
        if not self.panels:
            self.panels = ["panel1"]
            if "panel1" not in self.parser:
                self.parser["panel1"] = {}
                
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("<b>Target Panel:</b>"))
        self.panel_selector = QComboBox()
        self.panel_selector.addItems(self.panels)
        self.panel_selector.currentTextChanged.connect(self.load_panel_layout)
        top_row.addWidget(self.panel_selector)
        
        top_row.addStretch()
        
        import_btn = QPushButton("📥 Import Template")
        import_btn.clicked.connect(self.import_template)
        top_row.addWidget(import_btn)
        
        export_btn = QPushButton("📤 Export Template")
        export_btn.clicked.connect(self.export_template)
        top_row.addWidget(export_btn)
        
        self.layout.addLayout(top_row)
        
        lists_layout = QHBoxLayout()
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Available Widgets</b>"))
        self.list_available = QListWidget()
        # Restrict left list to not accept drops to keep it an "inventory"
        self.list_available.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)
        left_layout.addWidget(self.list_available)
        lists_layout.addLayout(left_layout)
        
        # Action Buttons
        mid_layout = QVBoxLayout()
        mid_layout.addStretch()
        
        self.btn_add = QPushButton("▶ Add")
        self.btn_add.clicked.connect(self.move_to_active)
        self.btn_add.setEnabled(False)
        mid_layout.addWidget(self.btn_add)
        
        self.btn_rm = QPushButton("◀ Remove")
        self.btn_rm.clicked.connect(self.move_to_available)
        self.btn_rm.setEnabled(False)
        mid_layout.addWidget(self.btn_rm)
        
        mid_layout.addSpacing(20)
        
        self.btn_up = QPushButton("▲ Move Left")
        self.btn_up.clicked.connect(self.move_item_up)
        self.btn_up.setEnabled(False)
        mid_layout.addWidget(self.btn_up)
        
        self.btn_down = QPushButton("▼ Move Right")
        self.btn_down.clicked.connect(self.move_item_down)
        self.btn_down.setEnabled(False)
        mid_layout.addWidget(self.btn_down)
        
        mid_layout.addStretch()
        lists_layout.addLayout(mid_layout)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<b>Active Panel Layout</b>"))
        self.list_active = QListWidget()
        # Internal move prevents messy duplicates during drag and drop
        self.list_active.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        right_layout.addWidget(self.list_active)
        lists_layout.addLayout(right_layout)
        
        self.layout.addLayout(lists_layout)
        
        self.list_available.itemSelectionChanged.connect(self.update_button_states)
        self.list_active.itemSelectionChanged.connect(self.update_button_states)
        
        self.load_panel_layout(self.panel_selector.currentText())
        
        save_btn = QPushButton("💾 Save & Restart Panel")
        save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(save_btn)

    def update_button_states(self):
        has_avail = len(self.list_available.selectedItems()) > 0
        has_active = len(self.list_active.selectedItems()) > 0
        
        row = self.list_active.currentRow()
        can_move_up = has_active and row > 0
        can_move_down = has_active and row >= 0 and row < (self.list_active.count() - 1)
        
        self.btn_add.setEnabled(has_avail)
        self.btn_rm.setEnabled(has_active)
        self.btn_up.setEnabled(can_move_up)
        self.btn_down.setEnabled(can_move_down)

    def get_widget_name(self, w_id):
        for w in WIDGETS:
            if w[0] == w_id:
                return w[1]
        native = {
            "mainmenu": "Main Menu (Native)",
            "desktopswitch": "Desktop Switcher",
            "quicklaunch": "Quick Launch",
            "taskbar": "Taskbar (Native)",
            "tray": "System Tray (Native)",
            "statusnotifier": "Status Notifier",
            "volume": "Volume Control (Native)",
            "clock": "Clock (Native)",
            "spacer": "Spacer"
        }
        return native.get(w_id, w_id)

    def load_panel_layout(self, panel_name):
        self.list_active.clear()
        self.list_available.clear()
        
        available_ids = [w[0] for w in WIDGETS]
        available_ids.extend(["mainmenu", "desktopswitch", "quicklaunch", "taskbar", "tray", "statusnotifier", "volume", "clock", "spacer"])
        
        active_ids = []
        if panel_name in self.parser and "plugins" in self.parser[panel_name]:
            active_ids = [p.strip() for p in self.parser[panel_name]["plugins"].split(",") if p.strip()]
            
        for a_id in active_ids:
            item = QListWidgetItem(self.get_widget_name(a_id))
            item.setData(Qt.ItemDataRole.UserRole, a_id)
            self.list_active.addItem(item)
            if a_id in available_ids:
                available_ids.remove(a_id)
                
        for avail_id in available_ids:
            item = QListWidgetItem(self.get_widget_name(avail_id))
            item.setData(Qt.ItemDataRole.UserRole, avail_id)
            self.list_available.addItem(item)

    def move_to_active(self):
        for item in self.list_available.selectedItems():
            row = self.list_available.row(item)
            # Take and copy so it stays in inventory
            taken = self.list_available.takeItem(row)
            new_item = QListWidgetItem(taken.text())
            new_item.setData(Qt.ItemDataRole.UserRole, taken.data(Qt.ItemDataRole.UserRole))
            self.list_active.addItem(new_item)
            # Optionally add it back to available so they can use multiple instances (like spacers)
            self.list_available.insertItem(row, taken)
            
    def move_to_available(self):
        for item in self.list_active.selectedItems():
            row = self.list_active.row(item)
            taken = self.list_active.takeItem(row)
            # If it's not already in available, add it back
            is_present = False
            for i in range(self.list_available.count()):
                if self.list_available.item(i).data(Qt.ItemDataRole.UserRole) == taken.data(Qt.ItemDataRole.UserRole):
                    is_present = True
                    break
            if not is_present:
                self.list_available.addItem(taken)
            
    def move_item_up(self):
        row = self.list_active.currentRow()
        if row > 0:
            item = self.list_active.takeItem(row)
            self.list_active.insertItem(row - 1, item)
            self.list_active.setCurrentRow(row - 1)
            
    def move_item_down(self):
        row = self.list_active.currentRow()
        if row < self.list_active.count() - 1 and row >= 0:
            item = self.list_active.takeItem(row)
            self.list_active.insertItem(row + 1, item)
            self.list_active.setCurrentRow(row + 1)

    def save_settings(self):
        panel_name = self.panel_selector.currentText()
        if panel_name not in self.parser:
            self.parser[panel_name] = {}
            
        active_plugins = [self.list_active.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.list_active.count())]
        self.parser[panel_name]["plugins"] = ", ".join(active_plugins)
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            self.parser.write(f)
            
        subprocess.Popen("killall lxqt-panel; lxqt-panel &", shell=True)
        QMessageBox.information(self, "Success", f"Layout for {panel_name} saved and applied!")

    def import_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Template", "", "INI Files (*.ini);;All Files (*)")
        if file_path:
            shutil.copyfile(file_path, self.config_path)
            self.parser.read(self.config_path)
            
            self.panels = []
            if "general" in self.parser and "panels" in self.parser["general"]:
                self.panels = [p.strip() for p in self.parser["general"]["panels"].split(",") if p.strip()]
            if not self.panels:
                self.panels = [s for s in self.parser.sections() if s.startswith("panel")]
            if not self.panels:
                self.panels = ["panel1"]
                
            self.panel_selector.blockSignals(True)
            self.panel_selector.clear()
            self.panel_selector.addItems(self.panels)
            self.panel_selector.blockSignals(False)
            
            self.load_panel_layout(self.panel_selector.currentText())
            subprocess.Popen("killall lxqt-panel; lxqt-panel &", shell=True)
            QMessageBox.information(self, "Imported", "Template imported and applied successfully!")

    def export_template(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Template", "", "INI Files (*.ini)")
        if file_path:
            if not file_path.endswith('.ini'):
                file_path += '.ini'
            shutil.copyfile(self.config_path, file_path)
            QMessageBox.information(self, "Exported", f"Template successfully exported to:\n{file_path}")

class WidgetConfigPage(QWidget):
    def __init__(self, w_id, name, mod_path, cls_name, launcher_cb):
        super().__init__()
        self.w_id = w_id
        self.name = name
        self.launcher_cb = launcher_cb
        
        self.layout = QVBoxLayout(self)
        
        header = QLabel(f"<h2>{name} Settings</h2>")
        self.layout.addWidget(header)
        
        launch_btn = QPushButton(f"🚀 Launch {name} (Standalone)")
        launch_btn.clicked.connect(lambda: self.launcher_cb(w_id, mod_path, cls_name, name))
        self.layout.addWidget(launch_btn)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)
        
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        
        self.fields = {}
        self.setup_fields()
        
        self.layout.addStretch()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(save_btn)
        
    def setup_fields(self):
        if self.w_id == "weather":
            loc = QLineEdit(config.get(self.w_id, "location", ""))
            loc.setPlaceholderText("e.g. London, UK or 10001")
            self.form_layout.addRow("Location/ZIP:", loc)
            self.fields["location"] = loc
            
            unit = QComboBox()
            unit.addItems(["Celsius", "Fahrenheit"])
            unit.setCurrentText(config.get(self.w_id, "unit", "Celsius"))
            self.form_layout.addRow("Temperature Unit:", unit)
            self.fields["unit"] = unit
            
        elif self.w_id == "pomodoro":
            work = QSpinBox()
            work.setRange(1, 120)
            work.setValue(config.get(self.w_id, "work_duration", 25))
            work.setSuffix(" min")
            self.form_layout.addRow("Work Duration:", work)
            self.fields["work_duration"] = work
            
            brk = QSpinBox()
            brk.setRange(1, 60)
            brk.setValue(config.get(self.w_id, "break_duration", 5))
            brk.setSuffix(" min")
            self.form_layout.addRow("Break Duration:", brk)
            self.fields["break_duration"] = brk
            
        elif self.w_id == "network_monitor":
            iface = QLineEdit(config.get(self.w_id, "interface", "eth0"))
            iface.setPlaceholderText("e.g. eth0, wlan0")
            self.form_layout.addRow("Network Interface:", iface)
            self.fields["interface"] = iface
        else:
            self.form_layout.addRow(QLabel("<i>No specific settings available for this widget yet.</i>"))
            
    def save_settings(self):
        for key, field in self.fields.items():
            if isinstance(field, QLineEdit):
                config.set(self.w_id, key, field.text())
            elif isinstance(field, QComboBox):
                config.set(self.w_id, key, field.currentText())
            elif isinstance(field, QSpinBox):
                config.set(self.w_id, key, field.value())
        QMessageBox.information(self, "Settings Saved", f"{self.name} settings saved successfully.")

class ManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NaraVisuals Settings Hub")
        self.setGeometry(100, 100, 750, 550)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        self._running_widgets = {}

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        sidebar_layout.addWidget(self.sidebar)
        
        reload_btn = QPushButton("🔄 Reload Panel")
        reload_btn.clicked.connect(lambda: subprocess.Popen("killall lxqt-panel; lxqt-panel &", shell=True))
        sidebar_layout.addWidget(reload_btn)
        
        exit_btn = QPushButton("❌ Exit Hub")
        exit_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(exit_btn)
        
        main_layout.addLayout(sidebar_layout)
        
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)
        
        self.sidebar.addItem("⚙️ Panel Organizer")
        lxqt_page = LXQtPanelConfigPage()
        self.pages.addWidget(lxqt_page)
        
        for w_id, name, mod_path, cls_name in WIDGETS:
            self.sidebar.addItem(name)
            page = WidgetConfigPage(w_id, name, mod_path, cls_name, self._launch)
            self.pages.addWidget(page)
            
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        if self.sidebar.count() > 0:
            self.sidebar.setCurrentRow(0)

    def _launch(self, w_id, mod_path, cls_name, name):
        if w_id in self._running_widgets and self._running_widgets[w_id].isVisible():
            self._running_widgets[w_id].raise_()
            self._running_widgets[w_id].activateWindow()
            return
            
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            w = cls()
            w.setWindowTitle(f"{name} (Standalone)")
            w.resize(300, 150)
            w.show()
            w.start()
            self._running_widgets[w_id] = w
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch {name}:\n{str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ManagerWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
