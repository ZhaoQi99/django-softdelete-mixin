from django.db import models, router, transaction

from .constant import UN_DELETE
from .deletion import SoftDeleteCollector
from .manger import SoftDeleteManager


class SoftDeleteModel(models.Model):
    deleted = models.CharField("是否删除", default=UN_DELETE, max_length=30, db_index=True)
    objects = SoftDeleteManager()
    src_objects = models.Manager()

    @transaction.atomic
    def delete(self, using=None, keep_parents=False, soft=True, only_self=False):
        if soft is False and only_self:
            raise ValueError("`soft` can't be False when `only_self` is True.")

        if soft:
            using = using or router.db_for_write(self.__class__, instance=self)
            assert self._get_pk_val() is not None, (
                "%s object can't be deleted because its %s attribute is set to None."
                % (self._meta.object_name, self._meta.pk.attname)
            )

            collector = SoftDeleteCollector(using=using)
            collector.collect([self], keep_parents=keep_parents, only_self=only_self)
            return collector.delete()
        else:
            return super().delete(using, keep_parents)

    class Meta:
        abstract = True
        default_manager_name = "objects"


class BaseModel(SoftDeleteModel):
    create_at = models.DateTimeField("创建时间", auto_now_add=True)
    update_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True
        default_manager_name = "objects"
