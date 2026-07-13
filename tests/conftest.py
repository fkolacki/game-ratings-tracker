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