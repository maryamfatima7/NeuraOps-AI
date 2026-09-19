import os

os.environ["DATABASE_URL"] = "sqlite:///./test_neuraops.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.main import app


engine = create_engine("sqlite:///./test_neuraops.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides.clear()
from app.db import session as db_session
app.dependency_overrides[db_session.get_db] = override_get_db

client = TestClient(app)


# Ensure each test starts from a clean database state.
client = TestClient(app)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
