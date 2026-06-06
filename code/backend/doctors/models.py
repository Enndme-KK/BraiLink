from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Doctor(models.Model):
    """医生信息模型"""
    SPECIALTY_CHOICES = [
        ('neurology', '神经科'),
        ('radiology', '放射科'),
        ('oncology', '肿瘤科'),
        ('neurosurgery', '神经外科'),
        ('general', '全科'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES)
    hospital = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    title = models.CharField(max_length=50)  # 职称
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.name} ({self.specialty})"
