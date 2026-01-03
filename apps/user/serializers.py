from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from . import models


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化"""

    username = serializers.CharField(
        label='用户名',
        help_text='用户名或手机号',
        max_length=20,
        required=True,
        error_messages={
            'required': '用户名不能为空',
            'blank': '用户名不能为空',
        }
    )

    password = serializers.CharField(
        label='密码',
        help_text='密码',
        max_length=128,
        required=True,
        write_only=True,
        error_messages={
            'required': '密码不能为空',
            'blank': '密码不能为空',
        }
    )

    def validate(self, attrs):
        """验证用户名和密码"""
        username = attrs.get('username')
        password = attrs.get('password')

        # 使用 Django 认证后端验证
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError('用户名或密码错误')

        if not user.is_active:
            raise serializers.ValidationError('用户已被禁用')

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        """生成 JWT token 并返回用户对象"""
        user = self.validated_data['user']

        # 生成 JWT token
        refresh = RefreshToken.for_user(user)

        # 将 token 添加到用户对象上
        user.access = str(refresh.access_token)
        user.refresh = str(refresh)

        return user


class TokenRefreshSerializer(serializers.Serializer):
    """Token刷新序列化"""

    refresh = serializers.CharField(
        label='刷新令牌',
        help_text='用于刷新访问令牌的刷新令牌',
        max_length=500,
        required=True,
        write_only=True,
        error_messages={
            'required': 'refresh不能为空',
            'blank': 'refresh不能为空',
        }
    )

    def validate(self, attrs):
        """验证并刷新 token"""
        refresh_token = attrs.get('refresh')

        try:
            # 验证 refresh token
            refresh = RefreshToken(refresh_token)

            # 生成新的 access token
            access_token = str(refresh.access_token)

            # 如果配置了 ROTATE_REFRESH_TOKENS,会生成新的 refresh token
            new_refresh_token = str(refresh)

            return {
                'access': access_token,
                'refresh': new_refresh_token,
            }
        except Exception as e:
            raise serializers.ValidationError(f'refresh token 无效或已过期: {str(e)}')


class UserSerializer(serializers.ModelSerializer):
    """用户序列化"""

    access = serializers.CharField(read_only=True, help_text='JWT access token')
    refresh = serializers.CharField(read_only=True, help_text='JWT refresh token')

    class Meta:
        model = models.User
        fields = ['id', 'name', 'gender', 'mobile', 'avatar_url', 'access', 'refresh']


class TestSerializer(serializers.Serializer):
    """test序列化"""

    abc = serializers.CharField(label='abc', help_text='测试刷新接口的文档是否有显示',
                                write_only=True, max_length=10, min_length=1, required=True,
                                error_messages={
                                    'invalid': '不是有效的字符串',
                                    'null': 'token_refresh参数不能为空',
                                    'blank': 'token_refresh参数内容不能为空',
                                    'required': '不能缺少abc字段',
                                    'max_length': '内容太长',
                                    'min_length': '内容太短'
                                }, )

    # 局部钩子
    # def validate_abc(self, abc):
    #     if abc:
    #         return abc

    # 全局钩子
    # def validate(self, attrs):
    #     abc = attrs.get('abc')
    #
    #     return {'get': abc}
