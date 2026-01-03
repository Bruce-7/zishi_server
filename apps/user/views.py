from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from utils.base_views import BaseModelViewSet
from utils.response import ResponseUtil
from . import models
from .serializers import UserLoginSerializer, UserSerializer, TokenRefreshSerializer


class CustomBackend(ModelBackend):
    """自定义用户验证
    
    支持用户名或手机号登录
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(models.User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        try:
            user = models.User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except models.User.DoesNotExist:
            return None


class UserViewSet(BaseModelViewSet):
    """用户视图集
    
    提供用户的查询和更新功能
    - list: 获取用户列表（需要管理员权限）
    - update: 更新用户信息
    - me: 获取当前登录用户信息
    - login: 用户登录
    - refresh_token: 刷新令牌
    """
    resource_name = '用户'
    queryset = models.User.objects.filter(is_delete=False)
    serializer_class = UserSerializer

    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action == 'list':
            return [IsAdminUser()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'me']:
            return [IsAuthenticated()]
        return []

    def get_serializer_class(self):
        """根据操作类型选择序列化器"""
        if self.action == 'login':
            return UserLoginSerializer
        elif self.action == 'refresh_token':
            return TokenRefreshSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        """更新用户信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseUtil(
            message='用户信息更新成功',
            data=serializer.data,
            http_status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前登录用户信息"""
        serializer = self.get_serializer(request.user)
        return ResponseUtil(data=serializer.data, http_status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[])
    def login(self, request):
        """用户登录
        
        支持用户名或手机号登录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_serializer = UserSerializer(user)
        return ResponseUtil(
            message='登录成功',
            data=user_serializer.data,
            http_status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], permission_classes=[], url_path='refresh_token')
    def refresh_token(self, request):
        """刷新令牌
        
        使用 refresh_token 刷新得到最新访问 token
        refresh_token 使用后不能再使用
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return ResponseUtil(
            message='令牌刷新成功',
            data=serializer.validated_data,
            http_status=status.HTTP_200_OK
        )
