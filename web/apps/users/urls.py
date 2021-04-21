# ––– DJANGO IMPORTS
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


# ––– APPLICATION IMPORTS
from apps.users import views


app_name = "apps.users"

urlpatterns = [
    path("", views.IndexView.as_view(), name="users_index"),
]
