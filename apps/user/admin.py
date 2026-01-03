from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户后台管理配置
    
    需要管理员权限才能访问和修改用户信息
    """

    list_display = (
        'id',
        'avatar_preview',
        'username',
        'name',
        'mobile',
        'gender_display',
        'tickets_display',
        'coins_display',
        'account_status',
        'is_staff',
        'date_joined',
    )

    list_display_links = ('id', 'username')

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'gender',
        'date_joined',
    )

    search_fields = (
        'username',
        'name',
        'mobile',
        'email',
    )

    readonly_fields = (
        'avatar_large_preview',
        'date_joined',
        'last_login',
        'create_time',
        'update_time',
    )

    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password')
        }),
        ('个人信息', {
            'fields': ('name', 'gender', 'mobile', 'email', 'avatar_url', 'avatar_large_preview')
        }),
        ('虚拟资产', {
            'fields': ('tickets', 'coins'),
            'description': '用户的门票和金币数量，请谨慎修改'
        }),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined', 'create_time', 'update_time'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'name', 'mobile', 'email'),
        }),
    )

    ordering = ('-id',)

    list_per_page = 20

    def tickets_display(self, obj):
        """门票显示（带颜色）"""
        color = 'green' if obj.tickets > 0 else 'gray'
        return mark_safe(f'<span style="color: {color};">{obj.tickets} 张</span>')

    tickets_display.short_description = '门票'

    def coins_display(self, obj):
        """金币显示（带颜色）"""
        color = 'orange' if obj.coins > 0 else 'gray'
        return mark_safe(f'<span style="color: {color};">{obj.coins} 枚</span>')

    coins_display.short_description = '金币'

    def avatar_preview(self, obj):
        """头像预览（小图）"""
        if obj.avatar_url:
            return mark_safe(f'<img src="{obj.avatar_url}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />')
        return mark_safe('<span style="color: gray;">无头像</span>')

    avatar_preview.short_description = '头像'

    def avatar_large_preview(self, obj):
        """头像预览（大图）"""
        if obj.avatar_url:
            return mark_safe(f'<img src="{obj.avatar_url}" width="150" height="150" style="border-radius: 10px; object-fit: cover;" />')
        return mark_safe('<span style="color: gray;">未设置头像</span>')

    avatar_large_preview.short_description = '头像预览'

    def gender_display(self, obj):
        """性别显示（带图标）"""
        gender_map = {
            'male': ('♂ 男', 'blue'),
            'female': ('♀ 女', 'pink'),
            'unknown': ('? 未知', 'gray'),
        }
        label, color = gender_map.get(obj.gender, ('未知', 'gray'))
        return mark_safe(f'<span style="color: {color}; font-weight: bold;">{label}</span>')

    gender_display.short_description = '性别'

    def account_status(self, obj):
        """账户状态显示"""
        if not obj.is_active:
            return mark_safe('<span style="color: red; font-weight: bold;">❌ 已禁用</span>')
        elif obj.is_superuser:
            return mark_safe('<span style="color: purple; font-weight: bold;">👑 超级管理员</span>')
        elif obj.is_staff:
            return mark_safe('<span style="color: blue; font-weight: bold;">🔧 管理员</span>')
        else:
            return mark_safe('<span style="color: green;">✓ 正常</span>')

    account_status.short_description = '账户状态'

    def has_module_permission(self, request):
        """只有管理员才能访问用户管理模块"""
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        """只有管理员才能查看用户信息"""
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        """只有管理员才能修改用户信息"""
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        """只有超级管理员才能删除用户"""
        return request.user.is_superuser
