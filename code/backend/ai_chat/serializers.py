from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ('timestamp',)

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'session_id')

class ChatSessionListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ('id', 'session_id', 'title', 'patient_name', 'last_message', 'created_at', 'updated_at', 'is_active')
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'message_type': last_msg.message_type,
                'timestamp': last_msg.timestamp
            }
        return None

class ChatMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('content', 'message_type')
    
    def create(self, validated_data):
        validated_data['session'] = self.context['session']
        return super().create(validated_data)
