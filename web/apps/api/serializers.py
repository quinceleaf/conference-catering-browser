# ––– DJANGO IMPORTS


# ––– PYTHON UTILITY IMPORTS


# ––– THIRD-PARTY IMPORTS
from rest_framework import generics, permissions, serializers


# ––– APPLICATION IMPORTS
from apps.common import models as common_models
from apps.orders import models as orders_models
from apps.users import models as users_models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ORDERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class CostTypeSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = orders_models.CostType


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# USERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class TenantSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = users_models.Tenant


class TenantGroupSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="name")

    class Meta:
        model = users_models.TenantGroup


class UserSelectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    text = serializers.CharField(source="get_full_name")

    class Meta:
        model = users_models.User
