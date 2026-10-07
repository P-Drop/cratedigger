from django.urls import path

from . import views

urlpatterns = [path("health/", view=views.health_check, name="healthcheck")]
