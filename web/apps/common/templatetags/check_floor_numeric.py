# ––– DJANGO IMPORTS
from django import template
from django.template.defaultfilters import stringfilter


# ––– PYTHON UTILITY IMPORTS
from re import sub

register = template.Library()


@register.filter(name="check_floor_numeric")
@stringfilter
def check_floor_numeric(value):

    try:
        k = int(value)
        return True
    except ValueError:
        return False
