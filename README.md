# Django Softdelete Mixin
## What is it
django-softdelete-mixin is a simple Django package that contains some mixins which implement soft delete for Django ORM.

## Requirements
* Python 3.6+
* Django 3.1+ (`related_objects` function has break changes in [django/django@26c66f45](https://github.com/django/django/commit/26c66f45193fa65125ca06328817927d6bbc2b22))

## Installation
Install from github.
```bash
pip install git+https://github.com/ZhaoQi99/django-softdelete-mixin.git
✨🍰✨
```
## Quick example
```python
from django_softdelete_mixin.models import SoftDeleteModel

class Article(SoftDeleteModel):
    title = models.CharField(max_length=100)

# Example of use
>>> a1 = Article.objects.create(title='django')
>>> a2 = Article.objects.create(title='python')

# soft deletion of object
>>> a1.delete()  
>>> Article.objects.count()
1
>>> Article.objects.filter(title='python').delete()
>>> Article.objects.count()
0

# Django default manager
>>> Article.src_objects.count()
2

# hard deletion of object
>>> a1.delete(soft=False)  
>>> Article.objects.all().delete(soft=False)
```

## Usage
### Model
Use the abstract model `SoftDeleteModel` for adding one field:
* deleted - is a CharField, shows weather of a deletion state of object

Use the abstract model `BaseModel` for adding another two fields in addition to `is_deleted`:
* create_at - is a DateTimeField, shows the time of creation of object
* update_at - is a DateTimeField, shows the time of last update of object

```python
from django_softdelete_mixin.models import SoftDeleteModel, BaseModel

class YourModel(SoftDeleteModel):
    pass

class YourModel(BaseModel):
    pass
```
### QuerySet

* `ModelName.objects.all()` - returns all objects except deleted ones
* `ModelName.src_objects.all()` - returns all objects 

### Delete

* `ModelName.objects.all().delete()` - soft delete all objects
* `ModelName.objects.all().delete(soft=False)` - hard delete all objects
* `Model.src_objects.delete()` - hard delete all objects(including soft deleted)

### Mixins
```python
from django_softdelete_mixin.mixins import SoftDeleteManagerMixin,SoftDeleteQuerySetMixin

# For inherited model
class YourOwnManager(SoftDeleteManagerMixin, SomeParentManagerClass):
    pass

class YourOwnQuerySet(SoftDeleteQuerySetMixin, SomeParentQuerySetClass):
    pass
```

### Unique

```python
class Test(BaseModel):
    name = models.CharField(max_length=100)
    class Meta:
        unique_together = (
            ('name', 'deleted'),
        )

```

In [Django REST framework](https://www.django-rest-framework.org/):

```python
from django_softdelete_mixin.constant import UN_DELETE

class TestSerializer(serializers.ModelSerializer):
    deleted = serializers.HiddenField(default=UN_DELETE)

    class Meta:
        model = Test
        fields = "__all__"
        extra_kwargs = {
            "deleted": {"write_only": True},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Test.objects.all(),
                fields=("name", "deleted"),
                message="XXX已存在"
            )
        ]
```

### Custom

#### QuerySet

```python
from django_softdelete_mixin.query import SoftDeleteQuerySet

class YourOwnQuerySet(SoftDeleteQuerySet):
    pass
```
#### Manager
```python
from django_softdelete_mixin.manager import SoftDeleteManager

class YourOwnManager(SoftDeleteManager):
    pass
```

## Bug

### Querying in the opposite direction using ForeignKey

Use the following solutions to solve:

```python
from django_softdelete_mixin.constant import UN_DELETE
role = Role.objects.first()
role.user_set.filter(role_user__deleted=UN_DELETE)
```

## License

[GNU General Public License v3.0](https://github.com/ZhaoQi99/django-softdelete-mixin/blob/main/LICENSE)
## Author
* Qi Zhao([zhaoqi99@outlook.com](mailto:zhaoqi99@outlook.com))