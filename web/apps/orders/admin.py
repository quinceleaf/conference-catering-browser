# ––– DJANGO IMPORTS
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


# ––– THIRD-PARTY IMPORTS


# ––– APPLICATION IMPORTS
from apps.common.admin import BaseAdminConfig
from apps.orders import models


"""
Admin for:

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


@admin.register(models.Calendar)
class Calendar(BaseAdminConfig):
    pass


@admin.register(models.Category)
class Category(BaseAdminConfig):
    pass


@admin.register(models.ClosedDay)
class ClosedDay(BaseAdminConfig):
    pass


@admin.register(models.CostType)
class CostType(BaseAdminConfig):
    pass


@admin.register(models.Location)
class Location(BaseAdminConfig):
    pass


@admin.register(models.PaymentMethod)
class PaymentMethod(BaseAdminConfig):
    pass


@admin.register(models.Tag)
class Tag(BaseAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MENU
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.AddOn)
class AddOn(BaseAdminConfig):
    pass


@admin.register(models.AddOnPrice)
class AddOnPrice(BaseAdminConfig):
    pass


@admin.register(models.Course)
class Course(BaseAdminConfig):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "variation",
                    "note",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price_descriptive",
                    "price_numeric_fixed",
                    "price_numeric_per_person",
                )
            },
        ),
        (
            "Menu Items",
            {
                "fields": (
                    "selection_quantity",
                    "menu_items_included",
                    "menu_items_select_from",
                )
            },
        ),
        (
            "Tags",
            {"fields": ("tags",)},
        ),
        (
            "Miscellaneous",
            {"fields": ("flag_active", "sort_order", "cxp_id")},
        ),
    ) + BaseAdminConfig.readonly_fieldsets


@admin.register(models.CourseModificationOption)
class CourseModificationOption(BaseAdminConfig):
    pass


@admin.register(models.Menu)
class Menu(BaseAdminConfig):
    pass


@admin.register(models.MenuItem)
class MenuItem(BaseAdminConfig):
    pass


@admin.register(models.Package)
class Package(BaseAdminConfig):
    pass


@admin.register(models.PackagePrice)
class PackagePrice(BaseAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ORDERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@admin.register(models.BillingRecord)
class BillingRecord(BaseAdminConfig):
    pass


@admin.register(models.OrderAddOn)
class OrderAddOn(BaseAdminConfig):
    pass


@admin.register(models.OrderBase)
class OrderBase(BaseAdminConfig):
    def get_status(self, obj):
        return obj.status.get_status_display()

    list_display = (
        "__str__",
        "get_status",
    )
    list_filter = (
        "status__status",
        "flag_custom",
    )


@admin.register(models.OrderCourse)
class OrderCourse(BaseAdminConfig):
    pass


@admin.register(models.OrderCourseModification)
class OrderCourseModification(BaseAdminConfig):
    pass


@admin.register(models.OrderDeliveryWindow)
class OrderDeliveryWindow(BaseAdminConfig):
    pass


@admin.register(models.OrderHistory)
class OrderHistory(BaseAdminConfig):
    pass


@admin.register(models.OrderLogistics)
class OrderLogistics(BaseAdminConfig):
    pass


@admin.register(models.OrderMenuItem)
class OrderMenuItem(BaseAdminConfig):
    pass


@admin.register(models.OrderNote)
class OrderNote(BaseAdminConfig):
    pass


@admin.register(models.OrderPackage)
class OrderPackage(BaseAdminConfig):
    pass


@admin.register(models.OrderPayment)
class OrderPayment(BaseAdminConfig):
    pass


@admin.register(models.OrderRepeat)
class OrderRepeat(BaseAdminConfig):
    pass


@admin.register(models.OrderStatus)
class OrderStatus(BaseAdminConfig):
    pass


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Settings(BaseAdminConfig):
    pass
