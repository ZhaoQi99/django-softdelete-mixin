import random

from django.utils import timezone


def random_datetime():
    # 微秒+4位随机数共27位 eg: 20221108.164544.897432.5045
    now_str = timezone.now().strftime("%Y%m%d.%H%M%S.%f")
    return "{}.{}".format(now_str, random.randint(1000, 9999))
