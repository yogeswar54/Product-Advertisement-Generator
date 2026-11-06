from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    database_path = tmp_path / "api-tests.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    def override_db():
        with Session(engine) as db:
            yield db

    monkeypatch.setattr("app.services.export_service.EXPORT_ROOT", tmp_path / "exports")
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()
