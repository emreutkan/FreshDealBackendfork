# tests/test_services/test_user_services.py

import pytest
from werkzeug.security import generate_password_hash
from app.models import User, CustomerAddress, UserFavorites
from app.services.user_services import (
    fetch_user_data,
    change_password,
    change_username,
    change_email,
    add_favorite,
    remove_favorite,
    get_favorites,
    authenticate_user,
)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        role="customer",
        email_verified=True,
        password=generate_password_hash("password"),
    )

def test_fetch_user_data(mocker, mock_user):
    mocker.patch("app.models.User.query.filter_by", return_value=mocker.Mock(first=lambda: mock_user))
    mocker.patch("app.models.CustomerAddress.query.filter_by", return_value=mocker.Mock(all=lambda: []))

    user_data, error = fetch_user_data(1)

    assert error is None
    assert user_data["user_data"]["id"] == 1
    assert user_data["user_data"]["email"] == "test@example.com"

def test_change_password_success(mocker, mock_user):
    mocker.patch("app.models.User.query.filter_by", return_value=mocker.Mock(first=lambda: mock_user))
    mocker.patch("app.models.db.session.commit", return_value=None)

    success, message = change_password(1, "password", "new_password")

    assert success
    assert message == "Password updated successfully"

def test_add_favorite(mocker):
    mocker.patch("app.models.UserFavorites.query.filter_by", return_value=mocker.Mock(first=lambda: None))
    mocker.patch("app.models.db.session.add", return_value=None)
    mocker.patch("app.models.db.session.commit", return_value=None)

    success, message = add_favorite(1, 101)

    assert success
    assert message == "Restaurant added to favorites"
