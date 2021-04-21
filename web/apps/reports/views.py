# ––– DJANGO IMPORTS
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import add_message
from django.core import serializers
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    TemplateView,
)


# ––– PYTHON UTILITY IMPORTS
import datetime as dt


# ––– THIRD-PARTY IMPORTS


# ––– APPLICATION IMPORTS
from apps.orders import models as orders_models
from apps.reports import forms, services
from apps.users import models as users_models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# INDEX
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# REPORT PARAMETERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


@login_required
def report_select_parameters(request, **kwargs):
    template_name = "report_parameters.html"
    form_class = forms.ReportForm

    form = form_class

    if request.method == "POST":
        print("request.POST:", request.POST)
        form = form_class(request.POST)
        request.session["report_params"] = request.POST
        return HttpResponseRedirect(reverse("apps.reports:reports_results"))

    return render(request, template_name, {"form": form})


@login_required
def report_render_results(request, **kwargs):
    template_name = "report_render.html"

    params = request.session["report_params"]

    if params:
        error_flag = False
        tenant_flag = None
        filter_conditions = []

        tenant_id = params.get("tenant", None)
        tenant_group_id = params.get("tenant_group", None)
        user_id = params.get("user", None)
        cost_type_id = params.get("cost_type", None)
        range_date = params.get("range_date", None)

        (
            orders,
            billing_records,
            summary,
            filter_condition_str,
            error_flag,
            tenant_flag,
        ) = services.filter_billing_records(
            tenant_id=tenant_id,
            tenant_group_id=tenant_group_id,
            user_id=user_id,
            cost_type_id=cost_type_id,
            range_date=range_date,
        )
        print("tenant_flag:", tenant_flag)
        add_message(
            request,
            messages.SUCCESS,
            f"Filtered for orders {filter_condition_str}",
        )

    else:
        error_flag = True
        tenant_flag = None
        billing_records = None
        summary = None
        add_message(
            request,
            messages.ERROR,
            f"Could not parse parameters provided",
        )

    return render(
        request,
        template_name,
        {
            "error_flag": error_flag,
            "tenant_flag": tenant_flag,
            "billing_records": billing_records,
            "summary": summary,
        },
    )


@login_required
def report_export_csv(request, **kwargs):
    params = request.session["report_params"]

    tenant_id = params.get("tenant", None)
    tenant_group_id = params.get("tenant_group", None)
    user_id = params.get("user", None)
    cost_type_id = params.get("cost_type", None)
    range_date = params.get("range_date", None)

    (
        orders,
        billing_records,
        summary,
        filter_condition_str,
        error_flag,
        tenant_flag,
    ) = services.filter_billing_records(
        tenant_id=tenant_id,
        tenant_group_id=tenant_group_id,
        user_id=user_id,
        cost_type_id=cost_type_id,
        range_date=range_date,
    )

    frames = orders_models.BillingRecord.frames.filter(order__in=orders)

    dataframe = services.generate_billing_records_dataframe(
        records=frames,
        filter_condition_str=filter_condition_str,
        tenant_flag=tenant_flag,
    )
    response = services.generate_billing_records_csv_from_dataframe(
        dataframe=dataframe, tenant_flag=tenant_flag
    )

    return response


@login_required
def report_export_xlsx(request, **kwargs):
    params = request.session["report_params"]

    tenant_id = params.get("tenant", None)
    tenant_group_id = params.get("tenant_group", None)
    user_id = params.get("user", None)
    cost_type_id = params.get("cost_type", None)
    range_date = params.get("range_date", None)

    (
        orders,
        billing_records,
        summary,
        filter_condition_str,
        error_flag,
        tenant_flag,
    ) = services.filter_billing_records(
        tenant_id=tenant_id,
        tenant_group_id=tenant_group_id,
        user_id=user_id,
        cost_type_id=cost_type_id,
        range_date=range_date,
    )

    frames = orders_models.BillingRecord.frames.filter(order__in=orders)

    dataframe = services.generate_billing_records_dataframe(
        records=frames,
        filter_condition_str=filter_condition_str,
        tenant_flag=tenant_flag,
    )
    response = services.generate_billing_records_xlsx_from_dataframe(
        dataframe=dataframe, tenant_flag=tenant_flag
    )

    return response
