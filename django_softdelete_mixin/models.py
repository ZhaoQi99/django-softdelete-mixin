from django.db import models, router, transaction

from .deletion import SoftDeleteCollector
from .manger import SoftDeleteManager


class SoftDeleteModelMixin(models.Model):
    is_deleted = models.BooleanField('是否删除', default=False)
    objects = SoftDeleteManager()
    src_objects = models.Manager()

    @transaction.atomic
    def delete(self, using=None, keep_parents=False, soft=True):
        if soft:
            using = using or router.db_for_write(self.__class__, instance=self)
            assert self._get_pk_val() is not None, (
                "%s object can't be deleted because its %s attribute is set to None." %
                (self._meta.object_name, self._meta.pk.attname)
            )

            collector = SoftDeleteCollector(using=using)
            collector.collect([self], keep_parents=keep_parents)
            return collector.delete()
        else:
            return super().delete(using, keep_parents)

    class Meta:
        abstract = True

class BaseModel(SoftDeleteModelMixin):
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    update_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True
