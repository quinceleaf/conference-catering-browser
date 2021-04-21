# ––– DJANGO IMPORTS
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, register_converter


# ––– APPLICATION IMPORTS
from apps.common import views as common_views
from apps.reports import views


app_name = "apps.reports"


urlpatterns = [
    path("export/csv/", views.report_export_csv, name="reports_export_csv"),
    path("export/xlsx/", views.report_export_xlsx, name="reports_export_xlsx"),
    path("results/", views.report_render_results, name="reports_results"),
    path("", views.report_select_parameters, name="reports_index"),
]
