from collections import Counter
from functools import reduce
from operator import attrgetter, or_

from django import get_version
from django.db import models, transaction
from django.db.models import query_utils, signals, sql
from django.db.models.deletion import Collector

from .utils import random_datetime


class SoftDeleteCollector(Collector):
    def related_objects(self, related_model, related_fields, objs):
        """
        Get a QuerySet of the related model to objs via related fields.
        """
        predicate = query_utils.Q.create(
            [(f"{related_field.name}__in", objs) for related_field in related_fields],
            connector=query_utils.Q.OR,
        )
        return related_model.objects.using(self.using).filter(predicate)

    def delete(self):
        deleted_time = random_datetime()

        # sort instance collections
        for model, instances in self.data.items():
            self.data[model] = sorted(instances, key=attrgetter("pk"))

        # if possible, bring the models in an order suitable for databases that
        # don't support transactions or cannot defer constraint checks until the
        # end of a transaction.
        self.sort()
        # number of objects deleted for each model label
        deleted_counter = Counter()

        # Optimize for the case with a single obj and no dependencies
        if len(self.data) == 1 and len(instances) == 1:
            instance = list(instances)[0]
            if self.can_fast_delete(instance):
                with transaction.mark_for_rollback_on_error(self.using):
                    sql.UpdateQuery(model).update_batch(
                        [instance.pk], {"deleted": deleted_time}, self.using
                    )
                    count = 1  # TODO:  update_batch method does not return count
                setattr(instance, model._meta.pk.attname, None)
                return count, {model._meta.label: count}

        with transaction.atomic(using=self.using, savepoint=False):
            # send pre_delete signals
            for model, obj in self.instances_with_model():
                if not model._meta.auto_created:
                    signals.pre_delete.send(
                        sender=model,
                        instance=obj,
                        using=self.using,
                        origin=self.origin,
                    )

            # fast deletes
            for qs in self.fast_deletes:
                count = qs.using(self.using).update(deleted=deleted_time)
                if count:
                    deleted_counter[qs.model._meta.label] += count

            # update fields
            if get_version() >= "4.2":
                # https://github.com/django/django/commit/0701bb8e1f1771b36cdde45602ad377007e372b3
                for (field, value), instances_list in self.field_updates.items():
                    updates = []
                    objs = []
                    for instances in instances_list:
                        if (
                            isinstance(instances, models.QuerySet)
                            and instances._result_cache is None
                        ):
                            updates.append(instances)
                        else:
                            objs.extend(instances)
                    if updates:
                        combined_updates = reduce(or_, updates)
                        combined_updates.update(**{field.name: value})
                    if objs:
                        model = objs[0].__class__
                        query = sql.UpdateQuery(model)
                        query.update_batch(
                            list({obj.pk for obj in objs}), {field.name: value}, self.using
                        )
            else:
                for model, instances_for_fieldvalues in self.field_updates.items():
                    for (field, value), instances in instances_for_fieldvalues.items():
                        query = sql.UpdateQuery(model)
                        query.update_batch(
                            [obj.pk for obj in instances],
                            {field.name: value},
                            self.using,
                        )

            # reverse instance collections
            for instances in self.data.values():
                instances.reverse()

            # delete instances
            for model, instances in self.data.items():
                query = sql.UpdateQuery(model)
                pk_list = [obj.pk for obj in instances]
                query.update_batch(pk_list, {"deleted": deleted_time}, self.using)
                count = len(pk_list)  # TODO:  update_batch method does not return count
                if count:
                    deleted_counter[model._meta.label] += count

                if not model._meta.auto_created:
                    for obj in instances:
                        signals.post_delete.send(
                            sender=model,
                            instance=obj,
                            using=self.using,
                            origin=self.origin,
                        )

        for model, instances in self.data.items():
            for instance in instances:
                setattr(instance, model._meta.pk.attname, None)
        return sum(deleted_counter.values()), dict(deleted_counter)

    def collect(self, objs, only_self=False, **kwargs) -> None:
        if only_self:
            if isinstance(objs, list):
                model = objs[0].__class__
                self.data[model].update(objs)
            else:
                self.fast_deletes.append(objs)
            return
        super().collect(objs, **kwargs)
