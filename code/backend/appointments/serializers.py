from rest_framework import serializers

from doctors.models import Doctor
from doctors.serializers import DoctorListSerializer
from medical_records.serializers import MedicalRecordSerializer
from patients.serializers import PatientSerializer

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorListSerializer(read_only=True)
    medical_record = MedicalRecordSerializer(read_only=True)
    doctor_id = serializers.IntegerField(write_only=True, required=True)
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_gender = serializers.CharField(source='patient.gender', read_only=True)
    patient_age = serializers.IntegerField(source='patient.age', read_only=True)
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_user_id = serializers.IntegerField(source='doctor.user.id', read_only=True)
    appointment_type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    medical_record_id = serializers.IntegerField(source='medical_record.id', read_only=True, allow_null=True)

    class Meta:
        model = Appointment
        fields = (
            'id',
            'patient',
            'patient_id',
            'patient_name',
            'patient_gender',
            'patient_age',
            'patient_phone',
            'doctor',
            'doctor_id',
            'doctor_name',
            'doctor_user_id',
            'medical_record',
            'medical_record_id',
            'appointment_type',
            'appointment_type_display',
            'visit_date',
            'department',
            'symptoms',
            'medical_history',
            'status',
            'status_display',
            'reject_reason',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'patient',
            'doctor',
            'medical_record',
            'status',
            'reject_reason',
            'created_at',
            'updated_at',
        )

    def validate_doctor_id(self, value):
        try:
            doctor = Doctor.objects.select_related('user').get(id=value)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError('指定的医生不存在')

        if not doctor.user.is_active:
            raise serializers.ValidationError('该医生账号不可用')

        return value

    def create(self, validated_data):
        doctor_id = validated_data.pop('doctor_id')
        validated_data['doctor'] = Doctor.objects.get(id=doctor_id)
        return super().create(validated_data)


class AppointmentRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
