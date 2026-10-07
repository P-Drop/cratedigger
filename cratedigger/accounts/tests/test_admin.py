import pytest
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.test import Client
from django.urls import reverse

from cratedigger.accounts.models import User


def test_user_model_registered_as_user_admin() -> None:
    model_admin = admin.site.get_model_admin(User)

    assert isinstance(model_admin, UserAdmin)


@pytest.mark.integration
@pytest.mark.django_db
def test_superuser_able_to_list_user_at_admin_panel(admin_client: Client) -> None:
    url = reverse("admin:accounts_user_changelist")
    response = admin_client.get(url)

    assert response.status_code == 200
