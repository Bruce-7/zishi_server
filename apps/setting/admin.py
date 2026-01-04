from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import AppVersion


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    """
    应用版本管理后台
    只有管理员可以访问和配置
    """
    list_display = [
        'id',
        'platform_badge',
        'version_name',
        'version_code',
        'title',
        'force_update_badge',
        'active_badge',
        'create_time',
        'action_buttons'
    ]

    list_filter = [
        'platform',
        'is_force_update',
        'is_active',
        'create_time'
    ]

    search_fields = [
        'version_name',
        'version_code',
        'title',
        'description'
    ]

    readonly_fields = [
        'create_time',
        'update_time',
        'is_delete',
        'delete_time'
    ]

    fieldsets = (
        ('基本信息', {
            'fields': (
                'platform',
                'version_code',
                'version_name',
                'title',
                'description'
            )
        }),
        ('下载配置', {
            'fields': (
                'download_url',
                'is_force_update',
                'min_support_version'
            )
        }),
        ('更新日志', {
            'fields': (
                'release_notes',
            ),
            'classes': ('collapse',)
        }),
        ('状态管理', {
            'fields': (
                'is_active',
            )
        }),
        ('时间信息', {
            'fields': (
                'create_time',
                'update_time',
                'is_delete',
                'delete_time'
            ),
            'classes': ('collapse',)
        })
    )

    ordering = ['-version_code', '-create_time']

    list_per_page = 20

    date_hierarchy = 'create_time'

    def platform_badge(self, obj):
        """平台标签"""
        colors = {
            'ios': '#007AFF',
            'android': '#3DDC84',
            'all': '#6C757D'
        }
        color = colors.get(obj.platform, '#6C757D')
        return mark_safe(
            f'<span style="background-color: {color}; color: white; padding: 3px 10px; '
            f'border-radius: 3px; font-size: 12px;">{obj.get_platform_display()}</span>'
        )

    platform_badge.short_description = '平台'

    def force_update_badge(self, obj):
        """强制更新标签"""
        if obj.is_force_update:
            return mark_safe(
                '<span style="background-color: #DC3545; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 12px;">强制</span>'
            )
        return mark_safe(
            '<span style="background-color: #28A745; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 12px;">可选</span>'
        )

    force_update_badge.short_description = '更新类型'

    def active_badge(self, obj):
        """启用状态标签"""
        if obj.is_active:
            return mark_safe(
                '<span style="background-color: #28A745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 12px;">✓ 启用</span>'
            )
        return mark_safe(
            '<span style="background-color: #6C757D; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 12px;">✗ 禁用</span>'
        )

    active_badge.short_description = '状态'

    def action_buttons(self, obj):
        """操作按钮"""
        return mark_safe(
            f'<a class="button" href="/zishi_admin/setting/appversion/{obj.id}/change/" '
            f'style="padding: 5px 10px; background-color: #417690; color: white; '
            f'text-decoration: none; border-radius: 3px; font-size: 12px;">编辑</a>'
        )

    action_buttons.short_description = '操作'

    def has_add_permission(self, request):
        """只有管理员可以添加"""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """只有管理员可以修改"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """只有管理员可以删除"""
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        """只有管理员可以查看"""
        return request.user.is_superuser

    actions = ['enable_versions', 'disable_versions']

    def enable_versions(self, request, queryset):
        """批量启用版本"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功启用 {updated} 个版本')

    enable_versions.short_description = '启用选中的版本'

    def disable_versions(self, request, queryset):
        """批量禁用版本"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功禁用 {updated} 个版本')

    disable_versions.short_description = '禁用选中的版本'
