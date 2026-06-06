from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """患者管理"""
    list_display = ['user', 'get_name', 'gender', 'birth_date', 'phone', 'id_card', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__username', 'user__name', 'phone', 'id_card']
    ordering = ['-created_at']
    
    fieldsets = (
        ('关联用户', {'fields': ('user',)}),
        ('基本信息', {'fields': ('gender', 'birth_date', 'id_card', 'phone', 'address')}),
        ('紧急联系人', {'fields': ('emergency_contact', 'emergency_phone')}),
        ('医疗信息', {'fields': ('blood_type', 'allergies', 'medical_history')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_name(self, obj):
        return obj.user.name or obj.user.username
    get_name.short_description = '姓名'

