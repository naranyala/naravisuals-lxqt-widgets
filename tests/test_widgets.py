import unittest
import sys
import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PyQt6.QtWidgets import QApplication

from naravisuals.widgets.system.system_monitor import SystemMonitor
from naravisuals.widgets.integrations.weather import WeatherWidget
from naravisuals.widgets.productivity.quick_notes import QuickNotes
from naravisuals.widgets.productivity.clipboard_manager import ClipboardManager
from naravisuals.widgets.productivity.pomodoro import PomodoroTimer
from naravisuals.widgets.system.network_monitor import NetworkMonitor
from naravisuals.widgets.integrations.tray_enhanced import TrayEnhanced
from naravisuals.widgets.integrations.media_player import MediaPlayerController
from naravisuals.widgets.system.battery import BatteryInfo
from naravisuals.widgets.system.uptime import UptimeWidget
from naravisuals.widgets.system.ping_monitor import PingMonitor
from naravisuals.widgets.integrations.system_updates import SystemUpdates
from naravisuals.widgets.system.kernel_version import KernelVersion
from naravisuals.widgets.native.clock import ClockWidget
from naravisuals.widgets.native.app_menu import AppMenuWidget
from naravisuals.widgets.native.volume import VolumeWidget
from naravisuals.widgets.native.pager import DesktopPagerWidget
from naravisuals.widgets.native.taskbar import TaskbarWidget
from naravisuals.widgets.native.system_tray import SystemTrayWidget

WIDGET_CLASSES = [
    SystemMonitor, WeatherWidget, QuickNotes, ClipboardManager, PomodoroTimer,
    NetworkMonitor, TrayEnhanced, MediaPlayerController, BatteryInfo,
    UptimeWidget, PingMonitor, SystemUpdates, KernelVersion,
    ClockWidget, AppMenuWidget, VolumeWidget, DesktopPagerWidget,
    TaskbarWidget, SystemTrayWidget
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
                    if hasattr(widget, '_on_tick'):
                        widget._on_tick()
                except Exception as e:
                    self.fail(f"{widget_cls.__name__} failed during instantiation or tick: {e}")

    @classmethod
    def tearDownClass(cls):
        from PyQt6.QtCore import QThreadPool
        QThreadPool.globalInstance().waitForDone()

if __name__ == '__main__':
    unittest.main()
