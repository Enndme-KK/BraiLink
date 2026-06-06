# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain_tumor_api.settings')
import django
django.setup()

from families.models import FamilyPatientBinding
from patients.models import Patient

print("=== Family Bindings ===")
for b in FamilyPatientBinding.objects.select_related('family','family__user','patient').all():
    print(f"patient_id={b.patient.id} patient={b.patient.name} family_user={b.family.user.username} family_user_id={b.family.user.id}")

print("\n=== Patients ===")
for p in Patient.objects.all():
    print(f"id={p.id} name={p.name}")
