from django.contrib.auth.models import AbstractUser
from django.db import models

from models.base_model import BaseModel


class User(AbstractUser, BaseModel):
    """用户信息模型
    
    继承自 Django 的 AbstractUser 和 BaseModel，提供完整的用户管理功能
    
    继承字段（来自 AbstractUser）：
    - username: 用户名，唯一标识，用于登录
    - password: 密码（已加密）
    - first_name: 名字
    - last_name: 姓氏
    - email: 邮箱地址
    - is_staff: 是否为员工（可访问后台）
    - is_active: 账户是否激活
    - is_superuser: 是否为超级管理员
    - last_login: 最后登录时间
    - date_joined: 注册时间
    
    继承字段（来自 BaseModel）：
    - create_time: 创建时间
    - update_time: 更新时间
    - is_delete: 是否删除（软删除标记）
    - delete_time: 删除时间
    
    扩展字段：
    - name: 真实姓名/昵称
    - gender: 性别
    - mobile: 手机号码
    - avatar_url: 头像链接
    - birthday: 出生日期
    - bio: 个人简介
    - address: 联系地址
    - id_card: 身份证号
    - wechat_openid: 微信 OpenID
    - wechat_unionid: 微信 UnionID
    - last_login_ip: 最后登录 IP
    """

    class Gender(models.TextChoices):
        """性别枚举"""
        MALE = 'male', '男'
        FEMALE = 'female', '女'
        UNKNOWN = 'unknown', '未知'

    name = models.CharField(
        verbose_name='姓名',
        help_text='用户真实姓名或昵称',
        max_length=50,
        null=True,
        blank=True
    )

    gender = models.CharField(
        verbose_name='性别',
        help_text='用户性别',
        max_length=10,
        choices=Gender,
        default=Gender.UNKNOWN,
        null=True,
        blank=True
    )

    mobile = models.CharField(
        verbose_name='手机号',
        help_text='用户手机号码，用于登录和找回密码',
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    avatar_url = models.URLField(
        verbose_name='头像链接',
        help_text='用户头像图片 URL',
        max_length=500,
        null=True,
        blank=True
    )

    birthday = models.DateField(
        verbose_name='出生日期',
        help_text='用户出生日期',
        null=True,
        blank=True
    )

    bio = models.TextField(
        verbose_name='个人简介',
        help_text='用户个人简介或签名',
        max_length=500,
        null=True,
        blank=True
    )

    address = models.CharField(
        verbose_name='联系地址',
        help_text='用户联系地址',
        max_length=200,
        null=True,
        blank=True
    )

    id_card = models.CharField(
        verbose_name='身份证号',
        help_text='用户身份证号码（加密存储）',
        max_length=18,
        null=True,
        blank=True,
        db_index=True
    )

    wechat_openid = models.CharField(
        verbose_name='微信OpenID',
        help_text='微信小程序/公众号 OpenID',
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    wechat_unionid = models.CharField(
        verbose_name='微信UnionID',
        help_text='微信开放平台 UnionID',
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    last_login_ip = models.GenericIPAddressField(
        verbose_name='最后登录IP',
        help_text='用户最后一次登录的 IP 地址',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['mobile'], name='idx_user_mobile'),
            models.Index(fields=['wechat_openid'], name='idx_user_wechat_openid'),
            models.Index(fields=['create_time'], name='idx_user_create_time'),
        ]

    def __str__(self):
        """返回用户的字符串表示"""
        return self.name or self.username or f'User-{self.id}'

    def get_full_info(self):
        """获取用户完整信息字典"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'mobile': self.mobile,
            'gender': self.gender,
            'avatar_url': self.avatar_url,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'bio': self.bio,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'create_time': self.create_time.isoformat() if self.create_time else None,
        }

    def get_display_name(self):
        """获取用户显示名称（优先级：name > username > 手机号）"""
        return self.name or self.username or self.mobile or f'用户{self.id}'

    @property
    def age(self):
        """计算用户年龄"""
        if not self.birthday:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birthday.year - (
                (today.month, today.day) < (self.birthday.month, self.birthday.day)
        )
