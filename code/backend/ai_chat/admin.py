from django.contrib import admin
from .models import ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    """聊天消息内联显示"""
    model = ChatMessage
    extra = 0
    fields = ['message_type', 'content', 'timestamp']
    readonly_fields = ['timestamp']
    ordering = ['timestamp']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """AI聊天会话管理"""
    list_display = ['patient', 'get_patient_name', 'title', 'message_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['patient__user__username', 'patient__user__name', 'patient__name', 'title']
    ordering = ['-updated_at']
    inlines = [ChatMessageInline]
    
    fieldsets = (
        ('关联患者', {'fields': ('patient',)}),
        ('会话信息', {'fields': ('title', 'session_id', 'is_active')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'session_id']
    
    def get_patient_name(self, obj):
        return obj.patient.name or obj.patient.user.username
    get_patient_name.short_description = '患者姓名'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = '消息数量'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """聊天消息管理"""
    list_display = ['session', 'message_type', 'get_content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['session__title', 'content']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('关联会话', {'fields': ('session',)}),
        ('消息内容', {'fields': ('message_type', 'content', 'is_processed')}),
        ('时间信息', {'fields': ('timestamp',)}),
    )
    
    readonly_fields = ['timestamp']
    
    def get_content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_content_preview.short_description = '内容预览'

