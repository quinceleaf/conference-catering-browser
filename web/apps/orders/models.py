# ––– DJANGO IMPORTS
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.db.models.enums import Choices
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property


# ––– PYTHON UTILITY IMPORTS
import datetime as dt
from decimal import Decimal as D
import pytz
import uuid


# –––THIRD-PARTY IMPORTS
from django_pandas.managers import DataFrameManager


# ––– APPLICATION IMPORTS
from apps.common import models as common_models
from apps.users import models as users_models


# ––– PARAMETERS

EASTERN_TZ = pytz.timezone("US/Eastern")
UTC_TZ = pytz.timezone("UTC")

DEFAULT_DATETIME = dt.datetime(2010, 1, 1, 0, 0)
DEFAULT_DATETIME_TZ = UTC_TZ.localize(DEFAULT_DATETIME)
DEFAULT_DATE = DEFAULT_DATETIME.date()

DEFAULT_START_TIME = dt.time(8, 0)  # offset for UTC comparisons
DEFAULT_END_TIME = dt.time(17, 0)  # offset for UTC comparisons

# ––– MODELS

"""
ENUMS
Calendar
Category
ClosedDay
CostType
Location
PaymentMethod
Tag

MENU
AddOn
AddOnPrice
Course
CourseModificationOption
Menu
MenuItem
Package
PackagePrice

ORDER
BillingRecord
OrderAddOn
OrderBase
OrderCourse
OrderCourseModification
OrderDeliveryWindow
OrderHistory
OrderLogistics
OrderMenuItem
OrderNote
OrderPackage
OrderPayment
OrderRepeat
OrderStatus

SETTINGS
Settings
"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ENUMS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Category(common_models.SortableBaseModel):
    name = models.CharField("Category", max_length=32, null=False)
    note = models.CharField("Note", max_length=128, blank=True, default="")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["sort_order"]


class DateObjectsManager(models.Manager):
    def is_upcoming(self):
        # Return only objects where flag_active is False
        queryset = self.get_queryset().filter(date_closed__gte=dt.date.today())
        return queryset

    def is_past(self):
        # Return only objects where flag_active is False
        queryset = self.get_queryset().filter(date_closed__lt=dt.date.today())
        return queryset


class ClosedDay(common_models.SortableBaseModel):
    reason = models.CharField("Reason", max_length=255, null=False)

    date_closed = models.DateField(
        "Closed",
        auto_now=False,
        auto_now_add=False,
        default=DEFAULT_DATE,
        help_text="Date Closed",
    )

    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )

    objects = DateObjectsManager()

    def __str__(self):
        return str(self.date_closed.strftime("%A, %B %d, %Y"))

    class Meta:
        ordering = ["sort_order"]


class CostType(common_models.SortableBaseModel):
    name = models.CharField("Cost Type", max_length=32, null=False)
    note = models.CharField("Note", max_length=128, blank=True, default="")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Cost Types"
        ordering = ["sort_order"]


class TagDisplayManager(models.Manager):
    def all(self):
        # Squarespace-specific allergen tags
        # Return only tags matching SS-criteria
        queryset = self.get_queryset().all()
        return queryset

    def is_squarespace_allergen(self):
        # Squarespace-specific allergen tags
        # Return only tags matching SS-criteria
        queryset = self.get_queryset().filter(
            Q(name="AV")
            | Q(name="C")
            | Q(name="D")
            | Q(name="E")
            | Q(name="F")
            | Q(name="G")
            | Q(name="M")
            | Q(name="N")
            | Q(name="P")
            | Q(name="S")
            | Q(name="SF")
        )
        return queryset

    def is_squarespace_preference(self):
        # Squarespace-specific preference/credence tags
        # Return only tags matching SS-criteria
        queryset = self.get_queryset().filter(Q(name="O") | Q(name="V") | Q(name="VGT"))
        return queryset

    def is_gp_standard(self):
        # Return only tags matching GP-standard negative-assertion tags (ie, gluten-free, nut-free)
        queryset = self.get_queryset().filter(
            Q(name="Dairy-Free")
            | Q(name="Gluten-Free")
            | Q(name="Nut-Free")
            | Q(name="Vegan")
            | Q(name="Vegetarian")
        )
        return queryset


class Tag(common_models.SortableBaseModel):
    name = models.CharField("Tag", max_length=32, null=False)

    objects = TagDisplayManager()

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["sort_order"]


class Location(common_models.SortableBaseModel):
    name = models.CharField(max_length=48, null=True, blank=True, default="")
    number = models.CharField(max_length=12, null=True, blank=True, default="")
    room_type = models.CharField(max_length=28, null=True, blank=True, default="")
    room_style = models.CharField(max_length=28, null=True, blank=True, default="")
    capacity_seats = models.PositiveSmallIntegerField(null=True, blank=True)
    capacity_max = models.PositiveSmallIntegerField(null=True, blank=True)
    flag_catering_allowed = models.BooleanField(default=True)

    building = models.ForeignKey(
        users_models.Building,
        on_delete=models.CASCADE,
        related_name="locations",
        null=True,
        blank=True,
    )

    tenant = models.ForeignKey(
        users_models.Tenant,
        on_delete=models.CASCADE,
        related_name="locations",
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.name is not None and self.number is not None:
            return str("{0} ({1})".format(self.name, self.number))
        else:
            return str(self.name)

    class Meta:
        ordering = [
            "building__name",
            "sort_order",
            "name",
        ]


class PaymentMethod(common_models.AbstractBaseModel):
    payment = models.CharField(max_length=64, blank=True)
    nickname = models.CharField(max_length=50, blank=True)

    date_created = models.DateTimeField("Created", auto_now_add=True)
    date_last_updated = models.DateTimeField("Updated", auto_now=True)
    flag_active = models.BooleanField(default=True)
    flag_house_account = models.BooleanField(default=False)

    user = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="payment_methods",
        null=True,
        blank=True,
    )
    tenant = models.ForeignKey(
        users_models.Tenant,
        on_delete=models.CASCADE,
        related_name="payment_methods",
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.flag_house_account:
            return "{0}-House Account".format(str(self.tenant.name))
        elif self.nickname is not None and self.payment == self.nickname:
            return str(self.payment)
        elif self.nickname is not None:
            return "{0} ({1})".format(self.nickname, self.payment)
        elif self.payment is not None:
            return str(self.payment)
        else:
            return str(self.id)

    class Meta:
        ordering = [
            "nickname",
            "payment",
        ]


class Calendar(common_models.SortableBaseModel):
    CALENDAR_TYPE_CHOICES = (
        ("Google", "Google"),
        ("Outlook", "Outlook"),
    )

    name = models.CharField(max_length=24, null=False, blank=False)
    description = models.CharField(max_length=255, blank=True, default="")

    calendar_type = models.CharField(
        "Calendar Type",
        max_length=32,
        choices=CALENDAR_TYPE_CHOICES,
        default="Pending",
        null=False,
    )
    calendar_id = models.CharField(max_length=64, blank=True, default="")

    flag_single_tenant_only = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.calendar_type})"

    class Meta:
        ordering = [
            "name",
        ]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MENU OBJECTS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class MenuObjectsManager(models.Manager):
    def is_active(self):
        # Return only objects where flag_active is False
        queryset = self.get_queryset().exclude(flag_active=False)
        return queryset

    def is_draft(self):
        # Return only objects where flag_active is False
        queryset = self.get_queryset().exclude(flag_active=True)
        return queryset


class MenuItem(common_models.SortableBaseModel):
    cxp_id = models.CharField("CXP ID", max_length=12, blank=True)

    name = models.CharField("Name", max_length=128, null=False, blank=False)
    description = models.TextField(
        "Description", max_length=255, blank=True, default=""
    )
    variation = models.CharField("Variation", max_length=60, blank=True, default="")

    price_descriptive = models.CharField(
        "Descriptive Price", max_length=128, blank=True, default=""
    )
    price_numeric_fixed = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, blank=True
    )
    price_numeric_per_person = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, blank=True
    )

    tags = models.ManyToManyField(Tag, related_name="menu_items", blank=True)

    objects = MenuObjectsManager()

    def __str__(self):
        if self.variation:
            return f"{self.name} ({self.variation})"
        else:
            return f"{self.name}"

    class Meta:
        ordering = ["sort_order", "name"]


class Course(common_models.SortableBaseModel):
    cxp_id = models.CharField("CXP ID", max_length=12, blank=True)

    name = models.CharField("Course", max_length=64, null=False, blank=False)
    description = models.CharField(
        "Description", max_length=255, blank=True, default=""
    )
    note = models.CharField("Note", max_length=255, blank=True, default="")
    variation = models.CharField("Variation", max_length=30, blank=True, default="")

    price_descriptive = models.CharField(
        "Descriptive Price", max_length=128, blank=True, default=""
    )
    price_numeric_fixed = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False, blank=True
    )
    price_numeric_per_person = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False, blank=True
    )

    selection_quantity = models.PositiveSmallIntegerField(null=True, default=0)

    tags = models.ManyToManyField(Tag, related_name="courses", blank=True)
    menu_items_select_from = models.ManyToManyField(
        MenuItem, related_name="available_for_courses", blank=True
    )
    menu_items_included = models.ManyToManyField(
        MenuItem, related_name="mandatory_for_courses", blank=True
    )

    objects = MenuObjectsManager()

    def __str__(self):
        if self.variation:
            return f"{self.name} ({self.variation})"
        else:
            return f"{self.name}"

    class Meta:
        ordering = ["sort_order"]


class Package(common_models.SortableBaseModel):
    cxp_id = models.CharField("CXP ID", max_length=12, blank=True)

    name = models.CharField("Package", max_length=64, null=False, blank=False)
    description = models.TextField("Description", blank=True, default="")
    note = models.CharField("Note", max_length=128, blank=True, default="")
    variation = models.CharField("Variation", max_length=60, blank=True, default="")

    flag_attended = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag, related_name="packages", blank=True)
    packages_select_from = models.ManyToManyField(
        "self", symmetrical=False, related_name="available_for_packages", blank=True
    )
    packages_included = models.ManyToManyField(
        "self", symmetrical=False, related_name="mandatory_for_packages", blank=True
    )
    courses_select_from = models.ManyToManyField(
        Course, related_name="available_for_packages", blank=True
    )
    courses_included = models.ManyToManyField(
        Course, related_name="mandatory_for_packages", blank=True
    )
    menu_items_select_from = models.ManyToManyField(
        MenuItem, related_name="available_for_packages", blank=True
    )
    menu_items_included = models.ManyToManyField(
        MenuItem, related_name="mandatory_for_packages", blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="packages"
    )
    cost_type = models.ForeignKey(
        CostType,
        on_delete=models.CASCADE,
        related_name="packages",
        null=True,
        blank=True,
    )  # Default is Temporary Placeholder

    objects = MenuObjectsManager()

    def __str__(self):
        if self.variation:
            if self.category.name == "Bento Boxes":
                return f"{self.name} ({self.variation}) Bento Box"
            else:
                return f"{self.name} ({self.variation})"
        else:
            if self.category.name == "Bento Boxes":
                return f"{self.name} Bento Box"
            else:
                return f"{self.name}"

    class Meta:
        ordering = ["sort_order"]


class Menu(common_models.SortableBaseModel):
    name = models.CharField("Name", max_length=4848, null=False, default="")
    note = models.CharField("Note", max_length=64, blank=True, default="")

    packages = models.ManyToManyField(
        Package, related_name="menus_containing", blank=True
    )

    objects = MenuObjectsManager()

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["sort_order"]


class CourseModificationOption(common_models.SortableBaseModel):
    name = models.CharField("Name", max_length=64, null=False, blank=False)
    description = models.CharField(
        "Description", max_length=255, blank=True, default=""
    )
    variation = models.CharField("Variation", max_length=30, blank=True, default="")

    price_descriptive = models.CharField(
        "Descriptive Price", max_length=128, blank=True, default=""
    )
    price_numeric_per_person = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False, blank=True
    )

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="modifications"
    )
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name="modifications"
    )

    objects = MenuObjectsManager()

    def __str__(self):
        if self.variation:
            return str(self.name) + " (" + str(self.variation) + ")"
        else:
            return str(self.name)

    class Meta:
        ordering = ["name"]


class PackagePrice(common_models.SortableBaseModel):
    note = models.CharField("Note", max_length=128, blank=True, default="")
    variation = models.CharField("Variation", max_length=60, blank=True, default="")
    price_descriptive = models.CharField(
        "Descriptive Price (total)", max_length=128, blank=True, default=""
    )
    price_descriptive_short = models.CharField(
        "Descriptive Price (total), short", max_length=128, blank=True, default=""
    )
    price_numeric = models.DecimalField(
        "Price (per person)", max_digits=12, decimal_places=2, default=0.00, blank=True
    )
    price_numeric_fixed = models.DecimalField(
        "Price (flat fee)",
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=True,
    )
    price_over_limit_descriptive = models.CharField(
        "Descriptive Price (per person) Over Selection Limit",
        max_length=128,
        blank=True,
        default="",
    )
    price_over_limit_numeric = models.DecimalField(
        "Price (per person) Over Selection Limit",
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=True,
    )

    price_under_minimum_fixed = models.DecimalField(
        "Surcharge (flat fee) Under Guest Count Minimum",
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=True,
    )
    price_under_minimum_numeric = models.DecimalField(
        "Surcharge (per person) Under Guest Count Minimum",
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=True,
    )

    lead_time = models.PositiveSmallIntegerField(
        "Lead Time (hours)", default=0, blank=True
    )
    time_limit = models.DurationField(
        default=dt.timedelta(hours=0), null=True, blank=True
    )
    selection_quantity = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        blank=True,
    )

    minimum_guest_count = models.PositiveSmallIntegerField(default=0, blank=True)

    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="package_prices"
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="menu_prices",
        null=True,
        blank=True,
    )
    tenant = models.ForeignKey(
        users_models.Tenant,
        on_delete=models.CASCADE,
        related_name="tenant_prices",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.package.name) + " (" + str(self.variation) + ")"

    class Meta:
        ordering = ["sort_order"]


class AddOn(common_models.SortableBaseModel):
    name = models.CharField("Name", max_length=32, null=False, default="")
    note = models.CharField("Note", max_length=128, blank=True, default="")

    flag_site_specific = models.BooleanField(default=False)
    flag_customer_selectable = models.BooleanField(default=True)

    cost_type = models.ForeignKey(
        CostType,
        on_delete=models.CASCADE,
        related_name="addons",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["sort_order"]


class AddOnPrice(common_models.AbstractBaseModel):
    variation = models.CharField("Variation", max_length=60, blank=True, default="")
    price_descriptive = models.CharField(
        "Descriptive Price", max_length=128, blank=True, default=""
    )
    price_numeric = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False, blank=True
    )  # PER PERSON
    price_numeric_fixed = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False, blank=True
    )  # FLAT FEE

    addon = models.ForeignKey(
        AddOn,
        on_delete=models.CASCADE,
        related_name="prices",
        null=True,
        blank=True,
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="addons",
        null=True,
        blank=True,
    )
    tenant = models.ForeignKey(
        users_models.Tenant,
        on_delete=models.CASCADE,
        related_name="addon_prices",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.addon.name}-{self.menu.name}"

    class Meta:
        ordering = ["addon__name"]
        unique_together = ["addon", "menu"]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ORDERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def increment_invoice_id():
    # changed starting number to 12800 to incorporate prior INVs
    # from ClientPortal migration without chance of collision (< 12700)
    from apps.orders.models import OrderBase

    prefix = "INV-"
    last_order = OrderBase.objects.all().order_by("invoice_number").last()
    if not last_order:
        return f"{prefix}12800"
    order_id = last_order.invoice_number
    order_id_int = int(order_id[4:])
    new_order_id_int = order_id_int + 1
    new_order_id = str(prefix) + str(new_order_id_int).zfill(5)
    return new_order_id


class OrderObjectsManager(models.Manager):
    def is_active(self):
        # Return only objects where flag_active is False
        queryset = self.get_queryset().exclude(flag_active=False)
        return queryset

    def is_draft(self):
        # Return only objects where flag_active is False
        queryset = self.get_queryset().exclude(flag_active=True)
        return queryset


class OrderRepeat(common_models.AbstractBaseModel):
    name = models.CharField(max_length=48, default="DEFAULT")

    def __str__(self):
        if self.name:
            return str(self.name)
        else:
            return (str(self.id))[:10]

    class Meta:
        ordering = ["name"]


class OrderBase(common_models.AbstractBaseModel):
    invoice_number = models.CharField(
        max_length=10,
        default=increment_invoice_id,
        null=False,
        unique=True,
        help_text="Invoice Number",
    )
    cis_numbers = models.CharField(
        max_length=64, blank=True, default="", help_text="CIS Number(s)"
    )

    event_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=DEFAULT_DATE,
        help_text="Order Date",
    )

    order_contact = models.CharField(
        max_length=48, blank=True, default="", help_text="Order Contact"
    )
    order_contact_telephone = models.CharField(
        max_length=48, blank=True, default="", help_text="Order Contact Telephone"
    )
    nickname = models.CharField(
        max_length=96, null=True, blank=True, help_text="Order Description"
    )

    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_submitted = models.DateTimeField(
        "Submitted",
        auto_now_add=False,
        auto_now=False,
        null=True,
        blank=True,
        help_text="Date Submitted",
    )
    date_approved = models.DateTimeField(
        "Approved",
        auto_now_add=False,
        auto_now=False,
        null=True,
        blank=True,
        help_text="Date Approved",
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )
    flag_active = models.BooleanField(default=False, help_text="Is Active")
    flag_custom = models.BooleanField(default=False, help_text="Is Custom Order")

    customer = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Customer",
    )
    repeat = models.ForeignKey(
        OrderRepeat,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        help_text="Order Repeat",
    )

    objects = OrderObjectsManager()
    frames = DataFrameManager()

    def __str__(self):
        return f"{self.invoice_number} {self.event_date} {self.customer.get_full_name}"

    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    def get_absolute_url(self):
        return reverse("portal:dashboard_order_detail", kwargs={"pk": str(self.id)})

    def days_until(self):
        return (self.event_date - dt.datetime.now().date()).days

    def hours_until(self):
        return (self.event_date - dt.datetime.now().date()).seconds / 3660

    def get_start_time(self):
        if self.logistics.count() > 0:
            return self.logistics.latest("event_start")
        else:
            return None

    class Meta:
        ordering = ["event_date"]


class OrderPayment(common_models.AbstractBaseModel):
    flag_active = models.BooleanField(default=False, help_text="Is Active")
    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )

    order = models.OneToOneField(
        OrderBase, on_delete=models.CASCADE, related_name="payment"
    )
    payment = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="Payment Reference",
    )

    objects = OrderObjectsManager()

    def __str__(self):
        return str(self.order)

    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    class Meta:
        ordering = ["order"]


class OrderDeliveryWindow(common_models.AbstractBaseModel):
    DEFAULT_DELIVERY_WINDOW_SIZE = 15  # minutes

    date = models.DateField(null=False)
    window = models.TimeField(auto_now=False, auto_now_add=False)

    flag_draft = models.BooleanField(default=True)

    building = models.ForeignKey(
        users_models.Building,
        on_delete=models.CASCADE,
        related_name="deliveries",
        null=True,
        blank=True,
    )

    def __str__(self):
        return "{0} {1}".format(
            str(self.date.strftime("%Y-%m-%d")),
            str(self.window.strftime("%I:%M %p")),
        )

    @cached_property
    def get_range(self):
        if self.building.delivery_window_size:
            window_size = self.building.delivery_window_size
        else:
            window_size = DEFAULT_WINDOW_SIZE
        range_start = dt.datetime.combine(self.date, self.window)
        range_end = range_start + dt.timedelta(minutes=window_size)

        if (range_start.hour <= 12 and range_end.hour >= 13) or (
            range_start.hour == 23 and range_end.hour == 00
        ):
            range_start_str = range_start.strftime("%I:%M %p")
            if range_start_str[0] == "0":
                range_start_str = range_start_str[1:]

            range_end_str = range_end.strftime("%I:%M %p")
            if range_end_str[0] == "0":
                range_end_str = range_end_str[1:]

            return "from {0} to {1}".format(
                str(range_start_str),
                str(range_end_str),
            )
        else:
            range_start_str = range_start.strftime("%I:%M")
            if range_start_str[0] == "0":
                range_start_str = range_start_str[1:]

            range_end_str = range_end.strftime("%I:%M %p")
            if range_end_str[0] == "0":
                range_end_str = range_end_str[1:]

            return "from {0} to {1}".format(
                str(range_start_str),
                str(range_end_str),
            )

    @cached_property
    def get_range_short(self):
        if self.building.delivery_window_size:
            window_size = self.building.delivery_window_size
        else:
            window_size = DEFAULT_WINDOW_SIZE
        range_start = dt.datetime.combine(self.date, self.window)
        range_end = range_start + dt.timedelta(minutes=window_size)

        if (range_start.hour <= 12 and range_end.hour >= 13) or (
            range_start.hour == 23 and range_end.hour == 00
        ):
            range_start_str = range_start.strftime("%I:%M %p")
            if range_start_str[0] == "0":
                range_start_str = range_start_str[1:]

            range_end_str = range_end.strftime("%I:%M %p")
            if range_end_str[0] == "0":
                range_end_str = range_end_str[1:]

            return "{0} – {1}".format(
                str(range_start_str),
                str(range_end_str),
            )
        else:
            range_start_str = range_start.strftime("%I:%M")
            if range_start_str[0] == "0":
                range_start_str = range_start_str[1:]

            range_end_str = range_end.strftime("%I:%M %p")
            if range_end_str[0] == "0":
                range_end_str = range_end_str[1:]

            return "{0} – {1}".format(
                str(range_start_str),
                str(range_end_str),
            )

    class Meta:
        ordering = [
            "date",
            "window",
            "building",
        ]


class OrderLogistics(common_models.AbstractBaseModel):
    repeat_linking_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    calendar_listing_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True)

    event_delivery_window = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        default=DEFAULT_DATETIME_TZ,
        help_text="Delivery Window",
    )

    event_start = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        default=DEFAULT_DATETIME_TZ,
        help_text="Service Start",
    )
    event_breakdown = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        default=DEFAULT_DATETIME_TZ,
        null=True,
        blank=True,
        help_text="Breakdown",
    )
    flag_breakdown_needed = models.BooleanField(
        default=True, help_text="Is Breakdown Needed"
    )

    building = models.ForeignKey(
        users_models.Building,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
        help_text="Building",
    )
    floor = models.CharField(max_length=48, blank=True, default="", help_text="Floor")
    room = models.CharField(max_length=48, blank=True, default="", help_text="Room")
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="logistics",
        help_text="Location",
    )

    guest_count = models.PositiveSmallIntegerField(
        null=False, default=0, help_text="Guest Count"
    )

    flag_active = models.BooleanField(default=False, help_text="Is Active")
    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )

    addons = models.ManyToManyField(
        AddOn, related_name="logistics", blank=True, help_text="AddOns"
    )
    calendars = models.ManyToManyField(Calendar, related_name="logistics", blank=True)
    order = models.ForeignKey(
        OrderBase, on_delete=models.CASCADE, related_name="logistics"
    )

    objects = OrderObjectsManager()
    frames = DataFrameManager()

    def __str__(self):
        return "{0} {1} {2}".format(
            str(self.order.invoice_number),
            str(self.event_start.date().strftime("%Y-%m-%d")),
            str(self.event_delivery_window.strftime("%I:%M %p")),
            str(self.id)[:5],
        )

    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    def is_draft(self):
        if flag_active == False:
            return self

    def hours_until(self):
        return (self.event_start - timezone.now()).total_seconds() / 3600

    # @cached_property
    def get_range_short(self):
        if self.building.delivery_window_size:
            window_size = self.building.delivery_window_size
        else:
            window_size = DEFAULT_WINDOW_SIZE
        range_start = self.event_delivery_window.astimezone(EASTERN_TZ)
        range_end = range_start + dt.timedelta(minutes=window_size)

        if (range_start.hour <= 12 and range_end.hour >= 13) or (
            range_start.hour == 23 and range_end.hour == 00
        ):
            range_start_str = range_start.strftime("%I:%M %p")
            if range_start_str[0] == "0":
                range_start_str = range_start_str[1:]

            range_end_str = range_end.strftime("%I:%M %p")
            if range_end_str[0] == "0":
                range_end_str = range_end_str[1:]

            return "{0} – {1}".format(
                str(range_start_str),
                str(range_end_str),
            )
        else:
            range_start_str = range_start.strftime("%I:%M")
            if range_start_str[0] == "0":
                range_start_str = range_start_str[1:]

            range_end_str = range_end.strftime("%I:%M %p")
            if range_end_str[0] == "0":
                range_end_str = range_end_str[1:]

            return "{0} – {1}".format(
                str(range_start_str),
                str(range_end_str),
            )

    class Meta:
        get_latest_by = ["-event_start"]
        ordering = ["event_start"]
        verbose_name_plural = "Order logistics"


class OrderNote(common_models.AbstractBaseModel):
    repeat_linking_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True)

    note = models.TextField(blank=True, default="", help_text="Instructions")

    flag_active = models.BooleanField(default=False, help_text="Is Active")
    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )

    logistics = models.OneToOneField(
        OrderLogistics,
        on_delete=models.CASCADE,
        related_name="note",
        null=True,
        blank=True,
    )
    order = models.ForeignKey(
        OrderBase,
        on_delete=models.CASCADE,
        related_name="notes",
        null=True,
        blank=True,
    )

    objects = OrderObjectsManager()

    def __str__(self):
        return str(self.logistics)

    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    class Meta:
        ordering = ["logistics"]


class OrderPackage(common_models.SortableBaseModel):
    repeat_linking_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True)

    price_descriptive = models.CharField(
        "Descriptive Price (total)", max_length=128, blank=True, default=""
    )
    price_descriptive_short = models.CharField(
        "Descriptive Price (total), short", max_length=128, blank=True, default=""
    )
    price_numeric = models.DecimalField(
        "Price (per person)", max_digits=12, decimal_places=2, default=0.00, blank=True
    )
    price_numeric_fixed = models.DecimalField(
        "Price (flat fee)",
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=True,
    )
    price_over_limit_descriptive = models.CharField(
        "Descriptive Price (per person) Over Selection Limit",
        max_length=96,
        blank=True,
        default="",
    )
    price_over_limit_numeric = models.DecimalField(
        "Price (per person) Over Selection Limit",
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=True,
    )
    price_under_minimum_fixed = models.DecimalField(
        "Surcharge (flat fee) Under Guest Count Minimum",
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=True,
    )
    price_under_minimum_numeric = models.DecimalField(
        "Surcharge (per person) Under Guest Count Minimum",
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=True,
    )

    lead_time = models.PositiveSmallIntegerField(default=0, blank=True)
    time_limit = models.DurationField(
        blank=True, default=dt.timedelta(hours=0), help_text="Time Limit"
    )
    selection_quantity = models.PositiveSmallIntegerField(
        blank=True, default=0, help_text="Selection Quantity"
    )
    minimum_guest_count = models.PositiveSmallIntegerField(default=0, blank=True)

    flag_included = models.BooleanField(default=False, help_text="Is Included")
    flag_override = models.BooleanField(default=False, help_text="Has Been Overridden")
    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )

    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="packages", help_text="Package"
    )
    order = models.ForeignKey(
        OrderBase, on_delete=models.CASCADE, related_name="packages"
    )
    logistics = models.ForeignKey(
        OrderLogistics,
        on_delete=models.CASCADE,
        related_name="packages",
        null=True,
        blank=True,
    )
    objects = OrderObjectsManager()
    frames = DataFrameManager()

    def __str__(self):
        return str(self.order) + "-" + str(self.package.name)

    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    class Meta:
        ordering = ["sort_order", "package__name"]


class OrderCourse(common_models.AbstractBaseModel):
    repeat_linking_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True)

    flag_active = models.BooleanField(default=False, help_text="Is Active")
    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="orders", help_text="Course"
    )
    package = models.ForeignKey(
        OrderPackage,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="Package",
    )
    order = models.ForeignKey(
        OrderBase, on_delete=models.CASCADE, related_name="courses"
    )

    objects = OrderObjectsManager()
    frames = DataFrameManager()

    def __str__(self):
        return str(self.order) + "-" + str(self.course.name)

    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    class Meta:
        ordering = ["course__sort_order"]


class OrderMenuItem(common_models.AbstractBaseModel):
    repeat_linking_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True)

    flag_active = models.BooleanField(default=False, help_text="Is Active")
    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )

    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE, related_name="orders", help_text="Menu Item"
    )
    course = models.ForeignKey(
        OrderCourse,
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
        help_text="Course",
    )
    package = models.ForeignKey(
        OrderPackage,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Package",
    )
    order = models.ForeignKey(OrderBase, on_delete=models.CASCADE, related_name="items")

    objects = OrderObjectsManager()
    frames = DataFrameManager()

    def __str__(self):
        return str(self.order) + "-" + str(self.menu_item.name)

    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    class Meta:
        ordering = ["menu_item__sort_order"]


class OrderCourseModification(common_models.AbstractBaseModel):
    price_descriptive = models.CharField(
        "Descriptive Price", max_length=128, blank=True, default=""
    )
    price_numeric_per_person = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False, blank=True
    )

    course = models.ForeignKey(
        OrderCourse, on_delete=models.CASCADE, related_name="ordered_modifications"
    )
    menu_item = models.ForeignKey(
        OrderMenuItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="modifications",
    )
    modification = models.ForeignKey(
        CourseModificationOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ordered_mods",
    )

    objects = MenuObjectsManager()

    def __str__(self):
        return "{0}-{1}".format(
            self.menu_item.order.invoice_number,
            self.modification.name,
        )

    class Meta:
        ordering = ["menu_item__menu_item__name"]


class OrderAddOn(common_models.SortableBaseModel):
    repeat_linking_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True)

    name = models.CharField(
        "Name", max_length=32, null=False, blank=False, help_text="Name"
    )
    note = models.CharField(
        "Note", max_length=128, blank=True, default="", help_text="Note"
    )

    price_descriptive = models.CharField(
        "Descriptive Price",
        max_length=128,
        blank=True,
        default="",
        help_text="Price Descriptive",
    )
    price_numeric = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        blank=True,
        help_text="Price Per Person",
    )
    price_numeric_fixed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        blank=True,
        help_text="Price Flat Fee",
    )

    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )

    flag_automatically_applied = models.BooleanField(
        default=False, help_text="Is Automatically Applied"
    )

    addon = models.ForeignKey(
        AddOn,
        on_delete=models.CASCADE,
        related_name="addons_staff",
        null=True,
        blank=True,
        help_text="AddOn",
    )
    logistics = models.ForeignKey(
        OrderLogistics,
        on_delete=models.CASCADE,
        related_name="addons_staff",
        null=True,
        blank=True,
        help_text="Setup/Delivery",
    )
    package = models.ForeignKey(
        OrderPackage,
        on_delete=models.CASCADE,
        related_name="addons_staff",
        null=True,
        blank=True,
        help_text="Package",
    )
    order = models.ForeignKey(
        OrderBase, on_delete=models.CASCADE, related_name="addons_staff"
    )
    cost_type = models.ForeignKey(
        CostType,
        on_delete=models.CASCADE,
        related_name="addons_staff",
        null=True,
        blank=True,
        help_text="Cost Type",
    )

    objects = OrderObjectsManager()

    def __str__(self):
        return str(self.order.invoice_number) + "-" + str(self.name)

    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    class Meta:
        ordering = ["name"]


class OrderHistory(common_models.AbstractBaseModel):
    comment = models.TextField(blank=False, default="")
    date_changed = models.DateTimeField(
        "Changed on", auto_now=False, auto_now_add=False
    )
    date_last_updated = models.DateTimeField("Updated", auto_now=True)

    flag_email_sent = models.BooleanField(default=False)

    changed_by = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    order = models.ForeignKey(
        OrderBase, on_delete=models.CASCADE, related_name="history"
    )

    def __str__(self):
        return (
            str(self.order.invoice_number)
            + "-"
            + str(self.date_changed.strftime("%Y-%m-%d-%I:%M %p"))
        )

    class Meta:
        ordering = ["-date_changed"]
        verbose_name_plural = "Order histories"


class OrderStatus(common_models.AbstractBaseModel):
    STATUS_CHOICES = (
        ("AWAITING", "Awaiting Approval"),
        ("PENDING", "Pending"),  # New Order, not yet viewed by
        ("CONFIRMED", "Confirmed"),
        ("CHANGE_REQUEST", "Change Requested"),
        ("CANCELLED", "Cancelled"),
        ("STATE_0", "State0 Start"),
        ("STATE_1", "State1 Where"),
        ("STATE_2", "State2 Time"),
        ("STATE_3A", "State3A Selection Packages"),
        ("STATE_3B", "State3B Selection Choices"),
        ("STATE_4", "State4 Details"),
    )

    status = models.CharField(
        "Status", max_length=32, choices=STATUS_CHOICES, default="Pending", null=False
    )
    date_changed = models.DateTimeField(
        "Changed on", auto_now=False, auto_now_add=False
    )

    flag_cxp = models.BooleanField(default=False)
    flag_calendar = models.BooleanField(default=False)
    flag_rentals = models.BooleanField(default=False)

    changed_by = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    order = models.OneToOneField(
        OrderBase, on_delete=models.CASCADE, related_name="status"
    )

    def __str__(self):
        return (
            str(self.order.invoice_number)
            + "-"
            + str(self.date_changed.strftime("%Y-%m-%d-%I:%M %p"))
        )

    class Meta:
        ordering = ["-date_changed"]
        verbose_name_plural = "Order statuses"


class BillingRecord(common_models.AbstractBaseModel):
    event_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=DEFAULT_DATE,
        help_text="Order Date",
    )
    payment_reference = models.CharField(max_length=96, blank=True)
    payment_note = models.CharField(max_length=96, blank=True)

    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        blank=True,
        help_text="Total Cost",
    )
    food_internal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        blank=True,
        help_text="Food (Internal)",
    )
    food_external = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        blank=True,
        help_text="Food (External)",
    )
    alcohol_beverages = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        blank=True,
        help_text="Alcohol/Beverages",
    )
    labor = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, blank=True, help_text="Labor"
    )
    rentals = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, blank=True, help_text="Rentals"
    )

    date_created = models.DateTimeField(
        "Created", auto_now_add=True, help_text="Date Created"
    )
    date_last_updated = models.DateTimeField(
        "Updated", auto_now=True, help_text="Date Last Updated"
    )
    date_billed = models.DateTimeField(
        "Billed",
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
        help_text="Date Billed to Client",
    )

    pdf_as_of_record = models.FileField(
        "PDF at time of record", upload_to="billing_pdfs/", null=True, blank=True
    )

    order = models.OneToOneField(
        OrderBase, on_delete=models.CASCADE, related_name="billing_record"
    )
    changed_by = models.ForeignKey(
        users_models.User, on_delete=models.SET_NULL, related_name="+", null=True
    )

    objects = models.Manager()
    frames = DataFrameManager()

    def __str__(self):
        return "{0}".format(self.order.invoice_number)

    class Meta:
        ordering = ["event_date", "order__invoice_number"]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Settings(common_models.HistoryMixin, common_models.SortableBaseModel):
    """ Orders settings """

    # ––– WORKFLOW SETTINGS –––––––––––––––––––––––––––––––––––––––––
    flag_tenant_workflow = models.BooleanField(default=False)

    # ––– INTERFACE SETTINGS ––––––––––––––––––––––––––––––––––––––––
    site_title = models.CharField(
        max_length=32, blank=True, default="Catering Services"
    )
    flag_sameday_ordering = models.BooleanField(
        default=False, help_text="Allowed to Order Same-Day?"
    )
    sameday_ordering_leadtime = models.PositiveSmallIntegerField(
        default=0, blank=True, help_text="Same-Day Lead-time (hours)"
    )  # hours
    sameday_ordering_categories = models.ManyToManyField(
        Category, related_name="+", blank=True, help_text="Same-Day Categories"
    )

    # ––– CONTACT SETTINGS ––––––––––––––––––––––––––––––––––––––––––
    gp_contact_email = models.EmailField(null=True, blank=True)

    # ––– MENU SETTINGS –––––––––––––––––––––––––––––––––––––––––––––

    # Specify which menu is available for ordering
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="tenants",
        null=True,
        blank=True,
    )

    MENU_PRICING_CHOICES = (
        ("Default", "Default"),
        ("Tenant-specific", "Tenant-specific"),
    )

    # Specify if tenant has special pricing for this menu or uses default
    menu_pricing = models.CharField(
        max_length=16, choices=MENU_PRICING_CHOICES, default="Default", null=False
    )

    addon_staff_labor_captain_charge = models.PositiveSmallIntegerField(
        default=0, blank=True
    )
    addon_staff_labor_charge = models.PositiveSmallIntegerField(default=0, blank=True)
    addon_after_hours_scheduled_event_charge = models.PositiveSmallIntegerField(
        default=0, blank=True
    )
    addon_after_hours_event_breakdown_charge = models.PositiveSmallIntegerField(
        default=0, blank=True
    )
    addon_small_order_charge = models.PositiveSmallIntegerField(default=0, blank=True)
    lead_time_by_guest_count_threshold = models.PositiveSmallIntegerField(
        "Guest Count to trigger lead time", default=0, blank=True
    )
    lead_time_by_guest_count_value = models.PositiveSmallIntegerField(
        "Lead Time constraint (hours)", default=0, blank=True
    )

    minimum_guest_counts_descriptive = models.TextField(null=True, blank=True)
    lead_times_descriptive = models.TextField(null=True, blank=True)

    # ––– BUILDING SETTINGS –––––––––––––––––––––––––––––––––––––––––

    flag_defined_locations = models.BooleanField(default=False)

    # If true, common floors will be included in all delivery location picklists
    use_common_floors = models.BooleanField(default=True)

    # Specifiy the floors occupied by this tenant – will be offered on delivery location picklists
    tenant_floors = models.ManyToManyField(
        users_models.Floor, related_name="floors", blank=True
    )

    # Specify which elevators service this tenant(s) floors
    elevators = models.ManyToManyField(
        users_models.Elevator, related_name="tenants", blank=True
    )

    # ––– ORDERING SETTINGS –––––––––––––––––––––––––––––––––––––––––

    # Addons selected here will be available for selection during ordering process
    addons = models.ManyToManyField(AddOn, related_name="addons", blank=True)

    # Schedule, descriptive text
    schedule_descriptive = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # Allowed order days and time range – orders outside this range will automatically incur a charge
    allow_sunday = models.BooleanField(default=False)
    allow_monday = models.BooleanField(default=True)
    allow_tuesday = models.BooleanField(default=True)
    allow_wednesday = models.BooleanField(default=True)
    allow_thursday = models.BooleanField(default=True)
    allow_friday = models.BooleanField(default=True)
    allow_saturday = models.BooleanField(default=False)

    allow_everyday = models.BooleanField(default=False)

    timeline_start = models.TimeField(default=DEFAULT_START_TIME)
    timeline_end = models.TimeField(default=DEFAULT_END_TIME)

    closed_days = models.ManyToManyField(ClosedDay, related_name="+", blank=True)

    # ––– DELIVERY SETTINGS –––––––––––––––––––––––––––––––––––––––––

    # Require user to specify building for delivery when placing order for this tenant
    is_building_required = models.BooleanField(default=False)

    REDIRECT_DELIVERIES_TO_RECEPTION = (
        ("User Directs Deliveries", "User Directs Deliveries"),
        ("All Deliveries Redirected", "All Deliveries Redirected"),
    )

    # Tenant option to limit delivery location to security or reception area

    choice_location_deliver_to_reception = models.CharField(
        max_length=32,
        choices=REDIRECT_DELIVERIES_TO_RECEPTION,
        default="User Directs Deliveries",
        null=False,
    )
    user_last_updated_choice_location_deliver_to_reception = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_choice_location_deliver_to_reception = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    value_location_deliver_to_reception = models.CharField(
        max_length=255, blank=True, default=""
    )
    user_last_updated_value_location_deliver_to_reception = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_value_location_deliver_to_reception = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    # Tenant option to limit delivery location to specific drop-down options

    RESTRICT_DELIVERY_DESTINATIONS = (
        ("User Enters Destinations", "User Enters Destinations"),
        ("Limited to Listed Destinations", "Limited to Listed Destinations"),
    )

    choice_location_restrict_locations = models.CharField(
        max_length=32,
        choices=RESTRICT_DELIVERY_DESTINATIONS,
        default="User Enters Destinations",
        null=False,
    )
    user_last_updated_choice_location_restrict_locations = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_choice_location_restrict_locations = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    value_location_restrict_locations = models.TextField(null=True, blank=True)
    user_last_updated_value_location_restrict_locations = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_value_location_restrict_locations = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    # ––– USER SETTINGS –––––––––––––––––––––––––––––––––––––––––––––

    USER_SIGNUP_CHOICES = (
        ("Tenant Distributes Signup URL", "Tenant Distributes Signup URL"),
    )

    # Tenant option whether to allow users to sign-up directly on site or if they must be created by Tenant Manager/GP Manager
    choice_user_signup_method = models.CharField(
        max_length=32,
        choices=USER_SIGNUP_CHOICES,
        default="Tenant Distributes Signup URL",
        null=False,
    )
    user_last_updated_user_signup_method = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_user_signup_method = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    APPROVE_DIRECT_SIGNUP_CHOICES = (
        ("Tenant Must Approve", "Tenant Must Approve"),
        ("Allow with Valid Email", "Allow with Valid Email"),
    )

    # (2) alternatives:
    # No email validation, but then TM must approve new users
    # or (EASIER FOR TENANT) no approval necessary but user email must be company standard

    # IF DIRECT SIGNUPS ALLOWED, choice to require tenant approval of all directly-signed-up users by tenant masteruser before validated
    choice_approve_direct_signup = models.CharField(
        max_length=24,
        choices=APPROVE_DIRECT_SIGNUP_CHOICES,
        default="Tenant Must Approve",
        null=True,
    )
    user_last_updated_approve_direct_signup = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_approve_direct_signup = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    # IF DIRECT SIGNUPS ALLOWED, users signing up must be have email address of this tenant-specified form
    value_user_email_validation = models.CharField(
        "Email format", max_length=48, blank=True, default=""
    )
    user_last_updated_user_email_validation = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_user_email_validation = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    # ––– PAYMENT SETTINGS ––––––––––––––––––––––––––––––––––––––––––

    tenant_has_house_account = models.BooleanField(default=True)
    tenant_specific_billing_options = models.BooleanField(default=False)
    user_can_access_all_tenant_accounts = models.BooleanField(default=False)

    RESTRICT_PAYMENT_TO_HOUSE_ACCOUNT = (
        ("User Enters Payment Account", "User Enters Payment Account"),
        ("Pay With House Account Only", "Pay With House Account Only"),
    )

    # Tenant option to limit payment method to their house account
    choice_payment_restrict_to_house_account = models.CharField(
        max_length=32,
        choices=RESTRICT_PAYMENT_TO_HOUSE_ACCOUNT,
        default="Pay With House Account Only",
        null=False,
    )
    user_last_updated_choice_payment_restrict_to_house_account = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_choice_payment_restrict_to_house_account = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    REQUIRE_PAYMENT_NOTATION = (
        ("User Must Provide Note", "User Must Provide Note"),
        ("No Notation Required", "No Notation Required"),
    )

    # Tenant option to require users to provide brief note describing use of house account
    choice_payment_require_payment_notation = models.CharField(
        max_length=32,
        choices=REQUIRE_PAYMENT_NOTATION,
        default="User Must Provide Note",
        null=False,
    )
    user_last_updated_choice_payment_require_notation = models.ForeignKey(
        users_models.User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    date_last_updated_choice_payment_require_notation = models.DateTimeField(
        auto_now=False, auto_now_add=False, default=DEFAULT_DATETIME_TZ
    )

    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    calendar = models.ForeignKey(
        Calendar,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sitesettings",
    )
    tenant = models.OneToOneField(
        users_models.Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Settings for Orders app"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        permissions = [
            (
                "change_orders_settings",
                "Can change Orders settings",
            ),
        ]
        verbose_name_plural = "Settings"
