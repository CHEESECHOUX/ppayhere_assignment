from rest_framework import serializers

from .models import Product, ProductSize


class ProductSerializer(serializers.ModelSerializer):
    size = serializers.ChoiceField(
        choices=[(size.name, size.value) for size in ProductSize])

    class Meta:
        model = Product
        fields = '__all__'
