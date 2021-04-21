# ––– DJANGO IMPORTS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.views.generic import (
    TemplateView,
)


# ––– PYTHON UTILITY IMPORTS


# ––– THIRD-PARTY IMPORTS
from django_filters.views import FilterView


# ––– APPLICATION IMPORTS
from apps.common import filters, forms, models, services


"""
Views for:
Generic Base Views

"""

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
# GENERIC VIEWS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class GenericFilteredListView(FilterView):
    """
    Must override for each view:
    - model

    Override as needed for each view:
    - template_name
    - exclude_by_field
    - exclude_by_value
    - order_field
    - filterset_class
    """

    model = models.Placeholder
    template_name = "generic_filter_list.html"

    exclude_by_field = None
    exclude_by_value = ""
    advanced_search_available = True
    bulk_create_available = False
    edit_via_xlsx = False

    # display session options
    order_by_field = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get naming and url options for list
        context["options"] = services.get_page_context_options(
            self.model, self.bulk_create_available, self.edit_via_xlsx
        )

        # get filtering, ordering and page size options for list
        (
            filter_by_value,
            order_by_field,
            page_size,
        ) = services.get_list_display_session_options(
            self.request, self.model, order_by_field=self.order_by_field
        )

        context["filterset"] = self.filterset
        context["filter_applied"] = any(
            field in self.request.GET for field in set(self.filterset.get_fields())
        )

        # pagination
        paginator = Paginator(
            self.filterset.qs,
            page_size,
            orphans=round(page_size / 3, 0),
        )
        page = self.request.GET.get("page", 1)
        try:
            data = paginator.get_page(page)
        except PageNotAnInteger:
            data = paginator.get_page(1)
        except EmptyPage:
            data = paginator.get_page(paginator.num_pages)
        context["data"] = data

        return context
