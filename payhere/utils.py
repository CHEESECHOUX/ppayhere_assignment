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
