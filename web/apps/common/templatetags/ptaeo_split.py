# ––– DJANGO IMPORTS
from django import template

register = template.Library()


@register.filter(name="ptaeo_split")
def ptaeo_split(ptaeo_str, element_name):

    ptaeo_items = ptaeo_str.split("-")
    if element_name == "project":
        element = ptaeo_items[0].strip()

    if element_name == "task":
        element = ptaeo_items[1].strip()

    if element_name == "award":
        element = ptaeo_items[2].strip()

    if element_name == "expenditure":
        element = ptaeo_items[3].strip()

    if element_name == "organization":
        element = ptaeo_items[4].strip()

    return element
