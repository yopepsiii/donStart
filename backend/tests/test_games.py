import pytest

from backend.app.schemas import game_schemas


# GET ---------------------------------------------------
def test_get_games(client, test_games):
    res = client.get("/games/")

    def validate_game(game):
        return game_schemas.GameOut(**game)

    games = list(map(validate_game, res.json()))

    assert res.status_code == 200
    assert len(games) == len(test_games)


def test_get_game(client, test_games):
    res = client.get(f"/games/{test_games[0].guid}")

    validated_game = game_schemas.GameOut(**res.json())

    assert res.status_code == 200
    assert validated_game.guid == test_games[0].guid


def test_get_unexisting_game(client):
    res = client.get(f"/games/77777777-7777-7777-7777-777777777777")

    assert res.status_code == 404


# CREATE GAME (POST) ---------------------------------------------------
@pytest.mark.parametrize(
    "title, description, img, status_code",
    [
        ("Новая игра", "описание", "картинка игры", 201),
        ("Новая игра", None, "картинка игры", 422),
        (None, "описание", "картинка игры", 422),
        (None, None, "картинка игры", 422),
        ("Новая игра", "описание", None, 422),
        (None, None, None, 422),
    ],
)
def test_create_game(authorized_client,
                     title,
                     description,
                     img,
                     status_code,
                     test_user):
    create_data = {
        "title": title,
        "description": description,
        "img": img
    }

    res = authorized_client.post("/games", json=create_data)

    assert res.status_code == status_code

    if res.status_code != 422:
        new_game = game_schemas.GameOut(**res.json())

        assert new_game.title == title
        assert new_game.description == description
        assert new_game.img == img

        print(test_user)

        assert new_game.creator.guid.__str__() == test_user["guid"]

def create_game_unauthorized(client):
    create_data = {
        "title": "Новая игра",
        "description": "Описание",
        "img": "Изображение"
    }

    res = client.post("/games", json=create_data)

    assert res.status_code == 401


# UPDATE (PATCH) ---------------------------------------------------
def test_update_game(authorized_client, test_games, test_updated_data):
    res = authorized_client.patch(f"/games/{test_games[0].guid}", json=test_updated_data)

    validated_game = game_schemas.GameOut(**res.json())

    assert res.status_code == 200
    assert validated_game.title == test_updated_data["title"]
    assert validated_game.description == test_updated_data["description"]
    assert validated_game.img == test_updated_data["img"]


def test_update_unexisting_game(authorized_client, test_updated_data):
    res = authorized_client.patch(f"/games/77777777-7777-7777-7777-777777777777", json=test_updated_data)

    assert res.status_code == 404


def test_update_game_of_other_user(authorized_admin_client, test_games, test_updated_data):
    res = authorized_admin_client.patch(f"/games/{test_games[0].guid}", json=test_updated_data)

    assert res.status_code == 403


def test_update_game_unauthorized(client, test_games, test_updated_data):
    res = client.patch(f"/games/{test_games[0].guid}", json=test_updated_data)
    print(client.headers)
    assert res.status_code == 401


# DELETE ---------------------------------------------------
def test_delete_game(authorized_client, test_games):
    res = authorized_client.delete(f"/games/{test_games[0].guid}")

    assert res.status_code == 204


def test_delete_game_of_other_user(authorized_admin_client, test_games):
    res = authorized_admin_client.delete(f"/games/{test_games[0].guid}")

    assert res.status_code == 403


def test_delete_unexisting_game(authorized_client):
    res = authorized_client.delete(f"/games/77777777-7777-7777-7777-777777777777")

    assert res.status_code == 404


def test_delete_game_unauthorized(client, test_games):
    res = client.delete(f"/games/{test_games[0].guid}")
    print(client.headers)
    assert res.status_code == 401
