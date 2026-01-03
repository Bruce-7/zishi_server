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
