# ––– DJANGO IMPORTS
from django.db.models import Model, Q, QuerySet, Sum
from django.http import HttpResponse


# ––– PYTHON UTILITY IMPORTS
from copy import copy
import csv
import datetime
import datetime as dt
import decimal
from decimal import Decimal as D
from io import BytesIO as IO
import json
import re
from tempfile import NamedTemporaryFile
from typing import Tuple


# ––– THIRD-PARTY IMPORTS
import pandas
import pandas as pd
import xlsxwriter


# ––– APPLICATION IMPORTS
from apps.orders import models as orders_models
from apps.users import models as users_models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# REPORTS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def filter_billing_records(
    *,
    tenant_id: str = None,
    tenant_group_id: str = None,
    user_id: str = None,
    cost_type_id: str = None,
    range_date: str = None,
) -> Tuple[
    QuerySet[orders_models.OrderBase],
    QuerySet[orders_models.BillingRecord],
    dict,
    str,
    str,
    str,
]:

    error_flag = None
    tenant_flag = None
    filter_conditions = []

    # convert range_date str to datetime
    if range_date:
        range_date_start, range_date_end = range_date.split(" to ")
        range_date_start = dt.datetime.strptime(range_date_start, "%Y-%m-%d")
        range_date_end = dt.datetime.strptime(range_date_end, "%Y-%m-%d")

    # define base queryset
    qs = orders_models.OrderBase.objects.is_active().filter(
        Q(status__status="CONFIRMED") | Q(status__status="CHANGE_REQUEST")
    )

    # filter based on tenant, tenant group or user (mutually-exclusive)
    if any([tenant_id, tenant_group_id, user_id]):
        if tenant_id:
            qs = qs.filter(customer__tenant=tenant_id)
            tenant = users_models.Tenant.objects.get(id=tenant_id)
            if re.search("University", tenant.name):
                tenant_flag = "university"
            filter_conditions.append(
                f"placed by customers at <strong>{tenant.name}</strong>"
            )
        elif tenant_group_id:
            qs = qs.filter(customer__tenant__groups__in=[tenant_group_id])
            tenant_group = users_models.TenantGroup.objects.get(id=tenant_group_id)
            filter_conditions.append(
                f"placed by customers of tenants within <strong>{tenant_group.name}</strong>"
            )
        elif user_id:
            qs = qs.filter(customer=user_id)
            user = users_models.User.objects.get(id=user_id)
            if re.search("University", user.tenant.name):
                tenant_flag = "university"
            filter_conditions.append(
                f"placed by customer <strong>{user.get_full_name}</strong>"
            )

    # filter based on date
    if range_date:
        qs = qs.filter(event_date__gte=range_date_start, event_date__lte=range_date_end)
        if range_date_start.year == range_date_end.year:
            filter_conditions.append(
                f"between <strong>{range_date_start.strftime('%B %d')} and {range_date_end.strftime('%B %d, %Y')}</strong>"
            )
        else:
            filter_conditions.append(
                f"between <strong>{range_date_start.strftime('%B %d, %Y')} and {range_date_end.strftime('%B %d, %Y')}</strong>"
            )

    # filter based on cost type
    if cost_type_id:
        cost_type = orders_models.CostType.objects.get(id=cost_type_id)
        if cost_type.name == "Food (Internal)":
            qs = qs.filter(billing_record__food_internal__gt=0)
        if cost_type.name == "Food (External)":
            qs = qs.filter(billing_record__food_external__gt=0)
        if cost_type.name == "Alcohol and NA Beverages":
            qs = qs.filter(billing_record__alcohol_beverages__gt=0)
        if cost_type.name == "Labor":
            qs = qs.filter(billing_record__labor__gt=0)
        if cost_type.name == "Rentals":
            qs = qs.filter(billing_record__rentals__gt=0)
        filter_conditions.append(
            f"including charges of cost type <strong>{cost_type.name}</strong>"
        )

    # select billing records for orders matching filter
    billing_records = (
        orders_models.BillingRecord.objects.filter(order__in=qs)
        .select_related("order")
        .only("order__customer")
    )

    # calculate summary of costs for filtered billing records
    summary = billing_records.aggregate(
        Sum("total_cost"),
        Sum("food_internal"),
        Sum("food_external"),
        Sum("alcohol_beverages"),
        Sum("labor"),
        Sum("rentals"),
    )

    # generate message string based on parameters provided
    filter_condition_str = ""
    for idx, condition in enumerate(filter_conditions):
        if idx == len(filter_conditions) - 1:
            filter_condition_str += f"{condition}"
        else:
            filter_condition_str += f"{condition}, "

    return (qs, billing_records, summary, filter_condition_str, error_flag, tenant_flag)


COLUMNS_GENERAL = [
    "Event Date",
    "Inv. Number",
    "Payment Ref.",
    "Customer",
    "Total Charges",
    "Food (Int.)",
    "Food (Ext.)",
    "Alcohol/Beverage",
    "Labor",
    "Rentals",
]


COLUMNS_UNIVERSITY = [
    "Event Date",
    "Inv. Number",
    "Project",
    "Task",
    "Award",
    "Expenditure",
    "Organization",
    "Customer",
    "Total Charges",
    "Food (Int.)",
    "Food (Ext.)",
    "Alcohol/Beverage",
    "Labor",
    "Rentals",
]


COLUMNS_MAPPING = {
    "order__invoice_number": "Inv. Number",
    "payment_reference": "Payment Ref.",
    "project": "Project",
    "task": "Task",
    "award": "Award",
    "expenditure": "Expenditure",
    "organization": "Organization",
    "customer": "Customer",
    "event_date": "Event Date",
    "total_cost": "Total Charges",
    "food_internal": "Food (Int.)",
    "food_external": "Food (Ext.)",
    "alcohol_beverages": "Alcohol/Beverage",
    "labor": "Labor",
    "rentals": "Rentals",
}


FIELDS = [
    "order__invoice_number",
    "payment_reference",
    "order__customer__first_name",
    "order__customer__last_name",
    "event_date",
    "total_cost",
    "food_internal",
    "food_external",
    "alcohol_beverages",
    "labor",
    "rentals",
]


def combine_and_drop_customer(*, dataframe: pandas.DataFrame) -> pandas.DataFrame:
    dataframe["customer"] = (
        dataframe["order__customer__first_name"]
        + " "
        + dataframe["order__customer__last_name"]
    )
    dataframe.drop(
        columns=[
            "order__customer__first_name",
            "order__customer__last_name",
        ],
        inplace=True,
    )
    return dataframe


def expand_ptaeo(*, dataframe: pandas.DataFrame) -> pandas.DataFrame:
    dataframe["Project"] = (
        dataframe["Payment Ref."].apply(lambda row: row.split("-")[0]).astype(str)
    )
    dataframe["Task"] = (
        dataframe["Payment Ref."].apply(lambda row: row.split("-")[1]).astype(str)
    )
    dataframe["Award"] = (
        dataframe["Payment Ref."].apply(lambda row: row.split("-")[2]).astype(str)
    )
    dataframe["Expenditure"] = (
        dataframe["Payment Ref."].apply(lambda row: row.split("-")[3]).astype(str)
    )
    dataframe["Organization"] = (
        dataframe["Payment Ref."].apply(lambda row: row.split("-")[4]).astype(str)
    )
    dataframe.drop(columns="Payment Ref.", inplace=True)

    return dataframe


def generate_billing_records_dataframe(
    *,
    records: QuerySet[orders_models.BillingRecord],
    filter_condition_str: str,
    tenant_flag: str,
) -> pandas.DataFrame:
    if tenant_flag == "university":
        columns = COLUMNS_UNIVERSITY
    else:
        columns = COLUMNS_GENERAL
    base_row = dict.fromkeys(columns, "")

    df = records.to_dataframe(fieldnames=FIELDS, verbose=True)
    df = combine_and_drop_customer(dataframe=df)
    df.rename(columns=COLUMNS_MAPPING, inplace=True)
    if tenant_flag == "university":
        df = expand_ptaeo(dataframe=df)
    df = df[columns]
    df_concat = []
    counter_rows = 0

    filter_condition_clean = re.sub("<[^<]+?>", "", filter_condition_str)
    billing_heading = f"Orders - {filter_condition_clean}"

    top_row = copy(base_row)
    top_row["Event Date"] = billing_heading

    heading_row = zip(columns, columns)
    heading_row = dict(heading_row)

    empty_row = copy(base_row)

    no_orders_row = copy(base_row)
    no_orders_row["Event Date"] = "NO ORDERS"

    df_top = pd.DataFrame(top_row, index=[counter_rows], columns=columns)
    df_concat.append(df_top)
    counter_rows += 1

    df_empty = pd.DataFrame(empty_row, index=[counter_rows], columns=columns)
    df_concat.append(df_empty)
    counter_rows += 1

    df_heading = pd.DataFrame(heading_row, index=[counter_rows], columns=columns)
    df_concat.append(df_heading)
    counter_rows += 1

    df_concat.append(df)

    df_complete = pd.concat(df_concat)

    return df_complete


def generate_billing_records_xlsx_from_dataframe(
    *, dataframe: pandas.DataFrame, tenant_flag: str
) -> HttpResponse:
    xlsx_stream = IO()
    writer = pd.ExcelWriter(
        xlsx_stream,
        engine="xlsxwriter",
        options={"remove_timezone": True, "strings_to_numbers": True},
    )

    workbook = writer.book

    dataframe.to_excel(writer, sheet_name="Orders", index=False, header=False)

    # XLSX FORMATTING STEPS
    basic_format = workbook.add_format(
        {
            "num_format": "General",
            "font_size": 14,
            "align": "left",
        }
    )

    centered_format = workbook.add_format(
        {
            "font_size": 14,
            "align": "center",
        }
    )

    numeric_format = workbook.add_format(
        {
            "num_format": "#,##0.00",
            "font_size": 14,
            "align": "right",
        }
    )

    currency_format = workbook.add_format(
        {
            # "num_format": "$#,##0.00",
            "num_format": '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)',
            "font_size": 14,
            "align": "right",
        }
    )

    title_format = workbook.add_format(
        {
            "font_size": 18,
            "bold": "True",
            "align": "left",
        }
    )

    header_format = workbook.add_format(
        {
            "bold": "True",
            "font_size": 14,
        }
    )

    total_row_numeric_format = workbook.add_format(
        {
            "bold": "True",
            "top": 1,
            "num_format": "#,##0.00",
            "font_size": 14,
            "align": "right",
        }
    )

    ws_c = writer.sheets["Orders"]

    if tenant_flag == "university":
        # Event Date, Invoice number, Project
        ws_c.set_column("A:C", 15, basic_format)

        # Task
        ws_c.set_column("D:D", 6, basic_format)

        # Award, Expenditure, Organization
        ws_c.set_column("E:G", 15, basic_format)

        # Customer
        ws_c.set_column("H:H", 25, basic_format)

        # Total Charges, Food (Internal), Food (External), Alcohol/Bev, Labor, Rentals
        ws_c.set_column("I:N", 15, currency_format)

    else:
        # Event Date, Invoice number
        ws_c.set_column("A:B", 15, basic_format)

        # Payment reference
        ws_c.set_column("C:C", 35, basic_format)

        # Customer
        ws_c.set_column("D:D", 25, basic_format)

        # Total Charges, Food (Internal), Food (External), Alcohol/Bev, Labor, Rentals
        ws_c.set_column("E:J", 15, currency_format)

    ws_c.set_row(2, 19, header_format)
    ws_c.set_row(0, 24, title_format)

    writer.save()
    # writer.close()

    xlsx_stream.seek(0)
    xlsx_file = f"orders.xlsx"
    response = HttpResponse(
        xlsx_stream.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="' + xlsx_file

    xlsx_stream.close()
    # writer.close()
    return response


def generate_billing_records_csv_from_dataframe(
    *, dataframe: pandas.DataFrame, tenant_flag: str
) -> HttpResponse:

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=orders.csv"
    dataframe.to_csv(
        path_or_buf=response,
        header=False,
        index=False,
        quoting=csv.QUOTE_ALL,
        float_format="%.2f",
    )

    return response