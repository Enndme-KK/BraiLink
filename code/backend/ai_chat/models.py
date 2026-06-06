from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ChatSession(models.Model):
    """AI聊天会话模型"""
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200, default='新对话')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.patient.name} - {self.title}"

class ChatMessage(models.Model):
    """聊天消息模型"""
    MESSAGE_TYPE_CHOICES = [
        ('user', '用户'),
        ('ai', 'AI助手'),
        ('system', '系统'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_message_type_display()} - {self.content[:50]}..."
    
    class Meta:
        ordering = ['timestamp']
