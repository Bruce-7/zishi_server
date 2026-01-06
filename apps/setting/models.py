from django.core.validators import RegexValidator
from django.db import models

from models.base_model import BaseModel


class AppVersion(BaseModel):
    """
    应用版本更新模型
    用于管理移动端应用的版本更新信息
    """
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('all', '全平台'),
    ]

    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='all',
        verbose_name='平台',
        help_text='应用平台类型'
    )

    version_code = models.IntegerField(
        verbose_name='版本号',
        help_text='版本号（整数），用于版本比较，例如：100、101、200',
        db_index=True
    )

    version_name = models.CharField(
        max_length=50,
        verbose_name='版本名称',
        help_text='版本名称（字符串），例如：1.0.0、1.0.1',
        validators=[
            RegexValidator(
                regex=r'^\d+\.\d+\.\d+$',
                message='版本名称格式必须为：x.x.x（例如：1.0.0）'
            )
        ]
    )

    title = models.CharField(
        max_length=200,
        verbose_name='更新标题',
        help_text='版本更新的标题'
    )

    description = models.TextField(
        verbose_name='更新描述',
        help_text='版本更新的详细描述，支持换行'
    )

    download_url = models.URLField(
        max_length=500,
        verbose_name='下载地址',
        help_text='应用下载链接（APK/IPA 或应用商店链接）',
        blank=True,
        null=True
    )

    is_force_update = models.BooleanField(
        default=False,
        verbose_name='是否强制更新',
        help_text='强制更新时，用户必须更新才能继续使用应用'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='只有启用的版本才会被检查接口返回'
    )

    release_notes = models.TextField(
        verbose_name='更新日志',
        help_text='详细的更新日志，支持 Markdown 格式',
        blank=True,
        null=True
    )

    min_support_version = models.IntegerField(
        verbose_name='最低支持版本号',
        help_text='低于此版本号的应用将被强制更新',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'setting_app_version'
        verbose_name = '应用版本'
        verbose_name_plural = '应用版本管理'
        ordering = ['-version_code', '-create_time']
        unique_together = [['platform', 'version_code']]
        indexes = [
            models.Index(fields=['platform', 'is_active']),
            models.Index(fields=['-version_code']),
        ]

    def __str__(self):
        return f"{self.get_platform_display()} - {self.version_name} (v{self.version_code})"

    def save(self, *args, **kwargs):
        """
        保存前的验证逻辑
        """
        # 如果设置为强制更新，确保有下载地址
        if self.is_force_update and not self.download_url:
            from django.core.exceptions import ValidationError
            raise ValidationError('强制更新时必须提供下载地址')

        super().save(*args, **kwargs)


class DynamicConfig(BaseModel):
    """
    动态配置模型
    用于管理应用中的各类动态内容配置，如 banner、活动、设置等
    支持通过 type 字段区分不同类型的配置
    """
    TYPE_CHOICES = [
        ('banner', 'Banner广告'),
        ('activity', '活动配置'),
        ('setting', '系统设置'),
    ]

    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        db_index=True,
        verbose_name='配置类型',
        help_text='配置类型：banner、activity、setting'
    )

    title = models.CharField(
        max_length=200,
        verbose_name='标题',
        help_text='配置项的标题'
    )

    banner_image_url = models.URLField(
        max_length=500,
        verbose_name='Banner图片URL',
        help_text='Banner图片地址，用于 banner 和 activity 类型',
        blank=True,
        null=True
    )

    target_url = models.URLField(
        max_length=500,
        verbose_name='目标URL',
        help_text='点击后跳转的网页地址',
        blank=True,
        null=True
    )

    description = models.TextField(
        verbose_name='描述',
        help_text='配置项的详细描述',
        blank=True,
        null=True
    )

    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序',
        help_text='数字越小越靠前，默认为0',
        db_index=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='只有启用的配置才会被接口返回'
    )

    start_time = models.DateTimeField(
        verbose_name='生效开始时间',
        help_text='配置生效的开始时间',
        blank=True,
        null=True
    )

    end_time = models.DateTimeField(
        verbose_name='生效结束时间',
        help_text='配置生效的结束时间',
        blank=True,
        null=True
    )

    extra_data = models.JSONField(
        verbose_name='扩展数据',
        help_text='额外的配置数据，JSON格式',
        blank=True,
        null=True,
        default=dict
    )

    class Meta:
        db_table = 'setting_dynamic_config'
        verbose_name = '动态配置'
        verbose_name_plural = '动态配置管理'
        ordering = ['type', 'sort_order', '-create_time']
        indexes = [
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['type', 'sort_order']),
            models.Index(fields=['start_time', 'end_time']),
        ]

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"

    def is_valid_time(self):
        """
        检查当前时间是否在配置的有效期内
        
        Returns:
            bool: 如果在有效期内返回 True，否则返回 False
        """
        from django.utils import timezone
        now = timezone.now()

        # 如果没有设置时间限制，则始终有效
        if not self.start_time and not self.end_time:
            return True

        # 只设置了开始时间
        if self.start_time and not self.end_time:
            return now >= self.start_time

        # 只设置了结束时间
        if not self.start_time and self.end_time:
            return now <= self.end_time

        # 同时设置了开始和结束时间
        return self.start_time <= now <= self.end_time

    def save(self, *args, **kwargs):
        """
        保存前的验证逻辑
        """
        # 验证时间范围
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                from django.core.exceptions import ValidationError
                raise ValidationError('生效开始时间必须早于结束时间')

        # 确保 extra_data 不为 None
        if self.extra_data is None:
            self.extra_data = {}

        super().save(*args, **kwargs)
