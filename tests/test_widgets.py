import unittest
import sys
import os

# Use offscreen platform for headless testing to avoid requiring a display
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
import naravisuals.widgets as w

WIDGET_CLASSES = [
    w.system.system_monitor.SystemMonitor,
    w.integrations.weather.WeatherWidget,
    w.productivity.quick_notes.QuickNotes,
    w.productivity.clipboard_manager.ClipboardManager,
    w.productivity.pomodoro.PomodoroTimer,
    w.system.network_monitor.NetworkMonitor,
    w.integrations.tray_enhanced.TrayEnhanced,
    w.integrations.media_player.MediaPlayerController,
    w.system.battery.BatteryInfo,
    w.system.uptime.UptimeWidget,
    w.system.ping_monitor.PingMonitor,
    w.integrations.system_updates.SystemUpdates,
    w.system.kernel_version.KernelVersion
]

class TestWidgets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_instantiation_and_tick(self):
        for widget_cls in WIDGET_CLASSES:
            with self.subTest(widget=widget_cls.__name__):
                try:
                    widget = widget_cls()
                    self.assertIsNotNone(widget)
                    
                    # Ensure the primary update loop can run once without crashing
                    if hasattr(widget, '_on_tick'):
                        widget._on_tick()
                except Exception as e:
                    self.fail(f"{widget_cls.__name__} failed during instantiation or tick: {e}")

    @classmethod
    def tearDownClass(cls):
        from PyQt6.QtCore import QThreadPool
        # Wait for all async subprocesses (like checkupdates or ping) to finish 
        # before tearing down the QApplication to prevent C++ wrapper deletion errors.
        QThreadPool.globalInstance().waitForDone()

if __name__ == '__main__':
    unittest.main()
