from django.db import models
from core.models import TimeStampModel


class User(TimeStampModel):
    phone = models.CharField(max_length=13)
    password = models.CharField(max_length=100)

    class Meta:
        db_table = 'users'
