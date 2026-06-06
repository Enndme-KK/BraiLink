from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Doctor
from .serializers import DoctorSerializer, DoctorListSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    """医生管理视图集"""
    permission_classes = [IsAuthenticated]

    def _build_unique_license_number(self, user):
        base = f'DOC{user.id:06d}'
        if not Doctor.objects.filter(license_number=base).exists():
            return base

        index = 1
        while Doctor.objects.filter(license_number=f'{base}-{index}').exists():
            index += 1
        return f'{base}-{index}'

    def _ensure_doctor_profile(self, user):
        if user.user_type != 'doctor':
            return None

        doctor = Doctor.objects.filter(user=user).first()
        if doctor:
            return doctor

        return Doctor.objects.create(
            user=user,
            name=user.name or user.username,
            license_number=self._build_unique_license_number(user),
            specialty='general',
            hospital='待完善',
            department='待完善',
            title='待完善',
            phone=user.phone or '',
            email=user.email or '',
            bio='',
            experience_years=0,
            is_verified=True,
        )
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'doctor':
            self._ensure_doctor_profile(user)
            return Doctor.objects.filter(user=user)
        elif user.user_type == 'patient':
            return (
                Doctor.objects
                .filter(user__user_type='doctor', user__is_active=True)
                .select_related('user')
                .order_by('-is_verified', 'id')
            )
        return Doctor.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DoctorListSerializer
        return DoctorSerializer
    
    def create(self, request, *args, **kwargs):
        """创建医生档案"""
        if request.user.user_type != 'doctor':
            return Response({'error': '只有医生可以创建档案'}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查是否已有档案
        if hasattr(request.user, 'doctor_profile'):
            return Response({'error': '您已有档案，请更新现有档案'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()
        
        return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """获取当前医生的档案"""
        if request.user.user_type != 'doctor':
            return Response({'error': '只有医生可以查看档案'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            doctor = self._ensure_doctor_profile(request.user)
            serializer = DoctorSerializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response({'error': '未找到医生档案'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def patients(self, request, pk=None):
        """获取医生负责的病人列表（去重，按最近就诊时间倒序）。"""
        from medical_records.models import MedicalRecord
        from appointments.models import Appointment
        from patients.models import Patient
        from patients.serializers import PatientListSerializer

        doctor = self.get_object()

        # 权限：仅本人可看自己的患者列表
        if request.user.user_type != 'doctor' or doctor.user_id != request.user.id:
            return Response({'error': '无权查看该医生的患者列表'}, status=status.HTTP_403_FORBIDDEN)

        record_patient_ids = set(
            MedicalRecord.objects
            .filter(doctor=doctor)
            .values_list('patient_id', flat=True)
        )
        appt_patient_ids = set(
            Appointment.objects
            .filter(doctor=doctor, status__in=['accepted', 'completed'])
            .values_list('patient_id', flat=True)
        )
        patient_ids = record_patient_ids | appt_patient_ids

        patients = (
            Patient.objects
            .filter(id__in=patient_ids)
            .select_related('user')
            .order_by('-updated_at')
        )

        serializer = PatientListSerializer(patients, many=True, context={'request': request})
        return Response({'patients': serializer.data, 'count': patients.count()})

    @action(detail=False, methods=['get'])
    def related_families(self, request):
        """获取该医生接诊过的患者所绑定的家属列表，用于医生主动联系家属。"""
        if request.user.user_type != 'doctor':
            return Response({'error': '只有医生可以查看关联家属'}, status=status.HTTP_403_FORBIDDEN)

        doctor_profile = getattr(request.user, 'doctor_profile', None)
        if not doctor_profile:
            return Response({'error': '未找到医生档案'}, status=status.HTTP_404_NOT_FOUND)

        from medical_records.models import MedicalRecord
        from appointments.models import Appointment
        from families.models import FamilyPatientBinding

        record_patient_ids = set(
            MedicalRecord.objects.filter(doctor=doctor_profile).values_list('patient_id', flat=True)
        )
        appt_patient_ids = set(
            Appointment.objects.filter(
                doctor=doctor_profile, status__in=['accepted', 'completed']
            ).values_list('patient_id', flat=True)
        )
        patient_ids = record_patient_ids | appt_patient_ids

        bindings = (
            FamilyPatientBinding.objects
            .filter(patient_id__in=patient_ids)
            .select_related('family', 'family__user', 'patient')
            .order_by('-created_at')
        )

        seen = set()
        result = []
        for b in bindings:
            fid = b.family_id
            if fid in seen:
                continue
            seen.add(fid)
            u = b.family.user
            result.append({
                'family_user_id': u.id,
                'family_name': b.family.name or u.name or u.username,
                'relationship': b.relationship or '',
                'patient_id': b.patient_id,
                'patient_name': b.patient.name,
                'phone': b.family.phone or u.phone or '',
            })

        return Response(result)
