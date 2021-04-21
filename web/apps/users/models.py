# ––– DJANGO IMPORTS
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal
from django.utils.functional import cached_property
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _


# ––– PYTHON UTILITY IMPORTS
import datetime as dt
import pytz


# –––THIRD-PARTY IMPORTS


# ––– APPLICATION IMPORTS
from apps.common import models as common_models


# ––– PARAMETERS

EASTERN_TZ = pytz.timezone("US/Eastern")
UTC_TZ = pytz.timezone("UTC")

DEFAULT_DATETIME = dt.datetime(2010, 1, 1, 0, 0)
DEFAULT_DATETIME_TZ = UTC_TZ.localize(DEFAULT_DATETIME)
DEFAULT_DATE = DEFAULT_DATETIME.date()

# ––– MODELS

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# LOCATIONS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Building(common_models.SortableBaseModel):

    DEFAULT_DELIVERY_WINDOW_BUFFER = 5  # minutes
    DEFAULT_DELIVERY_WINDOW_SIZE = 15  # minutes
    DEFAULT_DELIVERY_WINDOW_CAPACITY = 10  # arbitrary choice

    name = models.CharField(max_length=48, null=False, blank=False)
    name_full = models.CharField(max_length=48, null=True, blank=True)
    address = models.TextField(blank=True, default="")

    delivery_window_buffer = models.PositiveSmallIntegerField(
        default=DEFAULT_DELIVERY_WINDOW_BUFFER, null=False, blank=True
    )
    delivery_window_size = models.PositiveSmallIntegerField(
        default=DEFAULT_DELIVERY_WINDOW_SIZE, null=False, blank=True
    )
    delivery_capacity = models.PositiveSmallIntegerField(
        default=DEFAULT_DELIVERY_WINDOW_CAPACITY, null=False, blank=True
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = [
            "name",
        ]


class Floor(common_models.SortableBaseModel):
    floor = models.CharField(max_length=10, default="1", null=False, blank=False)
    name = models.CharField(max_length=48, blank=True, default="")

    flag_common_area = models.BooleanField(
        default=False
    )  # if true then will be offered as location in all picklists

    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="floors", null=True, blank=True
    )

    def __str__(self):
        if self.name == "":
            return "{0}".format(
                str(self.floor),
            )
        else:
            return "{0}".format(
                str(self.name),
            )

    class Meta:
        ordering = [
            "building__name",
            "floor",
        ]


class Room(common_models.SortableBaseModel):
    name = models.CharField(max_length=48, null=True, blank=True, default="")
    number = models.CharField(max_length=12, null=True, blank=True, default="")
    room_type = models.CharField(max_length=28, null=True, blank=True, default="")
    room_style = models.CharField(max_length=28, null=True, blank=True, default="")
    capacity_seats = models.PositiveSmallIntegerField(null=True, blank=True)
    capacity_max = models.PositiveSmallIntegerField(null=True, blank=True)
    flag_catering_allowed = models.BooleanField(default=True)

    floor = models.ForeignKey(
        Floor, on_delete=models.CASCADE, related_name="rooms", null=True, blank=True
    )

    def __str__(self):
        if self.name == "":
            return "{0}".format(
                str(self.floor),
            )
        else:
            return "{0}".format(
                str(self.name),
            )

    class Meta:
        ordering = [
            "floor__building__name",
            "floor",
            "name",
        ]


class Elevator(common_models.SortableBaseModel):
    name = models.CharField(max_length=48, null=False, blank=False)
    floors = models.CharField(max_length=48, null=False, blank=False)

    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="elevators",
        null=True,
        blank=True,
    )

    def __str__(self):
        return "{0} - {1}".format(
            str(self.building.name),
            str(self.name),
        )

    class Meta:
        ordering = [
            "sort_order",
            "name",
        ]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TENANTS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Tenant(common_models.SortableBaseModel):
    name = models.CharField("Name", max_length=64, null=False)
    formal_name = models.CharField("Formal Name", max_length=64, blank=True, default="")
    flag_building_management = models.BooleanField(default=False)

    buildings = models.ManyToManyField(Building, related_name="tenants", blank=True)
    building_default = models.ForeignKey(
        Building, on_delete=models.SET_NULL, related_name="+", null=True
    )
    contact_telephone_reception = models.CharField(
        max_length=32, blank=True, default=""
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["name"]


class TenantGroup(common_models.SortableBaseModel):
    name = models.CharField("Name", max_length=48, null=False)

    tenants = models.ManyToManyField(Tenant, related_name="groups", blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["sort_order"]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# USERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UserGroup(common_models.AbstractBaseModel):
    name = models.CharField(max_length=36, null=True, blank=True)
    template_string = models.CharField(max_length=24, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class InterfaceGroup(common_models.AbstractBaseModel):
    name = models.CharField(max_length=36, null=True, blank=True)
    template_string = models.CharField(max_length=24, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        # Creates and saves a User with the given email and password.
        if not email:
            raise ValueError("You must provide an email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(PermissionsMixin, AbstractBaseUser, common_models.AbstractBaseModel):
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField("Email address", null=False, blank=False, unique=True)
    is_active = models.BooleanField("Active", default=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_validated = models.BooleanField(
        _("validated"),
        default=True,
        help_text=_("Designates whether this user's email has been validated."),
    )
    last_login = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )

    first_name = models.CharField(max_length=40, null=True, blank=True)
    last_name = models.CharField(max_length=80, null=True, blank=True)

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="tenant_users",
        null=True,
        blank=True,
    )

    objects = CustomUserManager()

    class Meta:
        ordering = [
            "last_name",
            "first_name",
        ]

    def __str__(self):
        return f"{self.email}"

    @cached_property
    def get_email(self):
        return self.email

    @cached_property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse(
            "portal:management_tenantuser_detail", kwargs={"pk": str(self.id)}
        )

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
        return

    @cached_property
    def interface(self):
        if self.profile:
            return str(self.profile.interface_group.template_string)
        else:
            return "DEFAULT"

    @cached_property
    def role(self):
        if self.profile:
            return str(self.profile.user_type)
        else:
            return "Tenant User"


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Settings(common_models.AbstractBaseModel):

    USER_TYPE_CHOICES = (
        (
            "Tenant User",
            "Tenant User",
        ),  # Ordinary Users – order and view/modify own orders
        (
            "Tenant Manager",
            "Tenant Manager",
        ),  # Tenant Manager – admin own users/setting, view/modify tenant orders
        (
            "Tenant Viewer",
            "Tenant Viewer",
        ),  # Tenant reception/security – view today/tomorrow tenant orders
        (
            "Building Viewer",
            "Building Viewer",
        ),  # Building reception/security – view today/tomorrow building orders
        ("GP Manager", "GP Manager"),  # All access
    )

    user_type = models.CharField(
        max_length=24,
        choices=USER_TYPE_CHOICES,
        default="Tenant User",
        null=False,
        blank=False,
    )

    avatar = models.ImageField(
        upload_to="avatars",
        default="../static/img/avatars/default-user-avatar.png",
        null=True,
        blank=True,
    )

    unit = models.CharField(max_length=30, blank=True, default="")
    contact_telephone_office = models.CharField(max_length=32, blank=True, default="")
    contact_telephone_mobile = models.CharField(max_length=32, blank=True, default="")

    date_created = models.DateTimeField("Created", auto_now_add=True)
    date_last_updated = models.DateTimeField("Updated", auto_now=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # DEFAULTS
    building_default = models.ForeignKey(
        Building, on_delete=models.SET_NULL, related_name="+", null=True, blank=True
    )
    flag_use_default_location = models.BooleanField(default=False)
    floor_default = models.CharField(max_length=30, null=True, blank=True)
    room_default = models.CharField(max_length=30, null=True, blank=True)

    # PREFERENCES
    flag_email_on_order_creation = models.BooleanField(default=False)
    flag_email_on_order_cancellation = models.BooleanField(default=False)
    flag_email_on_order_updates = models.BooleanField(default=False)
    flag_email_on_service_notices = models.BooleanField(default=False)

    # ONBOARDING AND HELP MODALS/POPOVERS
    flag_waiting_validation = models.BooleanField(default=False)
    flag_helpful_popovers = models.BooleanField(default=True)
    flag_skipped_tour1 = models.BooleanField(default=False)
    flag_skipped_tour2 = models.BooleanField(default=False)

    date_last_offered_tour = models.DateTimeField(
        "Last Offered Tour",
        auto_now=False,
        auto_now_add=False,
        default=DEFAULT_DATETIME_TZ,
    )
    highest_tour_step_completed = models.PositiveSmallIntegerField(default=0)

    # GROUPS
    group_permissions = models.ManyToManyField(
        UserGroup, related_name="users", null=True, blank=True
    )
    interface_group = models.ForeignKey(
        InterfaceGroup,
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    # FOR GP MANAGERS
    tenants_managed = models.ManyToManyField(
        Tenant, related_name="gp_staff", blank=True
    )
    tenant_groups_managed = models.ManyToManyField(
        TenantGroup, related_name="gp_staff", blank=True
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return f"{self.user} | settings"
