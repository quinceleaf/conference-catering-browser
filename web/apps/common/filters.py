# ––– DJANGO IMPORTS
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


# ––– PYTHON UTILITY IMPORTS
import datetime as dt


# ––– THIRD-PARTY IMPORTS
import django_filters


# ––– APPLICATION IMPORTS
from apps.common import models


class OrderDateRangeFilter(django_filters.DateRangeFilter):
    """ Customize default backwards-looking ranges """

    choices = [
        ("past_current_year", _(f"YTD ({now().year})")),
        ("past_years_plus_1", _(f"{now().year - 1}")),
        ("past_years_plus_2", _(f"{now().year - 2}")),
        ("past_years_plus_3", _(f"{now().year - 3}")),
    ]

    filters = {
        "past_current_year": lambda qs, name: qs.filter(
            **{
                "%s__year" % name: now().year,
                "%s__lt" % name: now(),
            }
        ),
        "past_years_plus_1": lambda qs, name: qs.filter(
            **{
                "%s__year" % name: now().year - 1,
            }
        ),
        "past_years_plus_2": lambda qs, name: qs.filter(
            **{
                "%s__year" % name: now().year - 2,
            }
        ),
        "past_years_plus_3": lambda qs, name: qs.filter(
            **{
                "%s__year" % name: now().year - 3,
            }
        ),
    }
