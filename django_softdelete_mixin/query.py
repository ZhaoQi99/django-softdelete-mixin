from django.db import transaction
from django.db.models.query import QuerySet

from .deletion import SoftDeleteCollector


class SoftDeleteQuerySetMixin:
    @transaction.atomic
    def delete(self, soft=True):
        if soft:
            self._not_support_combined_queries("delete")
            if self.query.is_sliced:
                raise TypeError("Cannot use 'limit' or 'offset' with delete().")
            if self.query.distinct or self.query.distinct_fields:
                raise TypeError("Cannot call delete() after .distinct().")
            if self._fields is not None:
                raise TypeError(
                    "Cannot call delete() after .values() or .values_list()"
                )

            del_query = self._chain()
            collector = SoftDeleteCollector(using=del_query.db, origin=self)
            collector.collect(del_query)
            deleted, _rows_count = collector.delete()
            self._result_cache = None
            return deleted, _rows_count
        else:
            return super().delete()

class SoftDeleteQuerySet(SoftDeleteQuerySetMixin, QuerySet):
    pass
