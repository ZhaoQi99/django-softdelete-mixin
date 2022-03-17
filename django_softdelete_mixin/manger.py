from django.db import models

from .query import SoftDeleteQuerySet


class SoftDeleteManagerMixin:
    _queryset_class = SoftDeleteQuerySet

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteManager(SoftDeleteManagerMixin, models.Manager):
    pass
