# ––– DJANGO IMPORTS
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


# ––– PYTHON UTILITY IMPORTS


# ––– THIRD-PARTY IMPORTS


# ––– APPLICATION IMPORTS
from apps.api import select_views, views


app_name = "apps.api"


""" API endpoints for select2 dropdowns """
select_urls = [
    path(
        "tenants",
        select_views.TenantSelectAPIView.as_view(),
        name="select_tenants",
    ),
    path(
        "tenantgroups",
        select_views.TenantGroupSelectAPIView.as_view(),
        name="select_tenant_groups",
    ),
    path(
        "users",
        select_views.UserSelectAPIView.as_view(),
        name="select_users",
    ),
    path(
        "costtype",
        select_views.CostTypeSelectAPIView.as_view(),
        name="select_costtypes",
    ),
]


urlpatterns = [
    path("select/", include(select_urls)),
]
