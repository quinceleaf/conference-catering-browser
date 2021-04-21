# ––– DJANGO IMPORTS
from django import forms
from django.db.models import Q


# ––– THIRD-PARTY IMPORTS
from django_select2 import forms as s2forms


# ––– APPLICATION IMPORTS
from apps.common import models as common_models
from apps.common.forms import BaseModelForm
from apps.orders import models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# FORMS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class OrderForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.OrderBase
        fields = ("invoice_number",)
