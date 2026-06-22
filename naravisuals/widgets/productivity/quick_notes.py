import json
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QSplitter, QWidget

from naravisuals.core.base_widget import PanelWidget


NOTES_PATH = os.path.expanduser("~/.config/naravisuals/notes.json")


class QuickNotes(PanelWidget):
    WIDGET_NAME = "Quick Notes"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_update_interval(0)
        self._notes = self._load_notes()
        self._current_title = ""

        splitter = QSplitter(Qt.Orientation.Vertical)

        top = QVBoxLayout()
        self._list = QListWidget()
        self._list.itemClicked.connect(self._on_select)
        top.addWidget(QLabel("Notes"))
        top.addWidget(self._list)

        top_w = QWidget()
        top_w.setLayout(top)
        splitter.addWidget(top_w)

        bottom = QVBoxLayout()
        self._editor = QTextEdit()
        self._editor.setPlaceholderText("Write your note here...")
        btn_row = QHBoxLayout()
        self._add_btn = QPushButton("+ New")
        self._add_btn.clicked.connect(self._add_note)
        self._save_btn = QPushButton("Save")
        self._save_btn.clicked.connect(self._save_note)
        self._del_btn = QPushButton("Delete")
        self._del_btn.clicked.connect(self._delete_note)
        btn_row.addWidget(self._add_btn)
        btn_row.addWidget(self._save_btn)
        btn_row.addWidget(self._del_btn)
        btn_row.addStretch()
        bottom.addWidget(self._editor)
        bottom.addLayout(btn_row)

        bottom_w = QWidget()
        bottom_w.setLayout(bottom)
        splitter.addWidget(bottom_w)

        self._layout.addWidget(splitter)
        self._refresh_list()

    def _load_notes(self):
        try:
            os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
            with open(NOTES_PATH) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_notes_to_disk(self):
        os.makedirs(os.path.dirname(NOTES_PATH), exist_ok=True)
        with open(NOTES_PATH, "w") as f:
            json.dump(self._notes, f, indent=2)

    def _refresh_list(self):
        self._list.clear()
        for title in self._notes:
            self._list.addItem(title)

    def _on_select(self, item):
        title = item.text()
        self._current_title = title
        self._editor.setPlainText(self._notes.get(title, ""))

    def _add_note(self):
        title = f"Note {len(self._notes) + 1}"
        while title in self._notes:
            title += "_"
        self._notes[title] = ""
        self._save_notes_to_disk()
        self._refresh_list()

    def _save_note(self):
        if self._current_title:
            self._notes[self._current_title] = self._editor.toPlainText()
            self._save_notes_to_disk()

    def _delete_note(self):
        if self._current_title:
            self._notes.pop(self._current_title, None)
            self._save_notes_to_disk()
            self._refresh_list()
            self._editor.clear()
            self._current_title = ""


if __name__ == "__main__":
    QuickNotes.launch_standalone()
