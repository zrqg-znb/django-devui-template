from rest_framework.response import Response
from rest_framework import status
from typing import Any, Optional, Dict
from django.core.paginator import Paginator


class ApiResponse:
    """统一API响应格式"""

    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200) -> Response:
        """成功响应"""
        return Response({
            'code': code,
            'message': message,
            'data': data,
            'success': True
        }, status=status.HTTP_200_OK)

    @staticmethod
    def error(message: str = "操作失败", code: int = 400, data: Any = None) -> Response:
        """失败响应"""
        return Response({
            'code': code,
            'message': message,
            'data': data,
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def paginated_response(queryset, page: int, page_size: int, serializer_class, request=None) -> Response:
        """分页响应"""
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = serializer_class(page_obj.object_list, many=True, context={'request': request})

        return Response({
            'code': 200,
            'message': "获取成功",
            'data': {
                'items': serializer.data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            },
            'success': True
        }, status=status.HTTP_200_OK)