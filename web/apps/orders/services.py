# ––– DJANGO IMPORTS
from django.db.models import Model, QuerySet
from django.core.files import File
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.utils import timezone


# ––– PYTHON UTILITY IMPORTS
from collections import deque
import csv
import datetime
import datetime as dt
import decimal
from decimal import Decimal as D
import json
from tempfile import NamedTemporaryFile
from typing import Tuple


# ––– THIRD-PARTY IMPORTS
from openpyxl import load_workbook, Workbook
from openpyxl.utils import absolute_coordinate, quote_sheetname
from openpyxl.worksheet.cell_range import CellRange
from openpyxl.worksheet.datavalidation import DataValidation
import pytz
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration


# ––– APPLICATION IMPORTS
from apps.orders import forms, models
from apps.common import services as common_services


# --- PARAMETERS
EASTERN_TZ = pytz.timezone("US/Eastern")


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# FINANCIAL
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def calculate_logistics_cost(*, logistics: models.OrderLogistics, status: str) -> dict:
    """
    For each package, calculate package, course, and menu item costs
    For order, calculate addon costs
    """

    logistics_estimated_cost = 0
    cost_food_internal = 0
    cost_food_external = 0
    cost_beverage = 0
    cost_labor = 0
    cost_rentals = 0

    if status == "review":
        addons = logistics.addons_staff.all().filter(package__isnull=True)
    elif status == "is_active":
        addons = logistics.addons_staff.is_active().filter(package__isnull=True)
    elif status == "is_draft":
        addons = logistics.addons_staff.is_draft().filter(package__isnull=True)
    else:
        addons = logistics.addons_staff.all().filter(package__isnull=True)

    combined_per_person_cost = 0
    combined_fixed_cost = 0

    # ––– ADDONS ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    addons_staff = []

    for addon in addons:
        temp = {}

        temp["id"] = addon.id
        temp["name"] = addon.name
        temp["price_numeric"] = addon.price_numeric
        temp["price_numeric_fixed"] = addon.price_numeric_fixed

        addon_cost = (
            addon.price_numeric * logistics.guest_count
        ) + addon.price_numeric_fixed
        temp["cost"] = addon_cost

        temp["cost_type_id"] = addon.cost_type_id
        temp["package_id"] = addon.package_id
        temp["logistics_id"] = addon.logistics_id

        if addon.note:
            temp["note"] = addon.note
        else:
            if (addon.price_numeric > 0) and (addon.price_numeric_fixed > 0):
                temp["price_descriptive"] = "{0} per person, plus {1} fee".format(
                    addon.price_numeric, addon.price_numeric_fixed
                )
            elif addon.price_numeric == 1:
                temp["price_descriptive"] = "{0} guest, at {1} per person".format(
                    logistics.guest_count, addon.price_numeric
                )
            elif addon.price_numeric > 1:
                temp["price_descriptive"] = "{0} guests, at {1} per person".format(
                    logistics.guest_count, addon.price_numeric
                )
            else:
                temp["price_descriptive"] = "{0} fee".format(addon.price_numeric_fixed)

        addons_staff.append(temp)

        if addon.cost_type.name == "Food (Internal)":
            cost_food_internal += addon_cost
        elif addon.cost_type.name == "Food (External)":
            cost_food_external += addon_cost
        elif addon.cost_type.name == "Alcohol and NA Beverages":
            cost_beverage += addon_cost
        elif addon.cost_type.name == "Labor":
            cost_labor += addon_cost
        elif addon.cost_type.name == "Equipment and Rentals":
            cost_rentals += addon_cost

    return {
        "addons_staff": addons_staff,
        "cost_food_internal": cost_food_internal,
        "cost_food_external": cost_food_external,
        "cost_beverage": cost_beverage,
        "cost_labor": cost_labor,
        "cost_rentals": cost_rentals,
    }


def calculate_package_cost(*, orderpackage: models.OrderPackage, status: str) -> dict:
    """
    For each package, calculate package, course, and menu item costs
    For order, calculate addon costs
    """

    from apps.orders.models import OrderCourse, OrderMenuItem, OrderAddOn

    package_estimated_cost = 0
    cost_food_internal = 0
    cost_food_external = 0
    cost_beverage = 0
    cost_labor = 0
    cost_rentals = 0

    if status == "review":
        courses = orderpackage.courses.all()
        menu_items = orderpackage.items.all()
        addons = orderpackage.addons_staff.all().filter(logistics__isnull=True)
    elif status == "is_active":
        courses = orderpackage.courses.is_active()
        menu_items = orderpackage.items.is_active()
        addons = orderpackage.addons_staff.is_active().filter(logistics__isnull=True)
    elif status == "is_draft":
        courses = orderpackage.courses.is_draft()
        menu_items = orderpackage.items.is_draft()
        addons = orderpackage.addons_staff.is_draft().filter(logistics__isnull=True)
    else:
        courses = orderpackage.courses.all()
        menu_items = orderpackage.items.all()
        addons = orderpackage.addons_staff.all().filter(logistics__isnull=True)

    combined_per_person_cost = 0
    combined_fixed_cost = 0

    # ––– PACKAGE –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    package_estimated_cost += (
        orderpackage.price_numeric * orderpackage.logistics.guest_count
    ) + orderpackage.price_numeric_fixed
    combined_per_person_cost += orderpackage.price_numeric
    combined_fixed_cost += orderpackage.price_numeric_fixed

    """
    (3) possibilities:
    - if selection_quantity == 0 // NO CHOICE
    - elif selection_quantity == 999 // ARBITRARY NUMBER OF CHOICES
    – else selection_quantity specific
    if there are courses -> then selection_quantity refers to courses
    else selection_quantity refers to menu_items
    """

    # for now, over_limit costs refer only to menu selections
    if menu_items.count() > orderpackage.selection_quantity:
        package_estimated_cost += orderpackage.price_over_limit_numeric * (
            (menu_items.count() - orderpackage.selection_quantity)
            * orderpackage.logistics.guest_count
        )
        combined_per_person_cost += orderpackage.price_over_limit_numeric * (
            menu_items.count() - orderpackage.selection_quantity
        )

    # course
    if courses:
        for course in courses:
            package_estimated_cost += (
                course.course.price_numeric_per_person
                * orderpackage.logistics.guest_count
            ) + course.course.price_numeric_fixed
            combined_per_person_cost += course.course.price_numeric_per_person
            combined_fixed_cost += course.course.price_numeric_fixed
    else:
        pass

    # menu item
    for menu_item in menu_items:
        if menu_item.modifications.count() > 0:
            per_person_cost = menu_item.menu_item.price_numeric_per_person
            for mod in menu_item.modifications.all():
                per_person_cost += mod.price_numeric_per_person
            package_estimated_cost += (
                per_person_cost * orderpackage.logistics.guest_count
            ) + menu_item.menu_item.price_numeric_fixed
            combined_per_person_cost += per_person_cost
            combined_fixed_cost += menu_item.menu_item.price_numeric_fixed
        else:
            package_estimated_cost += (
                menu_item.menu_item.price_numeric_per_person
                * orderpackage.logistics.guest_count
            ) + menu_item.menu_item.price_numeric_fixed
            combined_per_person_cost += menu_item.menu_item.price_numeric_per_person
            combined_fixed_cost += menu_item.menu_item.price_numeric_fixed

    # ––– PRICE DESCRIPTIVE –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    if (combined_per_person_cost > orderpackage.price_numeric) or (
        combined_fixed_cost > orderpackage.price_numeric_fixed
    ):
        if combined_fixed_cost > 0:
            price_descriptive = "{0} per person, plus {1} fee".format(
                combined_per_person_cost, combined_fixed_cost
            )
        else:
            price_descriptive = "{0} per person".format(combined_per_person_cost)
    else:
        if len(orderpackage.price_descriptive_short) > 0:
            price_descriptive = orderpackage.price_descriptive_short
        else:
            price_descriptive = orderpackage.price_descriptive

    # ––– ADDONS ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    addons_staff = []

    for addon in addons:
        addon_cost = (
            addon.price_numeric * orderpackage.logistics.guest_count
        ) + addon.price_numeric_fixed

        temp = {}

        temp["id"] = addon.id
        temp["name"] = addon.name
        temp["cost"] = addon_cost
        if addon.note:
            temp["note"] = addon.note
        else:
            temp["note"] = price_descriptive
        temp["price_numeric"] = addon.price_numeric
        temp["price_numeric_fixed"] = addon.price_numeric_fixed
        temp["cost_type_id"] = addon.cost_type_id
        temp["package_id"] = addon.package_id
        temp["logistics_id"] = addon.logistics_id
        addons_staff.append(temp)

        if addon.cost_type.name == "Food (Internal)":
            cost_food_internal += addon_cost
        elif addon.cost_type.name == "Food (External)":
            cost_food_external += addon_cost
        elif addon.cost_type.name == "Alcohol and NA Beverages":
            cost_beverage += addon_cost
        elif addon.cost_type.name == "Labor":
            cost_labor += addon_cost
        elif addon.cost_type.name == "Equipment and Rentals":
            cost_rentals += addon_cost

    if orderpackage.package.cost_type.name == "Food (Internal)":
        cost_food_internal += package_estimated_cost
    elif orderpackage.package.cost_type.name == "Food (External)":
        cost_food_external += package_estimated_cost
    elif orderpackage.package.cost_type.name == "Alcohol and NA Beverages":
        cost_beverage += package_estimated_cost
    elif orderpackage.package.cost_type.name == "Labor":
        cost_labor += package_estimated_cost
    elif orderpackage.package.cost_type.name == "Equipment and Rentals":
        cost_rentals += package_estimated_cost

    return {
        "cost": package_estimated_cost,
        "guest_count": orderpackage.logistics.guest_count,
        "price_descriptive": price_descriptive,
        "addons_staff": addons_staff,
        "cost_food_internal": cost_food_internal,
        "cost_food_external": cost_food_external,
        "cost_beverage": cost_beverage,
        "cost_labor": cost_labor,
        "cost_rentals": cost_rentals,
    }


def calculate_order_total_cost(*, order: models.OrderBase, status: str) -> dict:
    """
    For each package, calculate package, course, and menu item costs
    For order, calculate addon costs
    Valid status choices: review, submitted
    """
    from apps.orders.models import OrderAddOn, OrderCourse, OrderMenuItem

    total_estimated_cost = 0
    cost_food_internal = 0
    cost_food_external = 0
    cost_beverage = 0
    cost_labor = 0
    cost_rentals = 0

    if status == "review":
        logistics_set = order.logistics.all()
        addons_set = order.addons_staff.all().filter(
            logistics__isnull=True, package__isnull=True
        )
    elif status == "is_active":
        logistics_set = order.logistics.is_active()
        addons_set = order.addons_staff.is_active().filter(
            logistics__isnull=True, package__isnull=True
        )
    elif status == "is_draft":
        logistics_set = order.logistics.is_draft()
        addons_set = order.addons_staff.is_draft().filter(
            logistics__isnull=True, package__isnull=True
        )
    elif status == "add_package":
        logistics_set = order.logistics.is_active()
        addons_set = order.addons_staff.is_active().filter(
            logistics__isnull=True, package__isnull=True
        )
    else:
        logistics_set = order.logistics.all()
        addons_set = order.addons_staff.all().filter(
            logistics__isnull=True, package__isnull=True
        )

    # ––– PACKAGES ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    for logistics in logistics_set:

        if status == "review":
            packages = logistics.packages.all()
            addons_logistics = logistics.addons_staff.all().filter(package__isnull=True)
        elif status == "is_active":
            packages = logistics.packages.is_active()
            addons_logistics = logistics.addons_staff.is_active().filter(
                package__isnull=True
            )
        elif status == "is_draft":
            packages = logistics.packages.is_draft()
            addons_logistics = logistics.addons_staff.is_draft().filter(
                package__isnull=True
            )
        elif status == "add_package":
            packages = logistics.packages.is_draft()
            addons_logistics = logistics.addons_staff.is_draft().filter(
                package__isnull=True
            )
        else:
            packages = logistics.packages.all()
            addons_logistics = logistics.addons_staff.all().filter(package__isnull=True)

        for orderpackage in packages:

            if status == "review":
                courses = orderpackage.courses.all()
                menu_items = orderpackage.items.all()
                addons = orderpackage.addons_staff.all().filter(logistics__isnull=True)
            elif status == "is_active":
                courses = orderpackage.courses.is_active()
                menu_items = orderpackage.items.is_active()
                addons = orderpackage.addons_staff.is_active().filter(
                    logistics__isnull=True
                )
            elif status == "is_draft":
                courses = orderpackage.courses.is_draft()
                menu_items = orderpackage.items.is_draft()
                addons = orderpackage.addons_staff.is_draft().filter(
                    logistics__isnull=True
                )
            elif status == "add_package":
                courses = orderpackage.courses.is_draft()
                menu_items = orderpackage.items.is_draft()
                addons = orderpackage.addons_staff.is_draft().filter(
                    logistics__isnull=True
                )
            else:
                courses = orderpackage.courses.all()
                menu_items = orderpackage.items.all()
                addons = orderpackage.addons_staff.all().filter(logistics__isnull=True)

            package_estimated_cost = 0
            combined_per_person_cost = 0
            combined_fixed_cost = 0

            # ––– PACKAGE –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
            package_estimated_cost += (
                orderpackage.price_numeric * logistics.guest_count
            ) + orderpackage.price_numeric_fixed
            combined_per_person_cost += orderpackage.price_numeric
            combined_fixed_cost += orderpackage.price_numeric_fixed

            """
            (3) possibilities:
            - if selection_quantity == 0 // NO CHOICE
            - elif selection_quantity == 999 // ARBITRARY NUMBER OF CHOICES
            – else selection_quantity specific
            if there are courses -> then selection_quantity refers to courses
            else selection_quantity refers to menu_items
            """

            # for now, over_limit costs refer only to menu selections
            if menu_items.count() > orderpackage.selection_quantity:
                package_estimated_cost += orderpackage.price_over_limit_numeric * (
                    (menu_items.count() - orderpackage.selection_quantity)
                    * logistics.guest_count
                )
                combined_per_person_cost += orderpackage.price_over_limit_numeric * (
                    menu_items.count() - orderpackage.selection_quantity
                )

            # course
            if courses:
                for course in courses:
                    package_estimated_cost += (
                        course.course.price_numeric_per_person * logistics.guest_count
                    ) + course.course.price_numeric_fixed
                    combined_per_person_cost += course.course.price_numeric_per_person
                    combined_fixed_cost += course.course.price_numeric_fixed
            else:
                pass

            # menu item
            for menu_item in menu_items:
                # if menu item modification
                if menu_item.modifications.count() > 0:
                    per_person_cost = menu_item.menu_item.price_numeric_per_person
                    for mod in menu_item.modifications.all():
                        per_person_cost += mod.price_numeric_per_person
                    package_estimated_cost += (
                        per_person_cost * logistics.guest_count
                    ) + menu_item.menu_item.price_numeric_fixed
                    combined_per_person_cost += per_person_cost
                    combined_fixed_cost += menu_item.menu_item.price_numeric_fixed
                else:
                    package_estimated_cost += (
                        menu_item.menu_item.price_numeric_per_person
                        * logistics.guest_count
                    ) + menu_item.menu_item.price_numeric_fixed
                    combined_per_person_cost += (
                        menu_item.menu_item.price_numeric_per_person
                    )
                    combined_fixed_cost += menu_item.menu_item.price_numeric_fixed

            """
            package_estimated_cost to this point is only package, not addons
            since (conceivably) cost_type for a package_addon could set differently than that of package,
            apply package_estimated_cost to cost_type totals, then do so separately/individually for each addon
            """

            if orderpackage.package.cost_type.name == "Food (Internal)":
                cost_food_internal += package_estimated_cost
            elif orderpackage.package.cost_type.name == "Food (External)":
                cost_food_external += package_estimated_cost
            elif orderpackage.package.cost_type.name == "Alcohol and NA Beverages":
                cost_beverage += package_estimated_cost
            elif orderpackage.package.cost_type.name == "Labor":
                cost_labor += package_estimated_cost
            elif orderpackage.package.cost_type.name == "Equipment and Rentals":
                cost_rentals += package_estimated_cost

            # package addons
            for addon in addons:
                addon_cost = (
                    addon.price_numeric * logistics.guest_count
                ) + addon.price_numeric_fixed
                package_estimated_cost += addon_cost

                if addon.cost_type.name == "Food (Internal)":
                    cost_food_internal += addon_cost
                elif addon.cost_type.name == "Food (External)":
                    cost_food_external += addon_cost
                elif addon.cost_type.name == "Alcohol and NA Beverages":
                    cost_beverage += addon_cost
                elif addon.cost_type.name == "Labor":
                    cost_labor += addon_cost
                elif addon.cost_type.name == "Equipment and Rentals":
                    cost_rentals += addon_cost

            total_estimated_cost += package_estimated_cost

        # ––– ADDONS (per logistics) ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

        for orderaddon in addons_logistics:
            orderaddon_cost = (
                orderaddon.price_numeric * orderaddon.logistics.guest_count
            ) + orderaddon.price_numeric_fixed
            total_estimated_cost += orderaddon_cost
            if orderaddon.cost_type.name == "Food (Internal)":
                cost_food_internal += orderaddon_cost
            elif orderaddon.cost_type.name == "Food (External)":
                cost_food_external += orderaddon_cost
            elif orderaddon.cost_type.name == "Alcohol and NA Beverages":
                cost_beverage += orderaddon_cost
            elif orderaddon.cost_type.name == "Labor":
                cost_labor += orderaddon_cost
            elif orderaddon.cost_type.name == "Equipment and Rentals":
                cost_rentals += orderaddon_cost

    # ––– ADDONS (per order) ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    for orderaddon in addons_set:
        total_estimated_cost += orderaddon.price_numeric_fixed
        if orderaddon.cost_type.name == "Food (Internal)":
            cost_food_internal += orderaddon.price_numeric_fixed
        elif orderaddon.cost_type.name == "Food (External)":
            cost_food_external += orderaddon.price_numeric_fixed
        elif orderaddon.cost_type.name == "Alcohol and NA Beverages":
            cost_beverage += orderaddon.price_numeric_fixed
        elif orderaddon.cost_type.name == "Labor":
            cost_labor += orderaddon.price_numeric_fixed
        elif orderaddon.cost_type.name == "Equipment and Rentals":
            cost_rentals += orderaddon.price_numeric_fixed

    # return total_estimated_cost
    return {
        "total_estimated_cost": total_estimated_cost,
        "cost_food_internal": cost_food_internal,
        "cost_food_external": cost_food_external,
        "cost_beverage": cost_beverage,
        "cost_labor": cost_labor,
        "cost_rentals": cost_rentals,
    }


def calculate_order_packages_cost(*, order: models.OrderBase, status: str) -> list:

    EASTERN_TZ = pytz.timezone("US/Eastern")
    packages_estimated_cost = []

    for idx, logistics in enumerate(order.logistics.is_active(), start=1):
        l_temp = {}

        l_temp["id"] = logistics.id
        formatted_start = (
            logistics.event_start.astimezone(EASTERN_TZ)
            .strftime("%I:%M %p")
            .lstrip("0")
            .replace(" 0", " ")
        )
        l_temp[
            "description"
        ] = f"Setup/Delivery {idx} at {formatted_start} for {logistics.guest_count} guests"

    packages = []

    for op in logistics.packages.is_active():
        temp = {}
        temp["id"] = op.id
        temp["name"] = op.package.name
        package_cost = calculate_package_cost(orderpackage=op, status="is_active")
        temp["cost"] = package_cost["cost"]
        temp["price_descriptive"] = package_cost["price_descriptive"]
        temp["guest_count"] = package_cost["guest_count"]
        temp["addons_staff"] = package_cost["addons_staff"]
        packages.append(temp)

    l_temp["packages"] = packages

    l_temp["addons_staff"] = calculate_logistics_cost(
        logistics=logistics, status="is_active"
    )

    packages_estimated_cost.append(l_temp)

    return packages_estimated_cost


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# EXPORT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

""" 
WeasyPrint currently (v.52.5, as of 2021-4-19) has not yet implemented CSS Grid  
- so the html template used for rendering for OrderDetails for export has been rewritten using tables
- there may be some inconsistencies in rendering, have to keep checking
"""


def order_generate_pdf(*, base_url: str, order_id: str) -> HttpResponse:
    # Retrieve/calculate context
    obj = models.OrderBase.objects.get(id=order_id)
    form = forms.OrderForm(instance=obj)
    options = common_services.get_page_context_options(models.OrderBase)

    total_estimated_cost = calculate_order_total_cost(order=obj, status="is_active")[
        "total_estimated_cost"
    ]

    packages_estimated_cost = calculate_order_packages_cost(
        order=obj, status="is_active"
    )

    if (
        obj.addons_staff.is_active()
        .filter(logistics__isnull=True, package__isnull=True)
        .count()
        > 0
    ):
        flag_order_addons = True
    else:
        flag_order_addons = False

    time_now_str = (
        timezone.now().astimezone(EASTERN_TZ).strftime("%A, %B %d, %Y at %I:%M %p")
    )
    printed_as_of = f"As of {time_now_str}"

    # Render PDF
    font_config = FontConfiguration()
    html_string = render_to_string(
        "order_detail_pdf.html",
        {
            "data": obj,
            "form": form,
            "options": options,
            "total_estimated_cost": total_estimated_cost,
            "packages_estimated_cost": packages_estimated_cost,
            "flag_order_addons": flag_order_addons,
            "printed_as_of": printed_as_of,
        },
    )
    html = HTML(string=html_string, base_url=base_url)
    result = html.write_pdf(font_config=font_config, presentational_hints=True)

    # Generate HTTP response
    invoice_number = obj.invoice_number
    event_date = obj.event_date.strftime("%Y-%m-%d")
    filename = f"{invoice_number}-{event_date}.pdf"

    response = HttpResponse(content_type="application/pdf;")
    response["Content-Transfer-Encoding"] = "binary"
    with NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, "rb")
        response.write(output.read())

    return (response, filename)
