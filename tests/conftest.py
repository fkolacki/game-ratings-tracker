from dotenv import load_dotenv
import os

os.environ["ENV_FILE"] = ".env.test"
load_dotenv("../.env.test", override=True)

from fastapi.testclient import TestClient
from main import app
from database import Base, engine
import pytest

@pytest.fixture
def client():
    test_client = TestClient(app)
    return test_client

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def fake_fetch_games():
    test_game = {"id": 1, "name": "test_game",  "genres": [{"name": "Action"}, {"name": "RPG"}], "released": "2024-04-04", "rating": 4.5}
    test_data = {"results": [test_game]}
    return test_data

@pytest.fixture
def mock_rawg_response(monkeypatch):
    monkeypatch.setattr("rawg_client.fetch_games", fake_fetch_games)

def fake_fetch_games_multiple():
    test_games = [{"id": 1, "name": "test_game",  "genres": [{"name": "Action"}, {"name": "RPG"}], "released": "2024-04-04", "rating": 4.5}, 
                  {"id": 2, "name": "test_game2",  "genres": [{"name": "Sports"}, {"name": "Adventure"}], "released": "2025-05-05", "rating": 4.4}]
    test_data = {"results": test_games}
    return test_data

@pytest.fixture
def auth_headers(client):
    client.post("/register/", json={"email": "a@a.com", "password": "password1"})
    user_login = client.post("/login/", data={"username": "a@a.com", "password": "password1"})
    test_token = user_login.json()["access_token"]
    return {"Authorization": f"Bearer {test_token}"}