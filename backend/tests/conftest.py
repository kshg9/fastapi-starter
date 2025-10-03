import os
import warnings
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Todo, User
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers

# Suppress warnings early - must be after imports to avoid E402
warnings.filterwarnings("ignore", "Please use.*python_multipart.*instead")
warnings.filterwarnings("ignore", "Support for class-based.*config.*is deprecated")
warnings.filterwarnings(
    "ignore", "Accessing the.*model_fields.*attribute.*is deprecated"
)
warnings.filterwarnings(
    "ignore", "The engine provided as bind.*already in a transaction"
)

# Set environment variable to suppress SQLAlchemy warnings
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"


# Suppress specific warnings to keep test output clean
def pytest_configure(_config):
    """Configure pytest to suppress specific warnings."""
    # Suppress non-security related warnings
    warnings.filterwarnings("ignore", "Please use.*python_multipart.*instead")
    warnings.filterwarnings("ignore", "Support for class-based.*config.*is deprecated")
    warnings.filterwarnings(
        "ignore", "Accessing the.*model_fields.*attribute.*is deprecated"
    )
    warnings.filterwarnings(
        "ignore", "The engine provided as bind.*already in a transaction"
    )
    # Keep security warnings about 'changethis' values visible


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine, autocommit=False, autoflush=False) as session:
        init_db(session)
        yield session
        # Cleanup after tests
        try:
            statement = delete(Todo)
            session.execute(statement)
            statement = delete(User)
            session.execute(statement)
            session.commit()
        except Exception:
            session.rollback()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
