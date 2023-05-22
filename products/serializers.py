from rest_framework import serializers
from .models import Product, ProductSize, Category


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(max_length=100, required=False)

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


class ProductCreateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(max_length=100, required=False)
    size = serializers.ChoiceField(
        choices=[(size.name, size.value) for size in ProductSize])
    chosung = serializers.CharField(max_length=100, required=False)

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
            'category_name'
        ]

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        category = None
        if category_name is not None:
            category, created = Category.objects.get_or_create(
                name=category_name)

        validated_data['category'] = category
        validated_data['user'] = self.context['request'].user

        product = super().create(validated_data)

        return product
