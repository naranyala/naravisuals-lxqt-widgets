import unittest
import sys
import os

# Use offscreen platform for headless testing to avoid requiring a display
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
import naravisuals.widgets as w

WIDGET_CLASSES = [
    w.SystemMonitor,
    w.WeatherWidget,
    w.QuickNotes,
    w.ClipboardManager,
    w.PomodoroTimer,
    w.NetworkMonitor,
    w.TrayEnhanced,
    w.MediaPlayerController,
    w.BatteryInfo,
    w.AudioVisualizer,
    w.ContainerRadar,
    w.GPUMatrix,
    w.BluetoothRadar,
    w.SystemLogTicker,
    w.SmartHomeToggle,
    w.APMCounter
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

if __name__ == '__main__':
    unittest.main()
