from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserSerializer
from families.models import FamilyPatientBinding
from medical_records.models import MedicalRecord


class NotificationSerializer(serializers.ModelSerializer):
    sender_info = UserSerializer(source='sender', read_only=True)
    recipient_info = UserSerializer(source='recipient', read_only=True)
    medical_record_id = serializers.IntegerField(source='medical_record.id', read_only=True)
    sender_user_type = serializers.CharField(source='sender.user_type', read_only=True, default='')
    recipient_user_type = serializers.CharField(source='recipient.user_type', read_only=True, default='')
    sender_display_name = serializers.SerializerMethodField()
    recipient_display_name = serializers.SerializerMethodField()
    family_patient_name = serializers.SerializerMethodField()
    family_relationship = serializers.SerializerMethodField()
    chat_context_subtitle = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id', 'recipient', 'sender', 'sender_info', 'recipient_info', 'notification_type', 'title',
            'content', 'is_read', 'medical_record', 'medical_record_id', 'created_at', 'read_at',
            'sender_user_type', 'recipient_user_type', 'sender_display_name', 'recipient_display_name',
            'family_patient_name', 'family_relationship', 'chat_context_subtitle'
        )
        read_only_fields = ('created_at', 'read_at')

    def _get_family_chat_context(self, obj):
        sender = getattr(obj, 'sender', None)
        recipient = getattr(obj, 'recipient', None)
        if not sender or not recipient:
            return None

        family_user = None
        doctor_user = None
        if getattr(sender, 'user_type', '') == 'family' and getattr(recipient, 'user_type', '') == 'doctor':
            family_user = sender
            doctor_user = recipient
        elif getattr(sender, 'user_type', '') == 'doctor' and getattr(recipient, 'user_type', '') == 'family':
            family_user = recipient
            doctor_user = sender
        else:
            return None

        family_profile = getattr(family_user, 'family_profile', None)
        if not family_profile:
            return None

        bindings = list(
            FamilyPatientBinding.objects
            .filter(family=family_profile)
            .select_related('patient', 'patient__user')
            .order_by('-created_at')
        )
        if not bindings:
            return None

        patient_ids = [binding.patient_id for binding in bindings]
        shared_record = (
            MedicalRecord.objects
            .filter(patient_id__in=patient_ids, doctor__user=doctor_user)
            .select_related('patient', 'patient__user')
            .order_by('-visit_date', '-created_at')
            .first()
        )
        if not shared_record:
            return None

        matched_binding = next((binding for binding in bindings if binding.patient_id == shared_record.patient_id), None)
        patient_name = getattr(shared_record.patient, 'name', '') or getattr(shared_record.patient.user, 'name', '') or getattr(shared_record.patient.user, 'username', '')
        relationship = matched_binding.relationship if matched_binding else ''
        return {
            'patient_name': patient_name,
            'relationship': relationship
        }

    def get_sender_display_name(self, obj):
        if not obj.sender:
            return ''
        return obj.sender.name or obj.sender.username

    def get_recipient_display_name(self, obj):
        if not obj.recipient:
            return ''
        return obj.recipient.name or obj.recipient.username

    def get_family_patient_name(self, obj):
        context = self._get_family_chat_context(obj)
        return context['patient_name'] if context else ''

    def get_family_relationship(self, obj):
        context = self._get_family_chat_context(obj)
        return context['relationship'] if context else ''

    def get_chat_context_subtitle(self, obj):
        context = self._get_family_chat_context(obj)
        if not context or not context['patient_name']:
            return ''
        return f"关于患者：{context['patient_name']}"
