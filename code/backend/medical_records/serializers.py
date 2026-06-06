from rest_framework import serializers
from .models import MedicalRecord, CTScan
from patients.serializers import PatientSerializer
from doctors.serializers import DoctorSerializer

class CTScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CTScan
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class MedicalRecordSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    ct_scans = CTScanSerializer(many=True, read_only=True)
    patient_id = serializers.IntegerField(write_only=True, required=False)  # 用于创建时接收patient_id
    doctor_id = serializers.IntegerField(write_only=True, required=False)  # 用于创建时接收doctor_id
    
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'record_number')
    
    def create(self, validated_data):
        # 生成记录号
        import uuid
        validated_data['record_number'] = f"MR{str(uuid.uuid4())[:8].upper()}"
        
        # 处理patient_id
        patient_id = validated_data.pop('patient_id', None)
        if patient_id:
            from patients.models import Patient
            validated_data['patient'] = Patient.objects.get(id=patient_id)
        
        # 处理doctor_id
        doctor_id = validated_data.pop('doctor_id', None)
        if doctor_id:
            from doctors.models import Doctor
            try:
                validated_data['doctor'] = Doctor.objects.get(id=doctor_id)
            except Doctor.DoesNotExist:
                raise serializers.ValidationError({'doctor_id': '指定的医生不存在'})
        
        return super().create(validated_data)

class MedicalRecordListSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)  # 添加患者ID
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_gender = serializers.CharField(source='patient.gender', read_only=True)  # 添加性别
    patient_age = serializers.IntegerField(source='patient.age', read_only=True)  # 添加年龄
    doctor_name = serializers.CharField(source='doctor.name', read_only=True, allow_null=True)
    medical_history = serializers.CharField(source='patient.medical_history', read_only=True)  # 添加病史
    ct_scans = CTScanSerializer(many=True, read_only=True)
    is_assigned = serializers.SerializerMethodField()  # 是否已分配医生
    is_my_patient = serializers.SerializerMethodField()  # 是否当前医生接诊
    has_appointment_notification = serializers.SerializerMethodField()  # 是否有未读挂号通知
    
    class Meta:
        model = MedicalRecord
        fields = ('id', 'record_number', 'patient_id', 'patient_name', 'patient_gender', 'patient_age', 
                  'doctor_name', 'visit_date', 'status', 'created_at',
                  'department', 'bed_num', 'check_project', 'position', 'diagnosis', 'notes', 
                  'symptoms', 'medical_history', 'ct_scans', 'is_assigned', 'is_my_patient', 
                  'has_appointment_notification')
    
    def get_is_assigned(self, obj):
        """判断病历是否已分配医生"""
        return obj.doctor is not None
    
    def get_is_my_patient(self, obj):
        """判断是否当前医生接诊"""
        request = self.context.get('request')
        if request and request.user and request.user.user_type == 'doctor':
            return obj.doctor is not None and obj.doctor.user.id == request.user.id
        return False
    
    def get_has_appointment_notification(self, obj):
        """判断是否有未读挂号通知"""
        request = self.context.get('request')
        if request and request.user and request.user.user_type == 'doctor':
            # 检查是否有该医疗记录的未读挂号通知
            from notifications.models import Notification
            return Notification.objects.filter(
                medical_record=obj,
                notification_type='appointment',
                recipient=request.user,
                is_read=False
            ).exists()
        return False

class CTScanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CTScan
        fields = ('original_image', 'scan_mode')
    
    def create(self, validated_data):
        validated_data['medical_record'] = self.context['medical_record']
        return super().create(validated_data)
