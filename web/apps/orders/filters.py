# ––– DJANGO IMPORTS
from django.db.models import Q


# ––– THIRD-PARTY IMPORTS
import django_filters


# ––– APPLICATION IMPORTS
from apps.common import filters as common_filters
from apps.orders import models
from apps.users import models as users_models


class OrderFilterSimple(django_filters.FilterSet):

    invoice_number = django_filters.CharFilter(lookup_expr="icontains", distinct=True)

    event_date = common_filters.OrderDateRangeFilter()

    @property
    def qs(self):
        orders = super().qs
        return orders.filter(
            Q(status__status="CONFIRMED") | Q(status__status="CHANGE_REQUEST")
        )

    class Meta:
        model = models.OrderBase
        fields = ["invoice_number", "customer__tenant", "event_date"]
