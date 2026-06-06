from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    """通知模型"""
    NOTIFICATION_TYPE_CHOICES = [
        ('report_shared', '报告分享'),
        ('system', '系统通知'),
        ('reminder', '提醒通知'),
        ('chat', '聊天消息'),
        ('message', '消息'),
        ('appointment', '挂号通知'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收者')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', blank=True, null=True, verbose_name='发送者')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='system', verbose_name='通知类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    is_read = models.BooleanField(default=False, verbose_name='已读')
    
    # 关联的医疗记录（如果通知与报告相关）
    medical_record = models.ForeignKey('medical_records.MedicalRecord', on_delete=models.CASCADE, blank=True, null=True, related_name='notifications', verbose_name='关联医疗记录')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='读取时间')
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
