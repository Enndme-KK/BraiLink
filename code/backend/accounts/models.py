from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """用户基础模型 - 扩展Django默认用户模型"""
    USER_TYPE_CHOICES = [
        ('doctor', '医生'),
        ('patient', '病人'),
        ('family', '家属'),
    ]

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='patient',
        verbose_name='用户类型'
    )
    name = models.CharField(max_length=100, blank=True, verbose_name='真实姓名')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号码')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='头像'
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name or self.username} ({self.get_user_type_display()})"


class Feedback(models.Model):
    """用户意见反馈"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='提交用户'
    )
    content = models.TextField(max_length=500, verbose_name='反馈内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    is_resolved = models.BooleanField(default=False, verbose_name='是否处理')

    class Meta:
        verbose_name = '意见反馈'
        verbose_name_plural = '意见反馈'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} · {self.created_at:%Y-%m-%d %H:%M}"
