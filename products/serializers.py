from rest_framework import serializers
from .models import Product, ProductSize, Category
from rest_framework.response import Response
from rest_framework import status


def list_response(queryset, serializer):
    if queryset:
        next_cursor = queryset.last().id
        response_data = {
            'meta': {'code': status.HTTP_200_OK, 'message': '200_OK'},
            'data': serializer.data,
            'next_cursor': next_cursor
        }
        return Response(response_data)
    else:
        return Response({
            'meta': {'code': status.HTTP_404_NOT_FOUND, 'message': '404_NOT_FOUND_ERROR'}
        })


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
            category, created = Category.objects.get_or_create(
                name=category_name)

        validated_data['category'] = category
        validated_data['category_name'] = category_name
        validated_data['user'] = self.context['request'].user

        product = super().create(validated_data)

        return product
