"""Productivity data providers: pomodoro, quick notes, clipboard."""
import json
import os
import time
from pathlib import Path
from typing import Any

from naravisuals.daemon.dbus_service import WidgetProvider

NOTES_PATH = Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))) / "naravisuals" / "notes.json"


class PomodoroProvider(WidgetProvider):
    PROVIDER_ID = "pomodoro"

    def __init__(self):
        super().__init__()
        self._state = "idle"  # idle, running, paused
        self._is_work = True
        self._work_min = 25
        self._break_min = 5
        self._seconds_left = 25 * 60
        self._pomodoro_count = 0
        self._last_tick = 0.0

    def start(self):
        self._last_tick = time.time()

    def get_data(self) -> dict[str, Any]:
        if self._state == "running":
            now = time.time()
            elapsed = int(now - self._last_tick)
            self._last_tick = now
            self._seconds_left = max(0, self._seconds_left - elapsed)
            if self._seconds_left <= 0:
                self._switch_phase()

        mins, secs = divmod(self._seconds_left, 60)
        return {
            "state": self._state,
            "is_work": self._is_work,
            "time_left": f"{mins:02d}:{secs:02d}",
            "seconds_left": self._seconds_left,
            "pomodoro_count": self._pomodoro_count,
            "work_min": self._work_min,
            "break_min": self._break_min,
        }

    def start_timer(self):
        if self._state == "idle":
            self._seconds_left = self._work_min * 60
        self._state = "running"
        self._last_tick = time.time()

    def pause_timer(self):
        if self._state == "running":
            self._state = "paused"

    def resume_timer(self):
        if self._state == "paused":
            self._state = "running"
            self._last_tick = time.time()

    def reset_timer(self):
        self._state = "idle"
        self._is_work = True
        self._seconds_left = self._work_min * 60

    def set_work_min(self, minutes: int):
        self._work_min = max(1, minutes)
        if self._state == "idle":
            self._seconds_left = self._work_min * 60

    def set_break_min(self, minutes: int):
        self._break_min = max(1, minutes)

    def _switch_phase(self):
        self._is_work = not self._is_work
        if self._is_work:
            self._seconds_left = self._work_min * 60
        else:
            self._seconds_left = self._break_min * 60
            self._pomodoro_count += 1


class QuickNotesProvider(WidgetProvider):
    PROVIDER_ID = "quick-notes"

    def __init__(self):
        super().__init__()
        self._notes: list[dict[str, str]] = []

    def start(self):
        self._load_notes()

    def get_data(self) -> dict[str, Any]:
        return {"notes": self._notes, "count": len(self._notes)}

    def add_note(self, text: str):
        import datetime

        self._notes.append({
            "text": text,
            "created": datetime.datetime.now().isoformat(),
        })
        self._save_notes()

    def remove_note(self, index: int):
        if 0 <= index < len(self._notes):
            self._notes.pop(index)
            self._save_notes()

    def update_note(self, index: int, text: str):
        if 0 <= index < len(self._notes):
            self._notes[index]["text"] = text
            self._save_notes()

    def _load_notes(self):
        try:
            if NOTES_PATH.exists():
                with open(NOTES_PATH) as f:
                    self._notes = json.load(f).get("notes", [])
        except Exception:
            self._notes = []

    def _save_notes(self):
        try:
            NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(NOTES_PATH, "w") as f:
                json.dump({"notes": self._notes}, f, indent=2)
        except Exception:
            pass


class ClipboardProvider(WidgetProvider):
    PROVIDER_ID = "clipboard-manager"

    def __init__(self):
        super().__init__()
        self._history: list[str] = []
        self._max_history = 50

    def get_data(self) -> dict[str, Any]:
        return {"history": self._history, "count": len(self._history)}

    def clear(self):
        self._history.clear()
