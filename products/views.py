from functools import reduce
import operator
import pymysql
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models.functions import Cast, Substr
from django.db.models import CharField, Q
from django.db import transaction
from django.http import JsonResponse

from .models import Product, Category, ProductSize
from .serializers import ProductSerializer
from .korea_chosung import korea_chosung


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        category_name = data.pop('category_name', None)
        size = data.get('size', None)
        if size and size.upper() not in [s.name for s in ProductSize]:
            return Response({
                'meta': {'code': status.HTTP_400_BAD_REQUEST, 'message': 'INVALID PRODUCT SIZE'},
                'data': None
            })
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                product = serializer.save()
                if category_name:
                    category = Category.objects.get(
                        name=category_name)
                    product.category = category
                    product.category_name = category_name
                    product.save()
                    product.category_id = category.id
                return Response(
                    {
                        'meta': {'code': status.HTTP_201_CREATED, 'message': '상품 정보가 등록되었습니다'},
                        'data': serializer.data
                    }
                )
        else:
            return Response({
                'meta': {'code': status.HTTP_400_BAD_REQUEST, 'message': 'INVALID PRODUCT DATA'},
                'data': serializer.errors
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
        cursor = self.request.GET.get('cursor', 0)
        limit = Product.objects.count()
        keyword = self.request.GET.get('keyword', '')

        if not keyword:
            return Product.objects.none()

        products = Product.objects.filter(
            reduce(operator.and_, (Q(name__icontains=x)for x in keyword.split())))\
            .filter(id__gt=cursor).order_by('id')[:limit]

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


class ProductChosungView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        keyword = request.GET.get('keyword', '')
        if not keyword:
            return JsonResponse({'message': '상품 이름을 다시 입력하세요'}, status=400)

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='JisooChoi0206!',
            db='payhere',
            charset='utf8'
        )
        cursor = conn.cursor()

        # fn_choSearch 함수를 호출하여 초성 값을 가져옴
        cursor.callproc('fn_choSearch', [keyword])
        result = cursor.fetchone()[0]

        # MySQL 연결 종료
        cursor.close()
        conn.close()

        if not result:
            return JsonResponse({'message': '초성 값을 가져올 수 없습니다'}, status=400)

        # 가져온 초성 값을 사용하여 상품을 검색
        chosung_str = result.replace(' ', '')
        products = Product.objects.annotate(chosung_value=Substr('chosung', 1, len(chosung_str))) \
                          .filter(chosung_value=chosung_str, name__icontains=keyword)

        if not products:
            return JsonResponse({'message': '일치하는 상품 이름이 없습니다'}, status=404)

        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, status=200, safe=False)


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
