from rest_framework import serializers
from .models import Patient
from accounts.serializers import UserSerializer

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # 如果更新身份证号，检查是否与其他用户冲突
        if 'id_card' in validated_data:
            new_id_card = validated_data['id_card']
            # 如果新身份证号与当前不同，检查是否已被其他用户使用
            if new_id_card != instance.id_card:
                if Patient.objects.filter(id_card=new_id_card).exclude(id=instance.id).exists():
                    raise serializers.ValidationError({
                        'id_card': '该身份证号已被其他用户使用'
                    })
        return super().update(instance, validated_data)

class PatientListSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    id_card = serializers.CharField(read_only=True)
    medical_history = serializers.CharField(read_only=True)
    has_family = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ('id', 'user', 'name', 'gender', 'age', 'phone', 'id_card', 'medical_history', 'created_at', 'has_family')

    def get_has_family(self, obj):
        return obj.family_bindings.exists()
