from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models.functions import Cast
from django.db.models import CharField

from .models import Product
from .serializers import ProductSerializer


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'meta': {'code': status.HTTP_201_CREATED, 'message': '상품 정보가 등록되었습니다'},
                    'data': serializer.data
                }
            )
        else:
            return Response({
                'meta': {'code': status.HTTP_400_BAD_REQUEST, 'message': '상품 정보를 다시 확인해주세요'},
                'data': None
            })


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        limit = self.request.GET.get('limit', 10)
        cursor = self.request.GET.get('cursor', 0)

        products = Product.objects.filter(id__gt=cursor).order_by(
            'id').annotate(id_str=Cast('id', CharField())).values('id', 'id_str')[:limit]

        product_ids = [int(p['id']) for p in products]
        return Product.objects.filter(id__in=product_ids).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

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


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response({
            'meta': {'code': status.HTTP_200_OK, 'message': '200_OK'},
            'data': serializer.data
        })


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        cursor = self.request.GET.get('cursor', 0)  # cursor = 0
        limit = Product.objects.count()
        keyword = self.request.GET.get('keyword', '')

        products = Product.objects.filter(name__icontains=keyword).filter(
            id__gt=cursor).order_by('id')[:limit]

        product_ids = [int(p.id) for p in products]
        return Product.objects.filter(id__in=product_ids).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

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
                'meta': {'code': status.HTTP_404_NOT_FOUND, 'message': '해당 키워드에 맞는 상품이 존재하지 않습니다'}
            })


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(
            instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'meta': {'code': status.HTTP_200_OK, 'message': '상품 정보가 수정되었습니다'},
                'data': serializer.data
            })
        else:
            return Response({
                'meta': {'code': status.HTTP_400_BAD_REQUEST, 'message': '상품 정보를 다시 확인해주세요'},
                'data': None
            })


class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'meta': {'code': status.HTTP_200_OK, 'message': '상품 정보가 삭제되었습니다'},
            'data': None
        })
