from django.db import transaction
from django.db.models.query import QuerySet

from .deletion import SoftDeleteCollector


class SoftDeleteQuerySetMixin:
    @transaction.atomic
    def delete(self, soft=True):
        if soft:
            collector = SoftDeleteCollector(using=self.db)
            collector.collect(self)
            deleted, _rows_count = collector.delete()
            self._result_cache = None
            return deleted, _rows_count
        else:
            return super().delete()

class SoftDeleteQuerySet(SoftDeleteQuerySetMixin, QuerySet):
    pass
