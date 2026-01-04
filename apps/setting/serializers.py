from rest_framework import serializers

from .models import AppVersion


class AppVersionListSerializer(serializers.ModelSerializer):
    """应用版本列表序列化器"""

    platform_display = serializers.CharField(
        source='get_platform_display',
        read_only=True,
        help_text='平台显示名称'
    )

    class Meta:
        model = AppVersion
        fields = [
            'id',
            'platform',
            'platform_display',
            'version_code',
            'version_name',
            'title',
            'is_force_update',
            'is_active',
            'create_time',
        ]
        read_only_fields = ['id', 'create_time', 'update_time', 'is_delete']


class AppVersionSerializer(serializers.ModelSerializer):
    """应用版本详情序列化器"""

    platform_display = serializers.CharField(
        source='get_platform_display',
        read_only=True,
        help_text='平台显示名称'
    )

    class Meta:
        model = AppVersion
        fields = [
            'id',
            'platform',
            'platform_display',
            'version_code',
            'version_name',
            'title',
            'description',
            'download_url',
            'is_force_update',
            'is_active',
            'release_notes',
            'min_support_version',
            'create_time',
            'update_time'
        ]
        read_only_fields = ['id', 'create_time', 'update_time', 'is_delete']


class VersionCheckRequestSerializer(serializers.Serializer):
    """
    版本检查请求序列化器
    用于验证客户端提交的版本检查参数
    """
    platform = serializers.ChoiceField(
        choices=['ios', 'android', 'all'],
        required=True,
        help_text='客户端平台类型：ios、android、all'
    )

    version_code = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text='当前应用版本号（整数）'
    )

    version_name = serializers.CharField(
        required=False,
        max_length=50,
        help_text='当前应用版本名称（可选）'
    )

    _allowed_fields = {'platform', 'version_code', 'version_name'}

    def validate(self, attrs):
        extra_keys = set(self.initial_data.keys()) - self._allowed_fields
        if extra_keys:
            raise serializers.ValidationError(
                f'不支持的参数: {", ".join(sorted(extra_keys))}'
            )
        return attrs


class VersionCheckResponseSerializer(serializers.Serializer):
    """
    版本检查响应序列化器
    用于返回版本检查结果
    """
    has_update = serializers.BooleanField(
        help_text='是否有新版本'
    )

    is_force_update = serializers.BooleanField(
        help_text='是否强制更新'
    )

    latest_version = serializers.DictField(
        required=False,
        allow_null=True,
        help_text='最新版本信息'
    )

    message = serializers.CharField(
        required=False,
        help_text='提示信息'
    )
