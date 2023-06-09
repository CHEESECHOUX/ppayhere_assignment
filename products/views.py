from functools import reduce
import operator

from rest_framework import generics, status, serializers
from rest_framework.response import Response
from django.db.models.functions import Cast
from django.db.models import CharField, Q

from products.models import Product
from products.serializers import ProductSerializer, ProductCreateSerializer
from products.korea_chosung import get_chosung
from payhere.utils import list_response
from users.login_decorator import login_decorator


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer

    @login_decorator
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            name = validated_data.get('name', '')
            chosung = get_chosung(name)
            validated_data['chosung'] = chosung
            product = serializer.save()
        except serializers.ValidationError as e:
            return Response({'error': 'INVALID PRODUCT DATA' + str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'meta': {'code': status.HTTP_201_CREATED, 'message': '상품 정보가 등록되었습니다'},
                'data': serializer.data
            }
        )


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

        return list_response(queryset, serializer)


class ProductDetailView(generics.RetrieveAPIView):
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
        limit = self.request.GET.get('limit', 10)
        cursor = self.request.GET.get('cursor', 0)
        keyword = self.request.GET.get('keyword', '')

        if not keyword:
            return Product.objects.none()

        products = Product.objects.filter(
            reduce(operator.or_, (Q(name__icontains=x) | Q(chosung__icontains=x)for x in keyword.split())))\
            .filter(id__gt=cursor).order_by('id')[:limit]

        product_ids = [int(p.id) for p in products]
        return Product.objects.filter(id__in=product_ids).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        serializer = self.get_serializer(queryset, many=True)

        return list_response(queryset, serializer)


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    @login_decorator
    def patch(self, request, *args, **kwargs):
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
