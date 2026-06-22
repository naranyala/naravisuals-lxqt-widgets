from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QHBoxLayout, QPushButton, QLabel

from naravisuals.core.base_widget import PanelWidget


class ClipboardManager(PanelWidget):
    WIDGET_NAME = "Clipboard Manager"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(500)
        self._history = []
        self._max_items = 50
        self._last_text = ""

        self._list = QListWidget()
        self._list.itemClicked.connect(self._copy_item)
        self._layout.addWidget(QLabel("Clipboard History"))
        self._layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_history)
        btn_row.addStretch()
        btn_row.addWidget(clear_btn)
        self._layout.addLayout(btn_row)

        self._clip = QApplication.clipboard()

    def _on_tick(self):
        try:
            text = self._clip.text()
            if text and text != self._last_text:
                self._last_text = text
                if not self._history or self._history[0] != text:
                    self._history.insert(0, text)
                    if len(self._history) > self._max_items:
                        self._history.pop()
                    self._refresh_list()
        except Exception:
            pass

    def _refresh_list(self):
        self._list.clear()
        for item in self._history[:20]:
            display = item[:80].replace('\n', ' ')
            li = QListWidgetItem(display)
            li.setToolTip(item)
            self._list.addItem(li)

    def _copy_item(self, item):
        self._clip.setText(item.toolTip())

    def _clear_history(self):
        self._history.clear()
        self._list.clear()


if __name__ == "__main__":
    ClipboardManager.launch_standalone()
