from django.contrib import admin
from django.utils.html import format_html
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """医生管理"""
    list_display = ['get_name', 'hospital', 'department', 'title', 'specialty', 'phone', 'get_verified_badge', 'created_at']
    list_filter = ['is_verified', 'department', 'specialty', 'created_at']
    search_fields = ['user__username', 'user__name', 'hospital', 'department', 'license_number']
    ordering = ['is_verified', '-created_at']
    actions = ['approve_doctors', 'revoke_doctors']

    fieldsets = (
        ('审核状态', {'fields': ('is_verified',), 'classes': ('wide',)}),
        ('关联用户', {'fields': ('user',)}),
        ('职业信息', {'fields': ('hospital', 'department', 'title', 'specialty', 'license_number', 'experience_years')}),
        ('联系方式', {'fields': ('phone', 'email')}),
        ('个人简介', {'fields': ('bio',)}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_name(self, obj):
        return obj.name or obj.user.name or obj.user.username
    get_name.short_description = '姓名'

    def get_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color:green;font-weight:bold">✓ 已审核</span>')
        return format_html('<span style="color:red;font-weight:bold">✗ 待审核</span>')
    get_verified_badge.short_description = '审核状态'

    @admin.action(description='批量通过审核')
    def approve_doctors(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'已通过 {updated} 位医生的审核')

    @admin.action(description='批量撤销审核')
    def revoke_doctors(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'已撤销 {updated} 位医生的审核')

