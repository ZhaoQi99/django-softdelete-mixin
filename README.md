# Django Softdelete Mixin
## What is it
django-softdelete-mixin is a simple Django package that contains some mixins which implement soft delete for Django ORM.

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
* is_deleted - is a boolean field, shows weather of a deletion state of object

Use the abstract model `BaseModel` for adding another two fields in addition to `is_deleted`:
* create_at - is a datetime field, shows the time of creation of object
* update_at - is a datetime field, shows the time of last update of object

```python
from django_softdelete_mixin.models import SoftDeleteModel, BaseModel

class YourModel(SoftDeleteModel):
    pass

class YourModel(BaseModel):
    pass
```
### Custom QuerySet
```python
from django_softdelete_mixin.query import SoftDeleteQuerySet

class YourOwnQuerySet(SoftDeleteQuerySet):
    pass
```
### Custom Manager
```python
from django_softdelete_mixin.manager import SoftDeleteManager

class YourOwnManager(SoftDeleteManager):
    pass
```

### Mixins
```python
from django_softdelete_mixin.mixins import SoftDeleteManagerMixin,SoftDeleteQuerySetMixin

# For inherited model
class YourOwnManager(SoftDeleteManagerMixin, SomeParentManagerClass):
    pass

class YourOwnQuerySet(SoftDeleteQuerySetMixin, SomeParentQuerySetClass):
    pass
```
## License
[GNU General Public License v3.0](https://github.com/ZhaoQi99/django-softdelete-mixin/blob/main/LICENSE)
## Author
* Qi Zhao([zhaoqi99@outlook.com](mailto:zhaoqi99@outlook.com))