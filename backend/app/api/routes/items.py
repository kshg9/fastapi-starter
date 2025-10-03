import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Todo,
    TodoCreate,
    TodoPriority,
    TodoPublic,
    TodosPublic,
    TodoStatus,
    TodoUpdate,
)

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=TodosPublic)
def read_todos(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    status: TodoStatus | None = Query(default=None),
    priority: TodoPriority | None = Query(default=None),
) -> Any:
    """
    Retrieve todos with optional filtering by status and priority.
    """
    # Build the base query
    base_query = select(Todo).where(Todo.owner_id == current_user.id)
    count_query = (
        select(func.count()).select_from(Todo).where(Todo.owner_id == current_user.id)
    )

    # Apply filters
    if status:
        base_query = base_query.where(Todo.status == status)
        count_query = count_query.where(Todo.status == status)

    if priority:
        base_query = base_query.where(Todo.priority == priority)
        count_query = count_query.where(Todo.priority == priority)

    # Execute queries
    count = session.exec(count_query).one()
    todos = session.exec(base_query.offset(skip).limit(limit)).all()

    return TodosPublic(
        data=[TodoPublic.model_validate(todo) for todo in todos], count=count
    )


@router.get("/{id}", response_model=TodoPublic)
def read_todo(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get todo by ID.
    """
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return todo


@router.post("/", response_model=TodoPublic)
def create_todo(
    *, session: SessionDep, current_user: CurrentUser, todo_in: TodoCreate
) -> Any:
    """
    Create new todo.
    """
    todo = Todo.model_validate(todo_in, update={"owner_id": current_user.id})
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.put("/{id}", response_model=TodoPublic)
def update_todo(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    todo_in: TodoUpdate,
) -> Any:
    """
    Update a todo.
    """
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_dict = todo_in.model_dump(exclude_unset=True)

    # Handle status change to completed
    if todo_in.status == TodoStatus.COMPLETED and todo.status != TodoStatus.COMPLETED:
        update_dict["completed_at"] = datetime.utcnow()
    elif todo_in.status != TodoStatus.COMPLETED and todo.status == TodoStatus.COMPLETED:
        update_dict["completed_at"] = None

    # Update the updated_at timestamp
    update_dict["updated_at"] = datetime.utcnow()

    todo.sqlmodel_update(update_dict)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/{id}")
def delete_todo(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a todo.
    """
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(todo)
    session.commit()
    return Message(message="Todo deleted successfully")


@router.patch("/{id}/toggle-status", response_model=TodoPublic)
def toggle_todo_status(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Toggle todo between completed and pending status.
    """
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if not current_user.is_superuser and (todo.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Toggle status
    if todo.status == TodoStatus.COMPLETED:
        todo.status = TodoStatus.PENDING
        todo.completed_at = None
    else:
        todo.status = TodoStatus.COMPLETED
        todo.completed_at = datetime.utcnow()

    todo.updated_at = datetime.utcnow()
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
