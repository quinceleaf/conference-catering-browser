# ––– DJANGO IMPORTS
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


# ––– APPLICATION IMPORTS
from apps.common import views as common_views
from apps.orders import views


app_name = "apps.orders"


urlpatterns = [
    path(
        "<uuid:pk>/",
        views.OrderDetailView.as_view(),
        name="order_detail",
    ),
    path(
        "export/pdf/<uuid:pk>/",
        views.export_order_as_pdf,
        name="export_as_pdf",
    ),
    path(
        "export/csv/",
        views.export_orders_as_csv,
        name="export_as_csv",
    ),
    path(
        "",
        views.OrderFilterView.as_view(),
        name="order_filter",
    ),
]
