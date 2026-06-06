from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Feedback

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ['username', 'name', 'email', 'user_type', 'phone', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'name', 'email', 'phone']
    ordering = ['-created_at']

    # 添加自定义字段到管理界面
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('user_type', 'name', 'phone', 'avatar')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )

    # 添加用户时的字段
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('user_type', 'name', 'phone', 'email')}),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """意见反馈管理"""
    list_display = ['id', 'user', 'content_short', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['user__username', 'user__name', 'content']
    ordering = ['-created_at']
    readonly_fields = ['user', 'content', 'created_at']
    list_editable = ['is_resolved']

    def content_short(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_short.short_description = '反馈内容'

