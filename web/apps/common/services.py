def get_list_display_session_options(
    request, model, filter_by="ALL", order_by_field="name", page_size=10
):
    """ Returns list display options from session, or defaults if not yet set """
    return (
        request.session.get(
            f"display_filter_{model._meta.verbose_name.title()}", filter_by
        ),
        request.session.get(
            f"display_order_{model._meta.verbose_name.title()}", order_by_field
        ),
        request.session.get(
            f"display_page_size_{model._meta.verbose_name.title()}", page_size
        ),
    )


def get_page_context_options(model, bulk_create_available=False, edit_via_xlsx=False):
    """ Returns parameters for rendering model templates  """
    options = {
        "model": f"{model._meta.verbose_name.title()}",
        "plural": f"{model._meta.verbose_name_plural.title()}",
        "url_add": f"apps.{model._meta.app_label}:{model._meta.model_name}_add",
        "url_list": f"apps.{model._meta.app_label}:{model._meta.model_name}_list",
        "url_detail": f"apps.{model._meta.app_label}:{model._meta.model_name}_detail",
        "url_edit": f"apps.{model._meta.app_label}:{model._meta.model_name}_edit",
    }
    if bulk_create_available:
        options[
            "url_add_bulk"
        ] = f"apps.{model._meta.app_label}:{model._meta.model_name}_add_bulk"

    if edit_via_xlsx:
        options[
            "url_edit_via_xlsx"
        ] = f"apps.{model._meta.app_label}:{model._meta.model_name}_edit_via_xlsx"

    return options
