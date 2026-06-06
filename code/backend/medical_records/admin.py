from django.contrib import admin
from .models import MedicalRecord, CTScan

class CTScanInline(admin.TabularInline):
    """CT扫描内联显示"""
    model = CTScan
    extra = 0
    fields = ['scan_mode', 'original_image', 'processed_image', 'tumor_detected', 'confidence_score', 'is_verified', 'scan_date']
    readonly_fields = ['scan_date']

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """医疗记录管理"""
    list_display = ['patient', 'get_patient_name', 'doctor', 'get_doctor_name', 'diagnosis', 'status', 'visit_date', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at', 'visit_date']
    search_fields = ['patient__user__name', 'patient__name', 'doctor__user__name', 'doctor__name', 'diagnosis', 'symptoms', 'record_number']
    ordering = ['-created_at']
    inlines = [CTScanInline]
    
    fieldsets = (
        ('关联信息', {'fields': ('patient', 'doctor')}),
        ('就诊信息', {'fields': ('visit_date', 'symptoms')}),
        ('诊断信息', {'fields': ('diagnosis', 'treatment_plan', 'notes')}),
        ('状态', {'fields': ('status',)}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.patient.user.name or obj.patient.user.username
    get_patient_name.short_description = '患者姓名'
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.name or obj.doctor.user.username if obj.doctor else '-'
    get_doctor_name.short_description = '医生姓名'

@admin.register(CTScan)
class CTScanAdmin(admin.ModelAdmin):
    """CT扫描管理"""
    list_display = ['medical_record', 'scan_mode', 'tumor_detected', 'confidence_score', 'is_verified', 'scan_date']
    list_filter = ['scan_mode', 'tumor_detected', 'is_verified', 'scan_date', 'tumor_type']
    search_fields = ['medical_record__patient__user__name', 'medical_record__patient__name', 'ai_analysis', 'doctor_review']
    ordering = ['-created_at']
    
    fieldsets = (
        ('关联记录', {'fields': ('medical_record',)}),
        ('扫描信息', {'fields': ('scan_mode', 'original_image', 'processed_image', 'scan_date')}),
        ('分析结果', {'fields': ('tumor_detected', 'tumor_type', 'tumor_size', 'tumor_location', 'confidence_score', 'ai_analysis')}),
        ('验证信息', {'fields': ('is_verified', 'doctor_review')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'scan_date']

