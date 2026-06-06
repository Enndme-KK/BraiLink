from django.db import models
from django.utils import timezone


class Appointment(models.Model):
    """预约挂号记录。病历只在医生接诊后创建。"""

    STATUS_CHOICES = [
        ('pending', '待接诊'),
        ('accepted', '已接诊'),
        ('rejected', '已拒绝'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    ]

    APPOINTMENT_TYPE_CHOICES = [
        ('outpatient', '普通门诊'),
        ('expert', '专家门诊'),
        ('emergency', '急诊'),
        ('followup', '复诊'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='appointments')
    medical_record = models.OneToOneField(
        'medical_records.MedicalRecord',
        on_delete=models.SET_NULL,
        related_name='appointment',
        blank=True,
        null=True,
    )
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPE_CHOICES, default='outpatient')
    visit_date = models.DateTimeField()
    department = models.CharField(max_length=100, blank=True)
    symptoms = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reject_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-visit_date', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['doctor', 'status']),
            models.Index(fields=['visit_date']),
        ]

    def __str__(self):
        return f"{self.patient.name} -> {self.doctor.name} ({self.get_status_display()})"
