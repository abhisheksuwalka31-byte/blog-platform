import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User

# In-memory SQLite for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_users(db_session):
    user_a = User(
        username="alice",
        email="alice@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Alice Chen"
    )
    user_b = User(
        username="bob",
        email="bob@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Bob Martinez"
    )
    db_session.add(user_a)
    db_session.add(user_b)
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)
    return {"alice": user_a, "bob": user_b}


@pytest.fixture(scope="function")
def alice_headers(test_users):
    token = create_access_token(subject=test_users["alice"].id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def bob_headers(test_users):
    token = create_access_token(subject=test_users["bob"].id)
    return {"Authorization": f"Bearer {token}"}
