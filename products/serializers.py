from rest_framework import serializers
from .models import Product, ProductSize, Category


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(max_length=100, required=False)
    size = serializers.ChoiceField(
        choices=[(size.name, size.value) for size in ProductSize])

    class Meta:
        model = Product
        fields = [
            'id',
            'price',
            'const',
            'name',
            'chosung',
            'description',
            'barcode',
            'expiration_date',
            'size',
            'category_name',
        ]

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        category = None
        if category_name is not None:
            category = Category.objects.filter(name=category_name).first()
            if not category:
                category = Category.objects.create(name=category_name)
        validated_data['category'] = category
        return super().create(validated_data)
