# Generated by Django 4.1 on 2023-04-21 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='chosung',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
