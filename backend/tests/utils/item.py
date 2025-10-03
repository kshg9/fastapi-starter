from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.models import Todo, TodoCreate, User
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_todo(db: Session) -> Todo:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    todo_in = TodoCreate(title=title, description=description)
    return crud.create_todo(session=db, todo_in=todo_in, owner_id=owner_id)


def create_random_todo_for_superuser(db: Session) -> Todo:
    # Get the superuser
    superuser = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    assert superuser is not None
    title = random_lower_string()
    description = random_lower_string()
    todo_in = TodoCreate(title=title, description=description)
    return crud.create_todo(session=db, todo_in=todo_in, owner_id=superuser.id)


# Keep the old function name for backward compatibility
def create_random_item(db: Session) -> Todo:
    return create_random_todo(db)
