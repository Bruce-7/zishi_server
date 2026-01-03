from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny

from utils.base_views import BaseModelViewSet
from utils.response import ResponseUtil
from .models import AppVersion
from .serializers import (
    AppVersionSerializer,
    AppVersionListSerializer,
    VersionCheckRequestSerializer
)


class AppVersionViewSet(BaseModelViewSet):
    """应用版本视图集
    
    提供版本管理的增删查改功能
    - list: 获取版本列表（分页）
    - retrieve: 获取版本详情
    - create: 创建版本（需要管理员权限）
    - update: 更新版本（需要管理员权限）
    - destroy: 删除版本（需要管理员权限）
    - check: 检查版本更新（无需登录）
    - latest: 获取最新版本（无需登录）
    """
    resource_name = '应用版本'
    queryset = AppVersion.objects.filter(is_delete=False)
    serializer_class = AppVersionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['platform', 'is_active', 'is_force_update']
    search_fields = ['version_name', 'title', 'description']
    ordering_fields = ['version_code', 'create_time']
    ordering = ['-version_code', '-create_time']

    def get_serializer_class(self):
        """根据操作类型选择序列化器"""
        if self.action == 'list':
            return AppVersionListSerializer
        return AppVersionSerializer

    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def check(self, request):
        """检查版本更新
        
        POST /setting/versions/check/
        
        请求参数：
        {
            "platform": "android",
            "version_code": 100,
            "version_name": "1.0.0"
        }
        """
        # 验证请求参数
        serializer = VersionCheckRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseUtil(
                code=status.HTTP_400_BAD_REQUEST,
                message='参数错误：' + str(serializer.errors),
                data={
                    'has_update': False,
                    'is_force_update': False
                },
                http_status=status.HTTP_400_BAD_REQUEST
            )

        platform = serializer.validated_data['platform']
        current_version_code = serializer.validated_data['version_code']

        try:
            # 查询最新的启用版本
            latest_version = AppVersion.objects.filter(
                Q(platform=platform) | Q(platform='all'),
                is_active=True
            ).order_by('-version_code').first()

            # 如果没有找到任何版本配置
            if not latest_version:
                return ResponseUtil(
                    message='当前已是最新版本',
                    data={
                        'has_update': False,
                        'is_force_update': False,
                        'latest_version': None
                    },
                    http_status=status.HTTP_200_OK
                )

            # 判断是否需要更新
            has_update = current_version_code < latest_version.version_code

            # 判断是否强制更新
            is_force_update = False
            if has_update:
                is_force_update = latest_version.is_force_update
                if latest_version.min_support_version:
                    if current_version_code < latest_version.min_support_version:
                        is_force_update = True

            # 构建响应数据
            response_data = {
                'has_update': has_update,
                'is_force_update': is_force_update,
            }

            if has_update:
                # 有更新时返回最新版本信息
                version_serializer = AppVersionSerializer(latest_version)
                response_data['latest_version'] = version_serializer.data
                message = '发现新版本，请立即更新' if is_force_update else '发现新版本'
            else:
                response_data['latest_version'] = None
                message = '当前已是最新版本'

            return ResponseUtil(
                message=message,
                data=response_data,
                http_status=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseUtil(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f'服务器错误：{str(e)}',
                data={
                    'has_update': False,
                    'is_force_update': False
                },
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def latest(self, request):
        """获取最新版本信息
        
        GET /setting/versions/latest/?platform=android
        """
        platform = request.query_params.get('platform')

        if not platform:
            return ResponseUtil(
                code=status.HTTP_400_BAD_REQUEST,
                message='缺少 platform 参数',
                data=None,
                http_status=status.HTTP_400_BAD_REQUEST
            )

        if platform not in ['ios', 'android', 'all']:
            return ResponseUtil(
                code=status.HTTP_400_BAD_REQUEST,
                message='platform 参数必须是 ios、android 或 all',
                data=None,
                http_status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 查询最新的启用版本
            latest_version = AppVersion.objects.filter(
                Q(platform=platform) | Q(platform='all'),
                is_active=True
            ).order_by('-version_code').first()

            if not latest_version:
                return ResponseUtil(
                    code=status.HTTP_404_NOT_FOUND,
                    message='未找到版本信息',
                    data=None,
                    http_status=status.HTTP_404_NOT_FOUND
                )

            serializer = AppVersionSerializer(latest_version)
            return ResponseUtil(
                message='获取成功',
                data=serializer.data,
                http_status=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseUtil(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f'服务器错误：{str(e)}',
                data=None,
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
