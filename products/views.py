from rest_framework import generics, status
from rest_framework.response import Response

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
                    'meta': {
                        'code': status.HTTP_201_CREATED,
                        'message': '상품 정보가 등록되었습니다'
                    },
                    'data': serializer.data
                }
            )
        else:
            return Response(
                {
                    'meta': {
                        'code': status.HTTP_400_BAD_REQUEST,
                        'message': '상품 정보를 다시 확인해주세요'
                    },
                    'data': None
                }
            )


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
            return Response(
                {
                    'meta': {
                        'code': status.HTTP_200_OK,
                        'message': '상품 정보가 수정되었습니다'
                    },
                    'data': serializer.data
                }
            )
        else:
            return Response(
                {
                    'meta': {
                        'code': status.HTTP_400_BAD_REQUEST,
                        'message': '상품 정보를 다시 확인해주세요'
                    },
                    'data': None
                },
            )


class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {
                'meta': {
                    'code': status.HTTP_200_OK,
                    'message': '상품 정보가 삭제되었습니다'
                },
                'data': None
            }
        )
