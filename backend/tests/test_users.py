import pytest
from jose import jwt

from backend.app.config import settings
from backend.app.schemas import user_schemas, auth_schemas


def test_create_user(client):
    res = client.post(
        "/users",
        json={
            "email": "hello123@gmail.com",
            "password": "password123",
            "username": "bebra",
        },
    )

    new_user = user_schemas.UserProfile(**res.json())
    assert new_user.username == "bebra"
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201


def test_login_user(client, test_user):
    res = client.post(
        "/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    token_res = auth_schemas.Token(**res.json())
    payload = jwt.decode(
        token=token_res.access_token,
        algorithms=settings.algorithm,
        key=settings.secret_key,
    )
    print(payload)
    assert payload.get("user_guid")
    assert payload.get("email")
    assert res.status_code == 200
    assert token_res.token_type == "bearer"


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@gmail.com", "111", 403),
        (settings.owner_email, "wrongpassword", 403),
        ("wrongemail@gmail.com", "wrongpassword", 403),
        (None, "111", 422),
        (settings.owner_email, None, 422),
    ],
)
def test_incorrect_login_user(client, test_user, email, password, status_code):
    res = client.post("/login", json={"email": email, "password": password})
    assert res.status_code == status_code


@pytest.mark.parametrize(
    "username, email, password, profile_picture",
    [
        ("updated_username", "updated_email@gmail.com", "updated_pass", "updated_profile_picture"),
        (None, "updated_email@gmail.com", "updated_pass", "updated_profile_picture"),
        (None, None, "updated_pass", "updated_profile_picture"),
        (None, None, None, "updated_profile_picture"),
        (None, None, None, None)
    ]
)
def test_update_user(authorized_client, test_user, username, email, password, profile_picture):
    data = {key: value for key, value in {
        "username": username,
        "email": email,
        "password": password,
        "profile_picture": profile_picture
    }.items() if value is not None}

    res = authorized_client.patch(f"/users/{test_user["guid"]}", json=data)

    assert res.status_code == 200

    assert user_schemas.UserUpdate(**res.json())


def test_update_unexisting_user(authorized_client):
    data = {"email": "email@gmail.com", "password": "password", "username": "username"}
    res = authorized_client.patch(f"/users/77777777-7777-7777-7777-777777777777", json=data)
    assert res.status_code == 404


def test_update_unauthorized_user(client, test_user):
    data = {"email": "email@gmail.com", "password": "password", "username": "username"}
    res = client.patch(f'/users/{test_user["guid"]}', json=data)
    assert res.status_code == 401


def test_update_another_user(authorized_client, test_user, test_user2):
    data = {"email": "email@gmail.com", "password": "password", "username": "username"}
    res = authorized_client.patch(f'/users/{test_user2["guid"]}', json=data)
    assert res.status_code == 403
