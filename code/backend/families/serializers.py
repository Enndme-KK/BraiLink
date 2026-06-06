from rest_framework import serializers
from .models import Family, FamilyPatientBinding, FamilyInviteCode
from patients.models import Patient
from accounts.serializers import UserSerializer


class FamilySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Family
        fields = ('id', 'user', 'name', 'phone', 'relationship_note', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class FamilyPatientBindingSerializer(serializers.ModelSerializer):
    family = FamilySerializer(read_only=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)

    class Meta:
        model = FamilyPatientBinding
        fields = (
            'id',
            'family',
            'patient_id',
            'patient_name',
            'relationship',
            'created_at'
        )
        read_only_fields = fields


class FamilyInviteCodeSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)

    class Meta:
        model = FamilyInviteCode
        fields = ('code', 'patient_id', 'patient_name', 'created_at')
        read_only_fields = fields


class FamilyBindByCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=10)
    relationship = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_invite_code(self, value):
        code = (value or '').strip().upper()
        if len(code) != 10:
            raise serializers.ValidationError('邀请码必须为10位')
        if not code.isalnum():
            raise serializers.ValidationError('邀请码只能包含大写字母和数字')
        return code


class PatientInviteCodeGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id',)


class FamilyBoundPatientSummarySerializer(serializers.Serializer):
    binding_id = serializers.IntegerField()
    id = serializers.IntegerField()
    name = serializers.CharField()
    gender = serializers.CharField()
    age = serializers.IntegerField(allow_null=True)
    phone = serializers.CharField(allow_blank=True)
    relationship = serializers.CharField(allow_blank=True)
    binding_time = serializers.DateTimeField(allow_null=True)


class FamilyMedicalRecordSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    patient_id = serializers.IntegerField(required=False)
    patient_name = serializers.CharField(required=False, allow_blank=True)
    relationship = serializers.CharField(required=False, allow_blank=True)
    record_number = serializers.CharField()
    visit_date = serializers.DateTimeField(allow_null=True)
    department = serializers.CharField(allow_blank=True)
    bed_num = serializers.CharField(allow_blank=True)
    check_project = serializers.CharField(allow_blank=True)
    position = serializers.CharField(allow_blank=True)
    diagnosis = serializers.CharField(allow_blank=True)
    notes = serializers.CharField(allow_blank=True)
    status = serializers.CharField(allow_blank=True)
    doctor_name = serializers.CharField(allow_blank=True)


class FamilyRegistrationSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    patient_id = serializers.IntegerField(required=False)
    patient_name = serializers.CharField(required=False, allow_blank=True)
    relationship = serializers.CharField(required=False, allow_blank=True)
    record_number = serializers.CharField(allow_blank=True)
    visit_date = serializers.DateTimeField(allow_null=True)
    appointment_type = serializers.CharField(required=False, allow_blank=True)
    appointment_type_display = serializers.CharField(required=False, allow_blank=True)
    department = serializers.CharField(allow_blank=True)
    bed_num = serializers.CharField(allow_blank=True)
    check_project = serializers.CharField(allow_blank=True)
    position = serializers.CharField(allow_blank=True)
    status = serializers.CharField(allow_blank=True)
    status_display = serializers.CharField(required=False, allow_blank=True)
    symptoms = serializers.CharField(required=False, allow_blank=True)
    reject_reason = serializers.CharField(required=False, allow_blank=True)
    doctor_name = serializers.CharField(allow_blank=True)
    medical_record_id = serializers.IntegerField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)


class FamilyHomeSummarySerializer(serializers.Serializer):
    bound = serializers.BooleanField()
    patient = FamilyBoundPatientSummarySerializer(allow_null=True)
    medical_records = FamilyMedicalRecordSummarySerializer(many=True)
    registrations = FamilyRegistrationSummarySerializer(many=True)


class FamilyDoctorContactSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    doctor_user_id = serializers.IntegerField()
    doctor_name = serializers.CharField()
    specialty = serializers.CharField(allow_blank=True)
    hospital = serializers.CharField(allow_blank=True)
    department = serializers.CharField(allow_blank=True)
    title = serializers.CharField(allow_blank=True)
    patient_id = serializers.IntegerField()
    patient_name = serializers.CharField()
    relationship = serializers.CharField(allow_blank=True)
    latest_visit_date = serializers.DateTimeField(allow_null=True)
    latest_record_id = serializers.IntegerField(allow_null=True)
