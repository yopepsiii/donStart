import pytest

from backend.tests.conftest import test_user, test_user2, test_user3


# CREATE ROLE ----------------------------------
@pytest.mark.parametrize(
    "name, user_guid, status_code",
    [
        ("test", None, 201),
        ("test", test_user2.__dict__.get("guid"), 201),
        ("Администратор 💫", None, 201),
        ("Администратор 💫", test_user2.__dict__.get("guid"), 201),
        ("Создатель 🌀", None, 201),
        ("Создатель 🌀", test_user2.__dict__.get("guid"), 201)

    ]
)
def test_create_role_as_owner(authorized_client, name, user_guid, status_code, test_user2, test_user):
    role_data = {
        "name": name,
    }

    if user_guid is not None:
        role_data["user_guid"] = user_guid

    res = authorized_client.post("/roles", json=role_data)
    assert res.status_code == status_code

    res = res.json()
    assert res["name"] == role_data["name"]

    if role_data.get("user_guid") is None:
        assert res["user_guid"] == test_user["guid"]
    else:
        assert res["user_guid"] == test_user2["guid"]


@pytest.mark.parametrize(
    "name, user_guid, status_code",
    [
        ("test", None, 201),
        ("test", test_user3.__dict__.get("guid"), 201),
        ("Администратор 💫", None, 403),
        ("Администратор 💫", test_user3.__dict__.get("guid"), 403),
        ("Создатель 🌀", None, 403),
        ("Создатель 🌀", test_user3.__dict__.get("guid"), 403)

    ]
)
def test_create_role_as_admin(authorized_admin_client, name, user_guid, status_code, test_user2, test_user3):
    role_data = {
        "name": name,
    }

    if user_guid is not None:
        role_data["user_guid"] = user_guid

    res = authorized_admin_client.post("/roles", json=role_data)
    assert res.status_code == status_code

    if res.status_code != 403:
        res = res.json()
        assert res["name"] == role_data["name"]

        if role_data.get("user_guid") is None:
            assert res["user_guid"] == test_user2["guid"]
        else:
            assert res["user_guid"] == test_user3["guid"]


@pytest.mark.parametrize(
    "name, user_guid",
    [
        ("test", None),
        ("test", test_user2.__dict__.get("guid")),
        ("Администратор 💫", None),
        ("Администратор 💫", test_user2.__dict__.get("guid")),
        ("Создатель 🌀", None),
        ("Создатель 🌀", test_user2.__dict__.get("guid"))

    ]
)
def test_create_role_as_common(authorized_common_client, name, user_guid):
    role_data = {
        "name": name,
    }

    if user_guid is not None:
        role_data["user_guid"] = user_guid

    res = authorized_common_client.post("/roles", json=role_data)
    assert res.status_code == 403


@pytest.mark.parametrize(
    "name, user_guid",
    [
        ("test", None),
        ("test", test_user3.__dict__.get("guid"))

    ]
)
def test_create_role_unauthorized(client, name, user_guid):
    role_data = {
        "name": name
    }

    if user_guid is not None:
        role_data["user_guid"] = user_guid

    res = client.post("/roles", json=role_data)
    assert res.status_code == 401
