import uuid

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from medical_records.models import MedicalRecord
from notifications.models import Notification

from .models import Appointment
from .serializers import AppointmentRejectSerializer, AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """预约挂号管理。患者创建预约，医生接诊后才生成病历。"""

    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Appointment.objects
            .select_related(
                'patient',
                'patient__user',
                'doctor',
                'doctor__user',
                'medical_record',
            )
            .order_by('-visit_date', '-created_at')
        )

        if user.user_type == 'patient' and hasattr(user, 'patient_profile'):
            return queryset.filter(patient=user.patient_profile)

        if user.user_type == 'doctor' and hasattr(user, 'doctor_profile'):
            return queryset.filter(doctor=user.doctor_profile)

        if user.user_type == 'family' and hasattr(user, 'family_profile'):
            from families.models import FamilyPatientBinding

            patient_ids = FamilyPatientBinding.objects.filter(
                family=user.family_profile
            ).values_list('patient_id', flat=True)
            return queryset.filter(patient_id__in=patient_ids)

        return Appointment.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.user_type != 'patient':
            return Response({'error': '只有患者可以提交挂号申请'}, status=status.HTTP_403_FORBIDDEN)

        patient = getattr(request.user, 'patient_profile', None)
        if not patient:
            return Response({'error': '未找到患者档案，请先完善患者信息'}, status=status.HTTP_404_NOT_FOUND)

        # P0: 临时身份证号未补全时禁止挂号
        if patient.id_card and patient.id_card.startswith('TEMP'):
            return Response(
                {'error': '请先完善真实身份证信息后再挂号', 'redirect': '/pages/completeProfile/completeProfile'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save(patient=patient)

        Notification.objects.create(
            recipient=appointment.doctor.user,
            sender=request.user,
            notification_type='appointment',
            title=f'新挂号申请 - {appointment.patient.name}',
            content=self._build_doctor_notice(appointment),
        )

        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_appointments(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def doctor_pending(self, request):
        if request.user.user_type != 'doctor':
            return Response({'error': '只有医生可以查看待接诊挂号'}, status=status.HTTP_403_FORBIDDEN)

        appointments = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def family_appointments(self, request):
        if request.user.user_type != 'family':
            return Response({'error': '只有家属可以查看绑定患者挂号'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        appointment = self.get_object()
        if request.user.user_type != 'doctor' or appointment.doctor.user_id != request.user.id:
            return Response({'error': '只有预约医生可以接诊'}, status=status.HTTP_403_FORBIDDEN)

        if appointment.status != 'pending':
            return Response({'error': '只有待接诊挂号可以接诊'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            appointment = Appointment.objects.select_for_update().get(pk=appointment.pk)
            if appointment.status != 'pending':
                return Response({'error': '该挂号状态已变化，请刷新后重试'}, status=status.HTTP_400_BAD_REQUEST)

            medical_record = appointment.medical_record
            if not medical_record:
                medical_record = MedicalRecord.objects.create(
                    patient=appointment.patient,
                    doctor=appointment.doctor,
                    record_number=self._generate_record_number(),
                    visit_date=appointment.visit_date,
                    department=appointment.department or appointment.doctor.department or '',
                    symptoms=appointment.symptoms or '',
                    notes=self._build_record_notes(appointment),
                    status='processing',
                )

            appointment.medical_record = medical_record
            appointment.status = 'accepted'
            appointment.reject_reason = ''
            appointment.save(update_fields=['medical_record', 'status', 'reject_reason', 'updated_at'])

            Notification.objects.create(
                recipient=appointment.patient.user,
                sender=request.user,
                notification_type='appointment',
                title='挂号已接诊',
                content=f'医生 {appointment.doctor.name} 已接诊您的挂号申请，病历号：{medical_record.record_number}。',
                medical_record=medical_record,
            )

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        appointment = self.get_object()
        if request.user.user_type != 'doctor' or appointment.doctor.user_id != request.user.id:
            return Response({'error': '只有预约医生可以拒绝挂号'}, status=status.HTTP_403_FORBIDDEN)

        if appointment.status != 'pending':
            return Response({'error': '只有待接诊挂号可以拒绝'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AppointmentRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data.get('reason', '').strip() or '医生暂不接诊，请重新选择其他时间或医生。'

        appointment.status = 'rejected'
        appointment.reject_reason = reason
        appointment.save(update_fields=['status', 'reject_reason', 'updated_at'])

        Notification.objects.create(
            recipient=appointment.patient.user,
            sender=request.user,
            notification_type='appointment',
            title='挂号已被拒绝',
            content=f'医生 {appointment.doctor.name} 已拒绝您的挂号申请。原因：{reason}',
        )

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if request.user.user_type != 'patient' or appointment.patient.user_id != request.user.id:
            return Response({'error': '只有预约患者可以取消挂号'}, status=status.HTTP_403_FORBIDDEN)

        if appointment.status != 'pending':
            return Response({'error': '只有待接诊挂号可以取消'}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = 'cancelled'
        appointment.save(update_fields=['status', 'updated_at'])

        Notification.objects.create(
            recipient=appointment.doctor.user,
            sender=request.user,
            notification_type='appointment',
            title='挂号已取消',
            content=f'患者 {appointment.patient.name} 已取消挂号申请。',
        )

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        if request.user.user_type != 'doctor' or appointment.doctor.user_id != request.user.id:
            return Response({'error': '只有预约医生可以完成就诊'}, status=status.HTTP_403_FORBIDDEN)

        if appointment.status not in ['accepted']:
            return Response({'error': '只有已接诊挂号可以完成'}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = 'completed'
        appointment.save(update_fields=['status', 'updated_at'])

        if appointment.medical_record:
            appointment.medical_record.status = 'completed'
            appointment.medical_record.save(update_fields=['status', 'updated_at'])

        return Response(AppointmentSerializer(appointment).data)

    def _generate_record_number(self):
        record_number = f"MR{str(uuid.uuid4())[:8].upper()}"
        while MedicalRecord.objects.filter(record_number=record_number).exists():
            record_number = f"MR{str(uuid.uuid4())[:8].upper()}"
        return record_number

    def _build_record_notes(self, appointment):
        parts = []
        if appointment.medical_history:
            parts.append(f"病史：{appointment.medical_history}")
        if appointment.get_appointment_type_display():
            parts.append(f"挂号类型：{appointment.get_appointment_type_display()}")
        return '\n'.join(parts)

    def _build_doctor_notice(self, appointment):
        visit_date = appointment.visit_date.strftime('%Y-%m-%d %H:%M') if appointment.visit_date else '待定'
        return (
            f"患者 {appointment.patient.name} 提交了挂号申请。\n"
            f"挂号类型：{appointment.get_appointment_type_display()}\n"
            f"就诊时间：{visit_date}\n"
            f"就诊科室：{appointment.department or appointment.doctor.department or '未填写'}\n"
            f"主诉：{appointment.symptoms or '无'}\n\n"
            "请在医生端患者管理页进行接诊或拒绝。"
        )
