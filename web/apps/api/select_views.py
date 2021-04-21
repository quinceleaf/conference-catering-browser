# ––– DJANGO IMPORTS
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import timezone


# ––– PYTHON UTILITY IMPORTS
import datetime as dt
from decimal import Decimal
import json
import re


# ––– THIRD-PARTY IMPORTS
from rest_framework import (
    exceptions,
    generics,
    permissions,
    serializers,
    status,
    views,
    viewsets,
    filters,
)
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# ––– APPLICATION IMPORTS
from apps.api import serializers as api_serializers
from apps.common import models as common_models
from apps.orders import models as orders_models
from apps.users import models as users_models


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# ORDERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class CostTypeSelectAPIView(generics.ListAPIView):
    queryset = orders_models.CostType.objects.exclude(name="DEFAULT")
    serializer_class = api_serializers.CostTypeSelectSerializer

    def get(self, request, format=None):
        qs = orders_models.CostType.objects.exclude(name="DEFAULT")
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# USERS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class TenantSelectAPIView(generics.ListAPIView):
    queryset = users_models.Tenant.objects.all()
    serializer_class = api_serializers.TenantSelectSerializer

    def get(self, request, format=None):
        qs = users_models.Tenant.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class TenantGroupSelectAPIView(generics.ListAPIView):
    queryset = users_models.TenantGroup.objects.all()
    serializer_class = api_serializers.TenantGroupSelectSerializer

    def get(self, request, format=None):
        qs = users_models.TenantGroup.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(name__icontains=search_term)

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)


class UserSelectAPIView(generics.ListAPIView):
    queryset = users_models.User.objects.all()
    serializer_class = api_serializers.UserSelectSerializer

    def get(self, request, format=None):
        qs = users_models.User.objects.all()
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            qs = qs.filter(
                Q(first_name__icontains=search_term)
                | Q(last_name__icontains=search_term)
                | Q(email__icontains=search_term)
            )

        serializer_data = self.serializer_class(qs, many=True).data
        return JsonResponse({"results": serializer_data}, safe=False)
