from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """Base properties shared by create and update models."""
    title: str = Field(..., description="Short title for the todo item", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Detailed description of the todo item", max_length=2000)
    is_completed: bool = Field(False, description="Whether the todo is completed")


class TodoCreate(TodoBase):
    """Payload model for creating a new todo."""
    pass


class TodoUpdate(BaseModel):
    """Payload model for updating an existing todo."""
    title: Optional[str] = Field(None, description="Short title for the todo item", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Detailed description of the todo item", max_length=2000)
    is_completed: Optional[bool] = Field(None, description="Whether the todo is completed")


class Todo(TodoBase):
    """Represents a Todo item as stored and returned by the API."""
    id: int = Field(..., description="Unique identifier for the todo item")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")


class TodosList(BaseModel):
    """Response model for a list of todos."""
    items: List[Todo] = Field(..., description="List of todo items")
    total: int = Field(..., description="Total number of items")
