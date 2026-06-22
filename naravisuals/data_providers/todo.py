"""TodoList widget for task management."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any

from naravisuals.daemon.dbus_service import WidgetProvider

TODO_PATH = Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))) / "naravisuals" / "todos.json"


class TodoListProvider(WidgetProvider):
    PROVIDER_ID = "todo-list"

    def __init__(self):
        super().__init__()
        self._todos: list[dict[str, Any]] = []

    def start(self):
        self._load_todos()

    def get_data(self) -> dict[str, Any]:
        pending = [t for t in self._todos if not t.get("done", False)]
        completed = [t for t in self._todos if t.get("done", False)]
        return {
            "todos": self._todos,
            "pending_count": len(pending),
            "completed_count": len(completed),
            "total": len(self._todos),
        }

    def add_todo(self, text: str, priority: str = "medium"):
        """Add a new todo item."""
        self._todos.append({
            "id": len(self._todos) + 1,
            "text": text,
            "priority": priority,  # low, medium, high
            "done": False,
            "created": datetime.now().isoformat(),
            "due_date": None,
        })
        self._save_todos()

    def complete_todo(self, todo_id: int):
        """Mark a todo as completed."""
        for todo in self._todos:
            if todo.get("id") == todo_id:
                todo["done"] = True
                todo["completed_at"] = datetime.now().isoformat()
                break
        self._save_todos()

    def remove_todo(self, todo_id: int):
        """Remove a todo item."""
        self._todos = [t for t in self._todos if t.get("id") != todo_id]
        self._save_todos()

    def update_todo(self, todo_id: int, text: str = None, priority: str = None):
        """Update a todo item."""
        for todo in self._todos:
            if todo.get("id") == todo_id:
                if text is not None:
                    todo["text"] = text
                if priority is not None:
                    todo["priority"] = priority
                break
        self._save_todos()

    def _load_todos(self):
        try:
            if TODO_PATH.exists():
                with open(TODO_PATH) as f:
                    self._todos = json.load(f).get("todos", [])
        except Exception:
            self._todos = []

    def _save_todos(self):
        try:
            TODO_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TODO_PATH, "w") as f:
                json.dump({"todos": self._todos}, f, indent=2)
        except Exception:
            pass
