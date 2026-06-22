import sys
import importlib
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QListWidget, QStackedWidget, QLabel, QLineEdit, 
    QComboBox, QFormLayout, QFrame, QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt
from naravisuals.config import config

WIDGETS = [
    ("system_monitor", "System Monitor", "naravisuals.widgets.system_monitor", "SystemMonitor"),
    ("weather", "Weather", "naravisuals.widgets.weather", "WeatherWidget"),
    ("quick_notes", "Quick Notes", "naravisuals.widgets.quick_notes", "QuickNotes"),
    ("clipboard_manager", "Clipboard Manager", "naravisuals.widgets.clipboard_manager", "ClipboardManager"),
    ("pomodoro", "Pomodoro Timer", "naravisuals.widgets.pomodoro", "PomodoroTimer"),
    ("network_monitor", "Network Monitor", "naravisuals.widgets.network_monitor", "NetworkMonitor"),
    ("tray_enhanced", "Tray Enhanced", "naravisuals.widgets.tray_enhanced", "TrayEnhanced"),
    ("media_player", "Media Player", "naravisuals.widgets.media_player", "MediaPlayerController"),
    ("battery", "Battery Info", "naravisuals.widgets.battery", "BatteryInfo"),
    ("audio_visualizer", "Audio Visualizer", "naravisuals.widgets.audio_visualizer", "AudioVisualizer"),
    ("container_radar", "Container Radar", "naravisuals.widgets.container_radar", "ContainerRadar"),
    ("gpu_matrix", "GPU Matrix", "naravisuals.widgets.gpu_matrix", "GPUMatrix"),
    ("bluetooth_radar", "Bluetooth Radar", "naravisuals.widgets.bluetooth_radar", "BluetoothRadar"),
    ("system_log", "System Log Ticker", "naravisuals.widgets.system_log", "SystemLogTicker"),
    ("smart_home", "Smart Home Toggle", "naravisuals.widgets.smart_home", "SmartHomeToggle"),
    ("apm_counter", "APM Counter", "naravisuals.widgets.apm_counter", "APMCounter"),
]

class WidgetConfigPage(QWidget):
    def __init__(self, w_id, name, mod_path, cls_name, launcher_cb):
        super().__init__()
        self.w_id = w_id
        self.name = name
        self.launcher_cb = launcher_cb
        
        self.layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"<h2>{name} Settings</h2>")
        self.layout.addWidget(header)
        
        # Launch Button
        launch_btn = QPushButton(f"🚀 Launch {name} (Standalone)")
        launch_btn.clicked.connect(lambda: self.launcher_cb(w_id, mod_path, cls_name, name))
        self.layout.addWidget(launch_btn)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)
        
        # Settings Form
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        
        self.fields = {}
        self.setup_fields()
        
        self.layout.addStretch()
        
        # Save Button
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
        self.setGeometry(100, 100, 700, 500)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        self._running_widgets = {}

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        main_layout.addWidget(self.sidebar)
        
        # Stacked Widget Pages
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)
        
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
    
    # Apply modern styling
    app.setStyle("Fusion")
    
    win = ManagerWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
