from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """通知管理视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # 用户只能看到自己接收的通知
        return Notification.objects.filter(recipient=self.request.user)

    def _get_allowed_family_doctor_user_ids(self, user):
        if user.user_type != 'family' or not hasattr(user, 'family_profile'):
            return set()

        from families.models import FamilyPatientBinding
        from medical_records.models import MedicalRecord
        from appointments.models import Appointment

        patient_ids = list(
            FamilyPatientBinding.objects
            .filter(family=user.family_profile)
            .values_list('patient_id', flat=True)
        )

        if not patient_ids:
            return set()

        record_doctor_ids = set(
            MedicalRecord.objects
            .filter(patient_id__in=patient_ids, doctor__isnull=False)
            .values_list('doctor__user_id', flat=True)
            .distinct()
        )
        appointment_doctor_ids = set(
            Appointment.objects
            .filter(patient_id__in=patient_ids, doctor__isnull=False, status__in=['accepted', 'completed'])
            .values_list('doctor__user_id', flat=True)
            .distinct()
        )
        return record_doctor_ids | appointment_doctor_ids

    def _can_send_chat_message(self, sender, recipient):
        if sender.id == recipient.id:
            return False, '不能给自己发送消息'

        allowed_user_types = {'doctor', 'patient', 'family'}
        if sender.user_type not in allowed_user_types or recipient.user_type not in allowed_user_types:
            return False, '当前账号类型不支持聊天'

        if sender.user_type == 'family':
            allowed_doctor_user_ids = self._get_allowed_family_doctor_user_ids(sender)
            if recipient.user_type != 'doctor' or recipient.id not in allowed_doctor_user_ids:
                return False, '家属只能联系已接诊绑定病人的医生'

        if recipient.user_type == 'family':
            allowed_doctor_user_ids = self._get_allowed_family_doctor_user_ids(recipient)
            if sender.user_type != 'doctor' or sender.id not in allowed_doctor_user_ids:
                return False, '当前医生无权联系该家属'

        return True, ''

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记通知为已读"""
        notification = self.get_object()
        if notification.recipient != request.user:
            return Response({'error': '无权操作'}, status=status.HTTP_403_FORBIDDEN)

        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """标记所有通知为已读"""
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'message': '所有通知已标记为已读'})

    @action(detail=False, methods=['get'])
    def chat_sessions(self, request):
        """获取聊天会话列表，按对话对象分组，返回每个对话的最新消息和未读数。"""
        user = request.user
        chat_msgs = (
            Notification.objects
            .filter(
                Q(recipient=user, notification_type__in=['chat', 'message']) |
                Q(sender=user, notification_type__in=['chat', 'message'])
            )
            .select_related('sender', 'recipient')
            .order_by('-created_at')
        )

        sessions = {}
        for msg in chat_msgs:
            partner = msg.sender if msg.recipient_id == user.id else msg.recipient
            if not partner:
                continue
            pid = partner.id
            if pid not in sessions:
                sessions[pid] = {
                    'partner_id': pid,
                    'partner_name': partner.name or partner.username,
                    'partner_role': partner.user_type,
                    'last_message': msg.content[:80] if msg.content else '',
                    'last_time': msg.created_at.isoformat() if msg.created_at else '',
                    'unread': 0,
                }
            # 统计未读（只算对方发给我的且未读的）
            if msg.recipient_id == user.id and not msg.is_read:
                sessions[pid]['unread'] += 1

        result = sorted(sessions.values(), key=lambda s: s['last_time'], reverse=True)
        return Response(result)

    @action(detail=False, methods=['get'])
    def chat_messages(self, request):
        """获取聊天消息（包括发送和接收的）"""
        user = request.user
        partner_user_id = request.query_params.get('partner_user_id') or request.query_params.get('partner_id')

        messages = Notification.objects.filter(
            Q(recipient=user, notification_type__in=['chat', 'message']) |
            Q(sender=user, notification_type__in=['chat', 'message'])
        ).select_related('sender', 'recipient').distinct()

        if partner_user_id:
            try:
                partner_user_id = int(partner_user_id)
            except (TypeError, ValueError):
                return Response({'error': '无效的聊天对象ID'}, status=status.HTTP_400_BAD_REQUEST)

            messages = messages.filter(
                Q(sender_id=partner_user_id, recipient=user) |
                Q(sender=user, recipient_id=partner_user_id)
            )

            if user.user_type == 'family':
                allowed_doctor_user_ids = self._get_allowed_family_doctor_user_ids(user)
                if partner_user_id not in allowed_doctor_user_ids:
                    return Response({'error': '无权查看与该医生的会话'}, status=status.HTTP_403_FORBIDDEN)

            elif user.user_type == 'doctor':
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    partner = User.objects.get(id=partner_user_id)
                except User.DoesNotExist:
                    return Response({'error': '聊天对象不存在'}, status=status.HTTP_404_NOT_FOUND)

                can_chat, error_message = self._can_send_chat_message(user, partner)
                if not can_chat:
                    return Response({'error': error_message}, status=status.HTTP_403_FORBIDDEN)

        messages = messages.order_by('created_at')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def send_chat_message(self, request):
        """发送聊天消息（医生、患者、家属都可按权限发送）"""
        recipient_id = request.data.get('recipient_id')
        content = request.data.get('content', '')

        if not recipient_id:
            return Response({'error': '接收者ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        if not content.strip():
            return Response({'error': '消息内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            try:
                recipient_id_int = int(recipient_id)
            except (ValueError, TypeError):
                return Response({'error': f'无效的接收者ID: {recipient_id}'}, status=status.HTTP_400_BAD_REQUEST)

            recipient = User.objects.get(id=recipient_id_int)
            can_chat, error_message = self._can_send_chat_message(request.user, recipient)
            if not can_chat:
                return Response({'error': error_message}, status=status.HTTP_403_FORBIDDEN)

            sender_display_name = request.user.name or request.user.username
            sender_role_label = '家属' if request.user.user_type == 'family' else ('医生' if request.user.user_type == 'doctor' else '患者')

            notification = Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notification_type='chat',
                title=f'{sender_role_label} {sender_display_name} 发来的消息',
                content=content.strip()
            )

            return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error': '接收者不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_to_patient(self, request):
        """医生发送通知给患者（保留兼容性）"""
        if request.user.user_type != 'doctor':
            return Response({'error': '只有医生可以发送通知'}, status=status.HTTP_403_FORBIDDEN)

        patient_id = request.data.get('patient_id')
        medical_record_id = request.data.get('medical_record_id')
        title = request.data.get('title', '报告通知')
        content = request.data.get('content', '')
        notification_type = request.data.get('notification_type', 'report_shared')

        if not patient_id:
            return Response({'error': '患者ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from patients.models import Patient
            try:
                patient_id_int = int(patient_id)
            except (ValueError, TypeError):
                return Response({'error': f'无效的患者ID: {patient_id}'}, status=status.HTTP_400_BAD_REQUEST)

            patient = Patient.objects.get(id=patient_id_int)

            medical_record = None
            if medical_record_id:
                from medical_records.models import MedicalRecord
                try:
                    try:
                        medical_record_id_int = int(medical_record_id)
                    except (ValueError, TypeError):
                        medical_record = None
                    else:
                        medical_record = MedicalRecord.objects.get(id=medical_record_id_int)
                        if medical_record.patient != patient:
                            return Response({'error': '医疗记录与患者不匹配'}, status=status.HTTP_400_BAD_REQUEST)
                except MedicalRecord.DoesNotExist:
                    medical_record = None

            notification = Notification.objects.create(
                recipient=patient.user,
                sender=request.user,
                notification_type=notification_type,
                title=title,
                content=content or f"您的检查报告已生成，请及时查看。",
                medical_record=medical_record
            )

            return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)

        except Patient.DoesNotExist:
            return Response({'error': '患者不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
