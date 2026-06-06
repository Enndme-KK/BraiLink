# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain_tumor_api.settings')
import django
django.setup()

from families.models import FamilyPatientBinding
from accounts.models import User

print("=== All family users ===")
for u in User.objects.filter(user_type='family'):
    print(f"id={u.id} username={u.username} name={u.name}")

print("\n=== All bindings ===")
for b in FamilyPatientBinding.objects.select_related('family','family__user','patient').all():
    print(f"binding_id={b.id} patient_id={b.patient.id} patient={b.patient.name} family_user_id={b.family.user.id} family_username={b.family.user.username} family_name={b.family.name}")
