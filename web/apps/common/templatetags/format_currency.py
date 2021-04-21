# ––– DJANGO IMPORTS
from django import template

register = template.Library()


@register.filter(name="format_currency")
def format_currency(value):
    prefix = "$ "
    if type(value) == "str":
        value = float(value)
    try:
        return "{}{:,.2f}".format(prefix, value)
    except:
        return value
