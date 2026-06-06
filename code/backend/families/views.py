from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from appointments.models import Appointment
from medical_records.models import MedicalRecord

from .models import Family, FamilyInviteCode, FamilyPatientBinding
from .serializers import (
    FamilyBindByCodeSerializer,
    FamilyDoctorContactSerializer,
    FamilyHomeSummarySerializer,
    FamilyInviteCodeSerializer,
    FamilyPatientBindingSerializer,
    FamilySerializer,
)


class FamilyViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FamilySerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'family' and hasattr(user, 'family_profile'):
            return Family.objects.filter(user=user)
        return Family.objects.none()

    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        if request.user.user_type != 'family':
            return Response({'error': '只有家属可以查看家属档案'}, status=status.HTTP_403_FORBIDDEN)

        try:
            serializer = FamilySerializer(request.user.family_profile)
            return Response(serializer.data)
        except Family.DoesNotExist:
            return Response({'error': '未找到家属档案'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """医生查询某患者绑定的家属列表。需传 ?patient_id=<id>"""
        if request.user.user_type != 'doctor':
            return Response({'error': '只有医生可以查询患者家属'}, status=status.HTTP_403_FORBIDDEN)

        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response({'error': '请提供 patient_id'}, status=status.HTTP_400_BAD_REQUEST)

        doctor_profile = getattr(request.user, 'doctor_profile', None)
        if not doctor_profile:
            return Response({'error': '未找到医生档案'}, status=status.HTTP_403_FORBIDDEN)

        bindings = (
            FamilyPatientBinding.objects
            .filter(patient_id=patient_id)
            .select_related('family', 'family__user')
        )
        result = []
        for b in bindings:
            u = b.family.user
            result.append({
                'family_user_id': u.id,
                'family_name': b.family.name or u.name or u.username,
                'relationship': b.relationship or '',
            })
        return Response(result)

    @action(detail=False, methods=['get'])
    def my_bindings(self, request):
        if request.user.user_type != 'family':
            return Response({'error': '只有家属可以查看绑定关系'}, status=status.HTTP_403_FORBIDDEN)

        try:
            family = request.user.family_profile
        except Family.DoesNotExist:
            return Response({'error': '未找到家属档案'}, status=status.HTTP_404_NOT_FOUND)

        bindings = FamilyPatientBinding.objects.filter(family=family).select_related('patient', 'patient__user')
        serializer = FamilyPatientBindingSerializer(bindings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def home_summary(self, request):
        if request.user.user_type != 'family':
            return Response({'error': '只有家属可以查看首页摘要'}, status=status.HTTP_403_FORBIDDEN)

        try:
            family = request.user.family_profile
        except Family.DoesNotExist:
            return Response({'error': '未找到家属档案'}, status=status.HTTP_404_NOT_FOUND)

        bindings = list(
            FamilyPatientBinding.objects
            .filter(family=family)
            .select_related('patient', 'patient__user')
            .order_by('-created_at')
        )
        binding = bindings[0] if bindings else None

        if not binding:
            serializer = FamilyHomeSummarySerializer({
                'bound': False,
                'patient': None,
                'medical_records': [],
                'registrations': []
            })
            return Response(serializer.data)

        patient = binding.patient
        patient_map = {item.patient_id: item for item in bindings}
        patient_ids = list(patient_map.keys())
        medical_records_qs = (
            MedicalRecord.objects
            .filter(patient_id__in=patient_ids)
            .select_related('patient', 'patient__user', 'doctor', 'doctor__user')
            .order_by('-visit_date', '-created_at')
        )
        appointments_qs = (
            Appointment.objects
            .filter(patient_id__in=patient_ids)
            .select_related('patient', 'patient__user', 'doctor', 'doctor__user', 'medical_record')
            .order_by('-visit_date', '-created_at')
        )

        patient_summary = {
            'binding_id': binding.id,
            'id': patient.id,
            'name': patient.name,
            'gender': patient.get_gender_display(),
            'age': patient.age if patient.birth_date else None,
            'phone': patient.phone or '',
            'relationship': binding.relationship or '',
            'binding_time': binding.created_at,
        }

        medical_records = []
        registrations = []

        for record in medical_records_qs:
            doctor_name = ''
            if record.doctor:
                doctor_name = record.doctor.name or getattr(getattr(record.doctor, 'user', None), 'name', '') or getattr(getattr(record.doctor, 'user', None), 'username', '')

            record_binding = patient_map.get(record.patient_id)
            medical_records.append({
                'id': record.id,
                'patient_id': record.patient_id,
                'patient_name': record.patient.name,
                'relationship': record_binding.relationship if record_binding else '',
                'record_number': record.record_number,
                'visit_date': record.visit_date,
                'department': record.department or '',
                'bed_num': record.bed_num or '',
                'check_project': record.check_project or '',
                'position': record.position or '',
                'diagnosis': record.diagnosis or '',
                'notes': record.notes or '',
                'status': record.status or '',
                'doctor_name': doctor_name,
            })

        for appointment in appointments_qs:
            appointment_binding = patient_map.get(appointment.patient_id)
            record_number = appointment.medical_record.record_number if appointment.medical_record else ''
            registrations.append({
                'id': appointment.id,
                'patient_id': appointment.patient_id,
                'patient_name': appointment.patient.name,
                'relationship': appointment_binding.relationship if appointment_binding else '',
                'record_number': record_number,
                'visit_date': appointment.visit_date,
                'appointment_type': appointment.appointment_type or '',
                'appointment_type_display': appointment.get_appointment_type_display(),
                'department': appointment.department or appointment.doctor.department or '',
                'bed_num': '',
                'check_project': appointment.get_appointment_type_display(),
                'position': '',
                'status': appointment.status or '',
                'status_display': appointment.get_status_display(),
                'symptoms': appointment.symptoms or '',
                'reject_reason': appointment.reject_reason or '',
                'doctor_name': appointment.doctor.name or appointment.doctor.user.name or appointment.doctor.user.username,
                'medical_record_id': appointment.medical_record_id,
                'created_at': appointment.created_at,
            })

        serializer = FamilyHomeSummarySerializer({
            'bound': True,
            'patient': patient_summary,
            'medical_records': medical_records,
            'registrations': registrations,
        })
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def related_doctors(self, request):
        if request.user.user_type != 'family':
            return Response({'error': '只有家属可以查看关联医生'}, status=status.HTTP_403_FORBIDDEN)

        try:
            family = request.user.family_profile
        except Family.DoesNotExist:
            return Response({'error': '未找到家属档案'}, status=status.HTTP_404_NOT_FOUND)

        bindings = list(
            FamilyPatientBinding.objects
            .filter(family=family)
            .select_related('patient', 'patient__user')
            .order_by('-created_at')
        )

        if not bindings:
            return Response([])

        patient_map = {binding.patient_id: binding for binding in bindings}
        medical_records = (
            MedicalRecord.objects
            .filter(patient_id__in=patient_map.keys(), doctor__isnull=False)
            .select_related('patient', 'patient__user', 'doctor', 'doctor__user')
            .order_by('-visit_date', '-created_at')
        )
        accepted_appointments = (
            Appointment.objects
            .filter(patient_id__in=patient_map.keys(), doctor__isnull=False, status__in=['accepted', 'completed'])
            .select_related('patient', 'patient__user', 'doctor', 'doctor__user', 'medical_record')
            .order_by('-visit_date', '-created_at')
        )

        doctor_contacts = []
        seen_doctor_ids = set()

        for record in medical_records:
            doctor = record.doctor
            if not doctor or doctor.id in seen_doctor_ids:
                continue

            binding = patient_map.get(record.patient_id)
            if not binding:
                continue

            seen_doctor_ids.add(doctor.id)
            doctor_contacts.append({
                'doctor_id': doctor.id,
                'doctor_user_id': doctor.user.id,
                'doctor_name': doctor.name or doctor.user.name or doctor.user.username,
                'specialty': doctor.get_specialty_display() if hasattr(doctor, 'get_specialty_display') else (doctor.specialty or ''),
                'hospital': doctor.hospital or '',
                'department': doctor.department or '',
                'title': doctor.title or '',
                'patient_id': record.patient.id,
                'patient_name': record.patient.name,
                'relationship': binding.relationship or '',
                'latest_visit_date': record.visit_date,
                'latest_record_id': record.id,
            })

        for appointment in accepted_appointments:
            doctor = appointment.doctor
            if not doctor or doctor.id in seen_doctor_ids:
                continue

            binding = patient_map.get(appointment.patient_id)
            if not binding:
                continue

            seen_doctor_ids.add(doctor.id)
            doctor_contacts.append({
                'doctor_id': doctor.id,
                'doctor_user_id': doctor.user.id,
                'doctor_name': doctor.name or doctor.user.name or doctor.user.username,
                'specialty': doctor.get_specialty_display() if hasattr(doctor, 'get_specialty_display') else (doctor.specialty or ''),
                'hospital': doctor.hospital or '',
                'department': doctor.department or '',
                'title': doctor.title or '',
                'patient_id': appointment.patient.id,
                'patient_name': appointment.patient.name,
                'relationship': binding.relationship or '',
                'latest_visit_date': appointment.visit_date,
                'latest_record_id': appointment.medical_record_id,
            })

        serializer = FamilyDoctorContactSerializer(doctor_contacts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bind_by_invite_code(self, request):
        if request.user.user_type != 'family':
            return Response({'error': '只有家属可以使用邀请码绑定'}, status=status.HTTP_403_FORBIDDEN)

        try:
            family = request.user.family_profile
        except Family.DoesNotExist:
            return Response({'error': '未找到家属档案'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FamilyBindByCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invite_code = serializer.validated_data['invite_code']
        relationship = serializer.validated_data.get('relationship', '').strip()

        with transaction.atomic():
            invite = FamilyInviteCode.objects.select_for_update().select_related('patient', 'patient__user').filter(code=invite_code).first()
            if not invite:
                return Response({'error': '邀请码无效或已失效'}, status=status.HTTP_400_BAD_REQUEST)

            patient = invite.patient
            if FamilyPatientBinding.objects.filter(family=family, patient=patient).exists():
                return Response({'error': '您已绑定该病人，请勿重复提交'}, status=status.HTTP_400_BAD_REQUEST)

            binding = FamilyPatientBinding.objects.create(
                family=family,
                patient=patient,
                relationship=relationship
            )
            invite.delete()

        return Response({
            'message': '绑定成功',
            'binding': FamilyPatientBindingSerializer(binding).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post', 'delete'])
    def unbind_patient(self, request):
        if request.user.user_type != 'family':
            return Response({'error': '只有家属可以解除绑定'}, status=status.HTTP_403_FORBIDDEN)

        try:
            family = request.user.family_profile
        except Family.DoesNotExist:
            return Response({'error': '未找到家属档案'}, status=status.HTTP_404_NOT_FOUND)

        binding_id = request.data.get('binding_id')
        patient_id = request.data.get('patient_id')

        bindings = FamilyPatientBinding.objects.filter(family=family).select_related('patient')
        if binding_id:
            bindings = bindings.filter(id=binding_id)
        elif patient_id:
            bindings = bindings.filter(patient_id=patient_id)
        else:
            return Response({'error': '请提供 binding_id 或 patient_id'}, status=status.HTTP_400_BAD_REQUEST)

        binding = bindings.first()
        if not binding:
            return Response({'error': '未找到可解除的绑定关系'}, status=status.HTTP_404_NOT_FOUND)

        patient_name = binding.patient.name
        binding.delete()

        return Response({
            'message': '解绑成功',
            'patient_name': patient_name
        })

    @action(detail=False, methods=['post'])
    def generate_invite_code(self, request):
        if request.user.user_type != 'patient':
            return Response({'error': '只有病人可以生成邀请码'}, status=status.HTTP_403_FORBIDDEN)

        patient = getattr(request.user, 'patient_profile', None)
        if not patient:
            return Response({'error': '未找到病人档案'}, status=status.HTTP_404_NOT_FOUND)

        FamilyInviteCode.objects.filter(patient=patient).delete()
        invite = FamilyInviteCode.objects.create(
            patient=patient,
            code=FamilyInviteCode.generate_code(),
            created_by=request.user
        )

        return Response({
            'message': '邀请码生成成功',
            'invite': FamilyInviteCodeSerializer(invite).data
        }, status=status.HTTP_201_CREATED)
