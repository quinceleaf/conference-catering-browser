# ––– DJANGO IMPORTS
from django import template


# ––– APPLICATION IMPORTS
from apps.orders.models import MenuItem, Package


register = template.Library()


@register.filter(name="included_in_package")
def included_in_package(id, package_id):

    mi = MenuItem.objects.get(id=id)
    p = Package.objects.get(id=package_id)
    m2m_set = p.menu_items_included.all()
    if m2m_set:
        return True if mi in m2m_set else False
