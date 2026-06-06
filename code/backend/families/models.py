import random
import string

from django.conf import settings
from django.db import models
from django.utils import timezone

from patients.models import Patient

User = settings.AUTH_USER_MODEL


class Family(models.Model):
    """家属扩展档案"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='family_profile')
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    relationship_note = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '家属档案'
        verbose_name_plural = '家属档案'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or getattr(self.user, 'name', '') or self.user.username


class FamilyPatientBinding(models.Model):
    """家属与病人的绑定关系"""
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='bindings')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_bindings')
    relationship = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '家属病人绑定'
        verbose_name_plural = '家属病人绑定'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['family', 'patient'], name='unique_family_patient_binding')
        ]

    def __str__(self):
        return f'{self.family} -> {self.patient}'


class FamilyInviteCode(models.Model):
    """病人生成给家属使用的一次性邀请码"""
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='family_invite_code')
    code = models.CharField(max_length=10, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_family_invite_codes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = '家属邀请码'
        verbose_name_plural = '家属邀请码'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.patient} - {self.code}'

    @staticmethod
    def generate_code(length=10):
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(alphabet, k=length))
            if not FamilyInviteCode.objects.filter(code=code).exists():
                return code
