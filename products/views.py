from functools import reduce
import operator
import re
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models.functions import Cast
from django.db.models import CharField, Q
from django.db import transaction
from django.http import JsonResponse

from products.models import Product, Category, ProductSize
from products.serializers import ProductSerializer
from users.login_decorator import login_decorator


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @login_decorator
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user
        data['user_id'] = user.id
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
                    category, created = Category.objects.get_or_create(
                        name=category_name)
                    product.category = category
                    product.category_name = category_name
                    product.category_id = category.id
                    product.user_id = user.id
                    product.save()
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

    @login_decorator
    def get_queryset(self, request):
        limit = self.request.GET.get('limit', 10)
        cursor = self.request.GET.get('cursor', 0)

        products = Product.objects.filter(id__gt=cursor).order_by(
            'id').annotate(id_str=Cast('id', CharField())).values('id', 'id_str')[:limit]

        product_ids = [int(p['id']) for p in products]
        return Product.objects.filter(id__in=product_ids).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        serializer = self.get_serializer(queryset, many=True)

        if queryset:
            next_cursor = queryset.last().id
            response_data = {
                'meta': {'code': status.HTTP_200_OK, 'message': '상품 정보 리스트입니다'},
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

    @login_decorator
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response({
            'meta': {'code': status.HTTP_200_OK, 'message': '입력하신 id값에 해당하는 상품 정보입니다'},
            'data': serializer.data
        })


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @login_decorator
    def get_queryset(self, request):
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
        queryset = self.get_queryset(request)
        serializer = self.get_serializer(queryset, many=True)

        if queryset:
            next_cursor = queryset.last().id
            response_data = {
                'meta': {'code': status.HTTP_200_OK, 'message': '입력하신 키워드에 해당하는 상품 정보입니다'},
                'data': serializer.data,
                'next_cursor': next_cursor
            }
            return Response(response_data)
        else:
            return Response({
                'meta': {'code': status.HTTP_404_NOT_FOUND, 'message': '입력하신 키워드에 해당하는 상품이 존재하지 않습니다'}
            })


class ProductChosungView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @login_decorator
    def get_queryset(self, request):
        cursor = self.request.GET.get('cursor', 0)
        limit = Product.objects.count()
        keyword = self.request.GET.get('keyword', '')

        if not keyword:
            return Product.objects.none()

        CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ',
                        'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

        def get_chosung(word):
            chosung_word = ''
            for ch in word:
                if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', ch):
                    chosung = ord(ch) - 44032
                    chosung = int(chosung / 588)
                    if chosung < 0 or chosung >= len(CHOSUNG_LIST):
                        return ''
                    chosung_word += CHOSUNG_LIST[chosung]
                else:
                    chosung_word += ch
            return chosung_word

        keyword_chosung = get_chosung(keyword)

        products = Product.objects.filter(
            reduce(operator.and_, (Q(chosung__icontains=x)for x in keyword.split())))\
            .filter(id__gt=cursor).order_by('id')[:limit]

        product_ids = [int(p.id) for p in products]
        return Product.objects.filter(id__in=product_ids).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        serializer = self.get_serializer(queryset, many=True)

        if queryset:
            next_cursor = queryset.last().id
            response_data = {
                'meta': {'code': status.HTTP_200_OK, 'message': '입력하신 초성키워드에 해당하는 상품 정보입니다'},
                'data': serializer.data,
                'next_cursor': next_cursor
            }
            return Response(response_data)
        else:
            return Response({
                'meta': {'code': status.HTTP_404_NOT_FOUND, 'message': '입력하신 초성키워드에 해당하는 상품이 존재하지 않습니다'}
            })


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    @login_decorator
    def put(self, request, *args, **kwargs):
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

    @login_decorator
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            'meta': {'code': status.HTTP_200_OK, 'message': '상품 정보가 삭제되었습니다'},
            'data': None
        })
