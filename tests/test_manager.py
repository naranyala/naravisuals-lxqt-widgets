import unittest
import sys
import os
import tempfile
from unittest.mock import patch

# Force offscreen rendering for headless testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PyQt6.QtWidgets import QApplication

# Ensure QApplication is initialized before importing UI components
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from naravisuals.manager.app import LXQtPanelConfigPage, ManagerWindow

class TestManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file to safely isolate the test environment
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_config = os.path.join(self.temp_dir.name, "panel.conf")
        
        # Seed it with a fake dual-monitor layout
        with open(self.mock_config, 'w') as f:
            f.write("[general]\npanels=panel1,panel2\n\n[panel1]\nplugins=clock,volume\n\n[panel2]\nplugins=taskbar\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch('naravisuals.manager.app.os.path.expanduser')
    @patch('naravisuals.manager.app.subprocess.Popen')
    @patch('naravisuals.manager.app.QMessageBox.information')
    def test_lxqt_panel_organizer(self, mock_msg, mock_popen, mock_expanduser):
        """Tests the Drag-and-Drop Panel Organizer safely."""
        mock_expanduser.return_value = self.mock_config
        
        page = LXQtPanelConfigPage()
        
        # 1. Test multi-panel detection from the mocked INI file
        self.assertIn("panel1", page.panels)
        self.assertIn("panel2", page.panels)
        
        # 2. Test initial list population for panel1
        self.assertEqual(page.list_active.count(), 2) # It should load 'clock' and 'volume'
        
        # 3. Test changing target panels updates the lists
        page.panel_selector.setCurrentText("panel2")
        self.assertEqual(page.list_active.count(), 1) # It should load only 'taskbar'
        
        # 4. Test safe save execution
        page.save_settings()
        mock_popen.assert_called_with("killall lxqt-panel; lxqt-panel &", shell=True)
        mock_msg.assert_called_once()

    def test_manager_window_init(self):
        """Tests the primary Settings Hub application shell."""
        win = ManagerWindow()
        self.assertIsNotNone(win)
        self.assertEqual(win.windowTitle(), "NaraVisuals Settings Hub")
        
        # Verify the sidebar loaded the Panel Organizer plus all 19 widgets
        self.assertGreaterEqual(win.sidebar.count(), 20)
        
        # Verify the QStackedWidget pages exactly match the sidebar count
        self.assertEqual(win.pages.count(), win.sidebar.count())

if __name__ == '__main__':
    unittest.main()
