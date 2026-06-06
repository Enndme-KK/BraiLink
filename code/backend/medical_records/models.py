from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class MedicalRecord(models.Model):
    """医疗记录模型"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    TUMOR_TYPE_CHOICES = [
        ('benign', '良性'),
        ('malignant', '恶性'),
        ('unknown', '未知'),
    ]
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='medical_records', null=True, blank=True)
    record_number = models.CharField(max_length=50, unique=True)
    visit_date = models.DateTimeField(default=timezone.now)
    
    # 基本信息字段
    department = models.CharField(max_length=100, blank=True, verbose_name='科室')
    bed_num = models.CharField(max_length=50, blank=True, verbose_name='床号')
    check_project = models.CharField(max_length=200, blank=True, verbose_name='检查项目')
    position = models.CharField(max_length=200, blank=True, verbose_name='检查部位')
    
    # 原有字段
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.name} - {self.record_number}"

class CTScan(models.Model):
    """CT扫描记录模型"""
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='ct_scans')
    scan_date = models.DateTimeField(default=timezone.now)
    original_image = models.ImageField(upload_to='ct_scans/original/')
    processed_image = models.ImageField(upload_to='ct_scans/processed/', blank=True, null=True)
    scan_mode = models.CharField(max_length=20, default='1')
    tumor_detected = models.BooleanField(default=False)
    tumor_type = models.CharField(max_length=20, choices=MedicalRecord.TUMOR_TYPE_CHOICES, blank=True)
    tumor_size = models.CharField(max_length=100, blank=True)
    tumor_location = models.CharField(max_length=200, blank=True)
    confidence_score = models.FloatField(default=0.0)
    ai_analysis = models.TextField(blank=True)
    doctor_review = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"CT Scan - {self.medical_record.record_number}"
