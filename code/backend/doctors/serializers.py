from rest_framework import serializers
from .models import Doctor
from accounts.serializers import UserSerializer

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'is_verified')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DoctorListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Doctor
        fields = ('id', 'name', 'specialty', 'hospital', 'department', 'title', 'is_verified', 'user')
