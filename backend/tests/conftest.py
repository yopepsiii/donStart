from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import models
from backend.app.main import app

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models import Base

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}-test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_credentials = {
        "email": "bebra_test@gmail.com",
        "password": "111",
        "username": "bebra_t",
        "profile_picture": "some picture of user"
    }
    res = client.post("/users", json=user_credentials)

    new_user = res.json()

    new_user["password"] = user_credentials["password"]

    assert res.status_code == 201
    return new_user


@pytest.fixture
def test_user2(client):
    user_credentials = {
        "email": "bebra_test2@gmail.com",
        "password": "111",
        "username": "bebra_t2",
        "profile_picture": "some picture of user2"
    }
    res = client.post("/users", json=user_credentials)

    new_user = res.json()

    new_user["password"] = user_credentials["password"]

    assert res.status_code == 201

    return new_user


@pytest.fixture
def token(client, test_user):
    res = client.post(
        "/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    token = res.json()
    return token


@pytest.fixture
def authorized_client(client, token):  # Мы всегда залогинены от test_user
    new_client = client
    new_client.headers = {
        **new_client.headers,
        "Authorization": f'Bearer {token["access_token"]}',
    }
    return new_client


@pytest.fixture()
def test_games(client, test_user, test_user2, session):
    games_data = [  # Данные для создания игр
        {
            "title": "Тестовая игра",
            "description": "Игра от димы осипенко",
            "img": "some picture",
            "creator_guid": test_user["guid"],
        },
        {
            "title": "Тестовая игра 2",
            "description": "Игра от Николая",
            "img": "some picture 2",
            "creator_guid": test_user["guid"]
        },
        {
            "title": "Тестовая игра 3",
            "description": "Игра от Ильи",
            "img": "some picture 3",
            "creator_guid": test_user2["guid"]
        },
        {
            "title": "Тестовая игра 4",
            "description": "Игра от Поли",
            "img": "some picture 4",
            "creator_guid": test_user2["guid"]
        }

    ]

    def create_game_model(
            game,
    ):  # Словарь с данными для одной записки -> модель записки
        return models.Game(**game)

    game_map = map(
        create_game_model, games_data
    )  # Преобразуем список из словарей данных для сообщений в список моделей
    games = list(game_map)

    session.add_all(games)
    session.commit()

    messages = session.query(models.Game).all()
    return messages


@pytest.fixture
def test_updated_data():
    return {"title": "updated title", "description": "updated content", "img": "updated picture"}
