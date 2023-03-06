from django.db import models

from .constant import UN_DELETE
from .query import SoftDeleteQuerySet


class SoftDeleteManagerMixin:
    _queryset_class = SoftDeleteQuerySet

    def get_queryset(self):
        return super().get_queryset().filter(deleted=UN_DELETE)


class SoftDeleteManager(SoftDeleteManagerMixin, models.Manager):
    pass
