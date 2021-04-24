# ––– DJANGO IMPORTS
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


# ––– APPLICATION IMPORTS
from apps.common.admin import BaseAdminConfig
from apps.users import models


"""
Admin for:

LOCATIONS
Building
Elevator
Floor
Room

TENANTS
Tenant
TenantGroup

USER
InterfaceGroup
UserGroup
User
Settings

SETTINGS
Settings

"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# LOCATIONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Building)
class Building(BaseAdminConfig):
    pass


@admin.register(models.Elevator)
class Elevator(BaseAdminConfig):
    pass


@admin.register(models.Floor)
class Floor(BaseAdminConfig):
    pass


@admin.register(models.Room)
class Room(BaseAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TENANTS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Tenant)
class Tenant(BaseAdminConfig):
    pass


@admin.register(models.TenantGroup)
class TenantGroup(BaseAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# USERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.InterfaceGroup)
class InterfaceGroup(BaseAdminConfig):
    pass


@admin.register(models.UserGroup)
class UserGroup(BaseAdminConfig):
    pass


@admin.register(models.User)
class User(BaseAdminConfig):
    search_fields = (
        "first_name",
        "last_name",
        "email",
    )


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.Settings)
class Settings(BaseAdminConfig):
    pass
