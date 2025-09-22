from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .models import Todo, TodoCreate, TodoUpdate, TodosList
from .repository import InMemoryJSONTodoRepository
from .service import TodoService

# Configure FastAPI application with metadata and tags for OpenAPI
app = FastAPI(
    title="Todo Backend API",
    description="REST API for managing todo items. Supports CRUD operations with a simple file-backed store.",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Health and service information"},
        {"name": "todos", "description": "Operations on todo items"},
    ],
)

# CORS configuration: allow frontend at localhost:3000 (and 127.0.0.1 variants)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost:3000",
        "https://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize repository and service singletons
data_dir = Path(__file__).resolve().parents[2] / "data"
data_dir.mkdir(parents=True, exist_ok=True)
repo = InMemoryJSONTodoRepository(data_file=data_dir / "todos.json")
service = TodoService(repo=repo)


@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """
    Health check endpoint.
    Returns a simple JSON payload indicating the service is up.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/todos",
    response_model=TodosList,
    tags=["todos"],
    summary="List all todos",
    description="Retrieve all todo items.",
)
def list_todos():
    """
    Get all todo items.

    Returns:
        TodosList: JSON object containing items and total count.
    """
    items: List[Todo] = service.list_todos()
    return TodosList(items=items, total=len(items))


# PUBLIC_INTERFACE
@app.get(
    "/todos/{todo_id}",
    response_model=Todo,
    tags=["todos"],
    summary="Get a todo by ID",
    description="Retrieve a single todo item by its identifier.",
)
def get_todo(todo_id: int):
    """
    Get a single todo item.

    Parameters:
        todo_id (int): The ID of the todo item.

    Returns:
        Todo: The requested todo item.

    Raises:
        404: If the todo is not found.
    """
    todo = service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


# PUBLIC_INTERFACE
@app.post(
    "/todos",
    response_model=Todo,
    status_code=status.HTTP_201_CREATED,
    tags=["todos"],
    summary="Create a new todo",
    description="Create a new todo item with title, optional description, and is_completed flag.",
)
def create_todo(payload: TodoCreate):
    """
    Create a new todo.

    Parameters:
        payload (TodoCreate): The todo creation payload.

    Returns:
        Todo: The created todo item.

    Raises:
        400: If validation fails.
    """
    try:
        return service.create_todo(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# PUBLIC_INTERFACE
@app.put(
    "/todos/{todo_id}",
    response_model=Todo,
    tags=["todos"],
    summary="Update an existing todo",
    description="Update fields of an existing todo item by ID.",
)
def update_todo(todo_id: int, payload: TodoUpdate):
    """
    Update an existing todo item.

    Parameters:
        todo_id (int): The ID of the todo to update.
        payload (TodoUpdate): Fields to update.

    Returns:
        Todo: The updated todo.

    Raises:
        404: If the todo does not exist.
        400: If validation fails.
    """
    try:
        updated = service.update_todo(todo_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return updated


# PUBLIC_INTERFACE
@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["todos"],
    summary="Delete a todo",
    description="Delete a todo item by ID. Returns no content on success.",
)
def delete_todo(todo_id: int):
    """
    Delete a todo item.

    Parameters:
        todo_id (int): The ID of the todo to delete.

    Returns:
        204 No Content on success.

    Raises:
        404: If the todo is not found.
    """
    deleted = service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return None
