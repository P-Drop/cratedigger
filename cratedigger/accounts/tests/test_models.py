import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher

from cratedigger.accounts.models import User


def test_get_user_model_returns_custom_model() -> None:
    assert get_user_model() is User


@pytest.mark.django_db
def test_create_user_sets_regular_user_flags() -> None:
    user = User.objects.create_user(
        username="test_user",
        password="test_password",
    )

    assert user.username == "test_user"
    assert user.is_superuser is False
    assert user.is_staff is False
    assert user.is_active is True


@pytest.mark.django_db
def test_create_superuser_sets_superuser_flags() -> None:
    superuser = User.objects.create_superuser(
        username="test_superuser",
        password="test_superpassword",
    )

    assert superuser.username == "test_superuser"
    assert superuser.is_superuser is True
    assert superuser.is_staff is True


@pytest.mark.django_db
def test_user_password_saved_as_hash() -> None:
    user = User.objects.create_user(
        username="test_user",
        password="test_password",
    )

    assert identify_hasher(user.password)
    assert user.password != "test_password"


@pytest.mark.django_db
def test_check_password_accepts_correct_and_rejects_wrong() -> None:
    user = User.objects.create_user(
        username="test_user",
        password="test_password",
    )

    assert user.check_password("test_password") is True
    assert user.check_password("wrong_password") is False
