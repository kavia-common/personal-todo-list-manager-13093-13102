from __future__ import annotations

from typing import List, Optional

from .models import Todo, TodoCreate, TodoUpdate
from .repository import ITodoRepository


class TodoService:
    """Encapsulates business logic for Todo operations."""

    def __init__(self, repo: ITodoRepository):
        self._repo = repo

    # PUBLIC_INTERFACE
    def list_todos(self) -> List[Todo]:
        """Return all todos."""
        return self._repo.list_todos()

    # PUBLIC_INTERFACE
    def get_todo(self, todo_id: int) -> Optional[Todo]:
        """Return a todo by id if present."""
        return self._repo.get_todo(todo_id)

    # PUBLIC_INTERFACE
    def create_todo(self, payload: TodoCreate) -> Todo:
        """Create a new todo after any domain validations."""
        # Example validation hook: ensure title isn't just whitespace
        if not payload.title.strip():
            raise ValueError("Title cannot be empty or whitespace.")
        return self._repo.create_todo(payload)

    # PUBLIC_INTERFACE
    def update_todo(self, todo_id: int, payload: TodoUpdate) -> Optional[Todo]:
        """Update an existing todo if it exists."""
        if payload.title is not None and not payload.title.strip():
            raise ValueError("Title cannot be empty or whitespace.")
        return self._repo.update_todo(todo_id, payload)

    # PUBLIC_INTERFACE
    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo by id if it exists."""
        return self._repo.delete_todo(todo_id)
