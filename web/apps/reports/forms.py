# ––– DJANGO IMPORTS
from django import forms
from django.db.models import Q


# ––– THIRD-PARTY IMPORTS
from django_select2 import forms as s2forms


# ––– APPLICATION IMPORTS
from apps.api import select_views
from apps.common import models as common_models
from apps.common.forms import BaseModelForm
from apps.orders import models as orders_models
from apps.reports import models
from apps.users import models as users_models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# WIDGETS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class CostTypeWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.CostTypeSelectAPIView
    search_fields = ["name__icontains"]


class TenantWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.TenantSelectAPIView
    search_fields = ["name__icontains"]


class TenantGroupWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.TenantGroupSelectAPIView
    search_fields = ["name__icontains"]


class UserWidget(s2forms.ModelSelect2Widget):
    data_view = select_views.UserSelectAPIView
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "email__icontains",
    ]


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# FORMS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class ReportForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(ReportForm, self).__init__(*args, **kwargs)

    cost_type = forms.ModelChoiceField(
        queryset=orders_models.CostType.objects.exclude(name="DEFAULT"),
        required=False,
        label=u"Cost Type",
    )

    tenant_group = forms.ModelChoiceField(
        queryset=users_models.TenantGroup.objects.all(),
        required=False,
        label=u"Tenant Group",
    )

    tenant = forms.ModelChoiceField(
        queryset=users_models.Tenant.objects.all(),
        required=False,
        label=u"Tenant",
    )

    user = forms.ModelChoiceField(
        queryset=users_models.User.objects.all(),
        required=False,
        label=u"User",
    )

    range_date = forms.CharField(max_length=32)

    class Meta:
        fields = (
            "cost_type",
            "tenant",
            "tenant_group",
            "user",
            "range_date",
        )
        widgets = {
            "cost_type": CostTypeWidget,
            "tenant": TenantWidget,
            "tenant_group": TenantGroupWidget,
            "user": UserWidget,
        }
