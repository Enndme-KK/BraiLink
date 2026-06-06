from django.db import migrations


def build_unique_license(Doctor, user_id):
    base = f'DOC{user_id:06d}'
    if not Doctor.objects.filter(license_number=base).exists():
        return base

    index = 1
    while Doctor.objects.filter(license_number=f'{base}-{index}').exists():
        index += 1
    return f'{base}-{index}'


def sync_registered_doctors(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Doctor = apps.get_model('doctors', 'Doctor')

    doctor_users = User.objects.filter(
        user_type='doctor',
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )

    for user in doctor_users:
        Doctor.objects.get_or_create(
            user=user,
            defaults={
                'name': user.name or user.username,
                'license_number': build_unique_license(Doctor, user.id),
                'specialty': 'general',
                'hospital': '待完善',
                'department': '待完善',
                'title': '待完善',
                'phone': user.phone or '',
                'email': user.email or '',
                'bio': '',
                'experience_years': 0,
                'is_verified': True,
            },
        )

    Doctor.objects.filter(
        user__user_type='doctor',
        user__is_active=True,
        user__is_staff=False,
        user__is_superuser=False,
    ).update(is_verified=True)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_user_type'),
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sync_registered_doctors, migrations.RunPython.noop),
    ]
