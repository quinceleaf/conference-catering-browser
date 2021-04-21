# ––– DJANGO IMPORTS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
)


# ––– PYTHON UTILITY IMPORTS


# ––– THIRD-PARTY IMPORTS


# ––– APPLICATION IMPORTS
from apps.common import views as common_views, services as common_services
from apps.orders import filters, forms, models, services
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
# ORDERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def export_order_as_pdf(request, **kwargs):
    base_url = request.build_absolute_uri()
    order_id = kwargs["pk"]

    pdf_data = services.order_generate_pdf(base_url=base_url, order_id=order_id)
    response = pdf_data[0]

    return response


def export_orders_as_csv(request):
    pass


class OrderDetailView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    model = models.OrderBase
    form = forms.OrderForm
    template_name = "order_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(OrderDetailView, self).get_context_data(*args, **kwargs)
        obj = self.model.objects.get(id=self.kwargs["pk"])
        context["data"] = obj
        context["form"] = self.form(instance=obj)
        context["options"] = common_services.get_page_context_options(self.model)

        total_estimated_cost = services.calculate_order_total_cost(
            order=obj, status="is_active"
        )["total_estimated_cost"]
        context["total_estimated_cost"] = total_estimated_cost

        packages_estimated_cost = services.calculate_order_packages_cost(
            order=obj, status="is_active"
        )
        context["packages_estimated_cost"] = packages_estimated_cost

        if (
            obj.addons_staff.is_active()
            .filter(logistics__isnull=True, package__isnull=True)
            .count()
            > 0
        ):
            flag_order_addons = True
        else:
            flag_order_addons = False
        context["flag_order_addons"] = flag_order_addons

        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


class OrderFilterView(LoginRequiredMixin, common_views.GenericFilteredListView):
    model = models.OrderBase
    template_name = "order_filter_list.html"
    advanced_search_available = False
    bulk_create_available = False
    edit_via_xlsx = False
    filterset_class = filters.OrderFilterSimple

    def get_context_data(self, **kwargs):
        context = super(OrderFilterView, self).get_context_data(**kwargs)
        return context
