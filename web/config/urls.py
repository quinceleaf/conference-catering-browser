""" ConferenceCateringBrowser URL Configuration """

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("gearbox/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("select2/", include("django_select2.urls")),
    path("orders/", include("apps.orders.urls", namespace="apps.orders")),
    path("reports/", include("apps.reports.urls", namespace="apps.reports")),
    path("", include("apps.common.urls", namespace="apps.common")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "ConferenceCateringBrowser Administration"
admin.site.site_title = "ConferenceCateringBrowser Administration"
admin.site.index_title = "ConferenceCateringBrowser Administration"
