from collections import Counter
from operator import attrgetter

from django.db import transaction
from django.db.models import signals, sql
from django.db.models.deletion import Collector
from django.utils import six


class SoftDeleteCollector(Collector):
    def related_objects(self, related, objs):
        return related.related_model.objects.using(self.using).filter(
            **{"%s__in" % related.field.name: objs}
        )
    
    def delete(self):
        for model, instances in self.data.items():
            self.data[model] = sorted(instances, key=attrgetter("pk"))
        self.sort()
        # number of objects deleted for each model label
        deleted_counter = Counter()

        with transaction.atomic(using=self.using, savepoint=False):
            for model, obj in self.instances_with_model():
                if not model._meta.auto_created:
                    signals.pre_delete.send(
                        sender=model, instance=obj, using=self.using
                    )

            # fast deletes
            for qs in self.fast_deletes:
                count = qs.update(is_deleted=True)
                deleted_counter[qs.model._meta.label] += count

            # update fields
            for model, instances_for_fieldvalues in six.iteritems(self.field_updates):
                for (field, value), instances in six.iteritems(instances_for_fieldvalues):
                    query = sql.UpdateQuery(model)
                    query.update_batch([obj.pk for obj in instances],
                                       {field.name: value}, self.using)

            # reverse instance collections
            for instances in six.itervalues(self.data):
                instances.reverse()

            # delete instances
            for model, instances in six.iteritems(self.data):
                query = sql.UpdateQuery(model)
                pk_list = [obj.pk for obj in instances]
                query.update_batch(pk_list, {'is_deleted':True},self.using)
                count = len(pk_list) # TODO:  update_batch method does not return count
                deleted_counter[model._meta.label] += count

                if not model._meta.auto_created:
                    for obj in instances:
                        signals.post_delete.send(
                            sender=model, instance=obj, using=self.using
                        )

        for model, instances_for_fieldvalues in six.iteritems(self.field_updates):
            for (field, value), instances in six.iteritems(instances_for_fieldvalues):
                for obj in instances:
                    setattr(obj, field.attname, value)
        for model, instances in six.iteritems(self.data):
            for instance in instances:
                setattr(instance, model._meta.pk.attname, None)
        return sum(deleted_counter.values()), dict(deleted_counter)
