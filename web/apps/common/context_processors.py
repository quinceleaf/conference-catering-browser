# ––– DJANGO IMPORTS
from django.contrib import admin


"""
Menu links for header
"""


def app_header_links(requests):

    links = [
        {"route": "apps.orders:order_filter", "label": "Orders"},
        {"route": "apps.reports:reports_index", "label": "Reports"},
    ]
    return {"app_header_links": links}


def admin_app_list(requests):
    return {}