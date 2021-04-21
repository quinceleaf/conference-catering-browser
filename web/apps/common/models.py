# ––– DJANGO IMPORTS
from django.db import models
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy


# --- PYTHON UTILITY IMPORTS
import csv
import uuid


# ––– THIRD-PARTY IMPORTS


# ––– MODELS


class AbstractBaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, null=False, editable=False
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    def get_fields(self):
        return [
            (field.name, field.value_to_string(self))
            for field in self.__class__._meta.fields
        ]

    class Meta:
        abstract = True


class ImmutableBaseModel(models.Model):

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, null=False, editable=False
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    def get_fields(self):
        return [
            (field.name, field.value_to_string(self))
            for field in self.__class__._meta.fields
        ]

    class Meta:
        abstract = True


class SortableBaseModel(AbstractBaseModel):
    DEFAULT_SORT_ORDER = 1

    sort_order = models.PositiveSmallIntegerField(
        default=DEFAULT_SORT_ORDER, blank=True
    )
    flag_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Settings(AbstractBaseModel):
    def __str__(self):
        return f"Common app settings"

    class Meta:
        verbose_name_plural = "Settings"


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PLACEHOLDER
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Placeholder(AbstractBaseModel):

    CHOICES = [
        (1, "Choice 1"),
        (2, "Choice 2"),
    ]

    pass
