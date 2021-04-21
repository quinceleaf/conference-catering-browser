# ––– DJANGO IMPORTS
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.db.models.enums import Choices
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver, Signal
from django.urls import reverse, reverse_lazy


# ––– PYTHON UTILITY IMPORTS
from decimal import Decimal as D


# –––THIRD-PARTY IMPORTS
from django_pandas.managers import DataFrameManager


# ––– APPLICATION IMPORTS
from apps.common import models as common_models
from apps.users import models as users_models


# ––– PARAMETERS


# ––– MODELS

"""
Settings
"""


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SETTINGS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class Settings(common_models.AbstractBaseModel):
    """ Reports settings """

    def __str__(self):
        return f"Settings for Reports app"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        permissions = [
            (
                "change_reports_settings",
                "Can change Reports settings",
            ),
        ]
        verbose_name_plural = "Settings"