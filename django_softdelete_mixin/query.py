from django import get_version
from django.db import transaction
from django.db.models.query import QuerySet

from .deletion import SoftDeleteCollector


class SoftDeleteQuerySetMixin:
    @transaction.atomic
    def delete(self, soft=True, only_self=False):
        if soft is False and only_self:
            raise ValueError("`soft` can't be False when `only_self` is True.")

        if soft:
            self._not_support_combined_queries("delete")
            if self.query.is_sliced:
                raise TypeError("Cannot use 'limit' or 'offset' with delete().")
            # https://github.com/django/django/commit/28e2077148f7602d29165e90965974698819cbba
            if (
                get_version() < "5.0" and self.query.distinct
            ) or self.query.distinct_fields:
                raise TypeError("Cannot call delete() after .distinct().")
            if self._fields is not None:
                raise TypeError(
                    "Cannot call delete() after .values() or .values_list()"
                )

            del_query = self._chain()
            collector = SoftDeleteCollector(using=del_query.db, origin=self)
            collector.collect(
                del_query,
                only_self=only_self,
            )
            deleted, _rows_count = collector.delete()
            self._result_cache = None
            return deleted, _rows_count
        else:
            return super().delete()


class SoftDeleteQuerySet(SoftDeleteQuerySetMixin, QuerySet):
    pass
