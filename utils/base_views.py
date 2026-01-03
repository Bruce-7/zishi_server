from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from utils.response import ResponseUtil


class BaseModelViewSet(ModelViewSet):
    """基础 ModelViewSet
    
    提供通用的 CRUD 操作方法,减少代码重复
    子类需要配置:
    - resource_name: 资源名称,用于提示信息(如 '分类'、'标签')
    """
    resource_name = '资源'

    def _paginated_response(self, queryset):
        """通用分页响应辅助方法"""
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return ResponseUtil(
                data=paginated_response.data,
                http_status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(queryset, many=True)
        return ResponseUtil(data=serializer.data, http_status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """获取列表
        
        支持分页查询,客户端可通过 offset 和 limit 参数控制分页
        - offset: 从第几条记录开始,默认 0
        - limit: 获取多少条记录,默认 20,最大 200
        """
        queryset = self.filter_queryset(self.get_queryset())
        return self._paginated_response(queryset)

    def retrieve(self, request, *args, **kwargs):
        """获取详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ResponseUtil(data=serializer.data, http_status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """创建资源"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseUtil(
            message=f'{self.resource_name}创建成功',
            data=serializer.data,
            http_status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """更新资源"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseUtil(
            message=f'{self.resource_name}更新成功',
            data=serializer.data,
            http_status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """删除资源(软删除)"""
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return ResponseUtil(
            message=f'{self.resource_name}删除成功',
            http_status=status.HTTP_204_NO_CONTENT
        )
