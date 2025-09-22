from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import TypeAdapter

from .models import Todo, TodoCreate, TodoUpdate


class ITodoRepository:
    """Simple interface for a Todo repository for easy future DB swap."""

    # PUBLIC_INTERFACE
    def list_todos(self) -> List[Todo]:
        """Return all todos."""
        raise NotImplementedError

    # PUBLIC_INTERFACE
    def get_todo(self, todo_id: int) -> Optional[Todo]:
        """Return a single todo by ID, or None if not found."""
        raise NotImplementedError

    # PUBLIC_INTERFACE
    def create_todo(self, payload: TodoCreate) -> Todo:
        """Create a new todo and return it."""
        raise NotImplementedError

    # PUBLIC_INTERFACE
    def update_todo(self, todo_id: int, payload: TodoUpdate) -> Optional[Todo]:
        """Update an existing todo and return it, or None if not found."""
        raise NotImplementedError

    # PUBLIC_INTERFACE
    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo by ID. Return True if deleted, False if not found."""
        raise NotImplementedError


class InMemoryJSONTodoRepository(ITodoRepository):
    """Thread-safe in-memory repository with JSON file persistence."""

    def __init__(self, data_file: Path):
        self._lock = threading.RLock()
        self._data_file = data_file
        self._todos: Dict[int, Todo] = {}
        self._next_id: int = 1
        self._adapter = TypeAdapter(List[Todo])  # for serialization of list[Todo]
        self._load()

    def _load(self) -> None:
        """Load todos from a JSON file into memory."""
        with self._lock:
            try:
                if self._data_file.exists():
                    raw = json.loads(self._data_file.read_text(encoding="utf-8"))
                    items = self._adapter.validate_python(raw)
                    self._todos = {item.id: item for item in items}
                    self._next_id = (max(self._todos.keys()) + 1) if self._todos else 1
                else:
                    self._data_file.parent.mkdir(parents=True, exist_ok=True)
                    self._data_file.write_text("[]", encoding="utf-8")
            except Exception:
                # On any error, start with a clean slate but keep the file intact
                self._todos = {}
                self._next_id = 1

    def _persist(self) -> None:
        """Persist current in-memory data to disk."""
        with self._lock:
            items = list(self._todos.values())
            data = self._adapter.dump_python(items, by_alias=False)
            self._data_file.write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")

    def list_todos(self) -> List[Todo]:
        with self._lock:
            return list(sorted(self._todos.values(), key=lambda t: t.id))

    def get_todo(self, todo_id: int) -> Optional[Todo]:
        with self._lock:
            return self._todos.get(todo_id)

    def create_todo(self, payload: TodoCreate) -> Todo:
        with self._lock:
            now = datetime.now(timezone.utc)
            todo = Todo(
                id=self._next_id,
                title=payload.title,
                description=payload.description,
                is_completed=payload.is_completed,
                created_at=now,
                updated_at=now,
            )
            self._todos[self._next_id] = todo
            self._next_id += 1
            self._persist()
            return todo

    def update_todo(self, todo_id: int, payload: TodoUpdate) -> Optional[Todo]:
        with self._lock:
            existing = self._todos.get(todo_id)
            if not existing:
                return None
            updated = existing.model_copy(update={
                "title": payload.title if payload.title is not None else existing.title,
                "description": payload.description if payload.description is not None else existing.description,
                "is_completed": payload.is_completed if payload.is_completed is not None else existing.is_completed,
                "updated_at": datetime.now(timezone.utc),
            })
            self._todos[todo_id] = updated
            self._persist()
            return updated

    def delete_todo(self, todo_id: int) -> bool:
        with self._lock:
            if todo_id in self._todos:
                del self._todos[todo_id]
                self._persist()
                return True
            return False
