from django.db import models
from core.models import TimeStampModel
from enum import Enum


class ProductSize(Enum):
    SMALL = 'SMALL'
    LARGE = 'LARGE'


class Product(TimeStampModel):
    price = models.DecimalField(max_digits=8, decimal_places=2)
    const = models.DecimalField(max_digits=8, decimal_places=2)
    name = models.CharField(max_length=50)
    chosung = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    barcode = models.CharField(max_length=15)
    expiration_date = models.DateTimeField()
    size = models.CharField(max_length=5, choices=[(
        size.name, size.value) for size in ProductSize])
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE)
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'products'


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'categories'
