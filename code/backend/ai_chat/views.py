from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import uuid
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatSessionListSerializer, ChatMessageSerializer, ChatMessageCreateSerializer

class ChatSessionViewSet(viewsets.ModelViewSet):
    """AI聊天会话管理视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return ChatSession.objects.filter(patient__user=user)
        elif user.user_type == 'doctor':
            # 医生只能查看与自己存在医患关系的患者的会话
            # （via 已接诊的 MedicalRecord 或 已 accepted/completed 的 Appointment）
            from medical_records.models import MedicalRecord
            from appointments.models import Appointment
            related_patient_ids = set(
                MedicalRecord.objects
                .filter(doctor__user=user)
                .values_list('patient_id', flat=True)
            ) | set(
                Appointment.objects
                .filter(doctor__user=user, status__in=['accepted', 'completed'])
                .values_list('patient_id', flat=True)
            )
            return ChatSession.objects.filter(patient_id__in=related_patient_ids)
        return ChatSession.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionSerializer
    
    def create(self, request, *args, **kwargs):
        """创建新的聊天会话"""
        if request.user.user_type != 'patient':
            return Response({'error': '只有病人可以创建聊天会话'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            patient = request.user.patient_profile
        except:
            return Response({'error': '请先完善病人档案'}, status=status.HTTP_400_BAD_REQUEST)
        
        session_id = str(uuid.uuid4())
        title = request.data.get('title', '新对话')
        
        session = ChatSession.objects.create(
            patient=patient,
            session_id=session_id,
            title=title
        )
        
        # 添加欢迎消息
        welcome_message = ChatMessage.objects.create(
            session=session,
            message_type='ai',
            content='您好！我是您的AI医疗助手，有什么可以帮助您的吗？'
        )
        
        return Response(ChatSessionSerializer(session).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """发送消息给AI"""
        session = self.get_object()
        
        if request.user.user_type != 'patient':
            return Response({'error': '只有病人可以发送消息'}, status=status.HTTP_403_FORBIDDEN)
        
        content = request.data.get('content', '')
        if not content:
            return Response({'error': '消息内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存用户消息
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=content
        )
        
        # 调用AI服务获取回复
        try:
            # 获取会话历史
            recent_messages = session.messages.order_by('-timestamp')[:10]
            message_history = []
            for msg in reversed(recent_messages):
                message_history.append({
                    'role': 'user' if msg.message_type == 'user' else 'assistant',
                    'content': msg.content
                })
            
            ai_response = requests.post(
                f"{settings.FLASK_ML_SERVICE_URL}/chat",
                json={
                    'messages': message_history,
                    'patient_info': {
                        'name': session.patient.name,
                        'age': session.patient.age,
                        'medical_history': session.patient.medical_history
                    }
                }
            )
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                ai_content = ai_data.get('response', '抱歉，我暂时无法回答您的问题。')
                
                # 保存AI回复
                ai_message = ChatMessage.objects.create(
                    session=session,
                    message_type='ai',
                    content=ai_content
                )
                
                return Response({
                    'user_message': ChatMessageSerializer(user_message).data,
                    'ai_message': ChatMessageSerializer(ai_message).data
                })
            else:
                return Response({'error': 'AI服务暂时不可用'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except requests.RequestException:
            return Response({'error': '无法连接到AI服务'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话的所有消息"""
        session = self.get_object()
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def update_title(self, request, pk=None):
        """更新会话标题"""
        session = self.get_object()
        title = request.data.get('title', '')
        
        if not title:
            return Response({'error': '标题不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        session.title = title
        session.save()
        
        return Response({'message': '标题更新成功'})
