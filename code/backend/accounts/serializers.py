from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'user_type', 'name', 'phone')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("密码不匹配")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # 注册成功后，自动创建对应的档案（医生或患者）
        user_type = validated_data.get('user_type', 'patient')
        
        if user_type == 'doctor':
            # 自动创建医生档案
            from doctors.models import Doctor
            try:
                Doctor.objects.create(
                    user=user,
                    name=user.name or user.username,
                    license_number=f'DOC{user.id:06d}',  # 临时执业证号，后续可修改
                    specialty='general',  # 默认为全科
                    hospital='待完善',
                    department='待完善',
                    title='待完善',
                    phone=user.phone or '',
                    email=user.email or '',
                    bio='',
                    is_verified=True  # 当前项目没有审核后台，注册医生默认可被患者挂诊页看到
                )
                print(f"✅ 为医生用户 {user.username} 自动创建档案")
            except Exception as e:
                print(f"⚠️ 创建医生档案失败: {str(e)}")
                # 不抛出异常，允许用户后续手动创建
            
        elif user_type == 'patient':
            # 自动创建患者档案
            from patients.models import Patient
            from datetime import date
            import time
            try:
                # 计算一个默认生日（约30岁）
                default_birth_date = date(date.today().year - 30, 1, 1)
                
                # 生成唯一的临时身份证号（使用时间戳+用户ID确保唯一性）
                import random
                temp_id_card = f'TEMP{int(time.time())}{user.id:04d}{random.randint(100, 999)}'
                
                Patient.objects.create(
                    user=user,
                    name=user.name or user.username,
                    gender='M',  # 默认男性，后续可修改
                    birth_date=default_birth_date,
                    id_card=temp_id_card,  # 临时身份证号，后续必须修改为真实身份证
                    phone=user.phone or '',
                    address='待完善',
                    emergency_contact='',
                    emergency_phone=''
                )
                print(f"✅ 为患者用户 {user.username} 自动创建档案")
            except Exception as e:
                print(f"⚠️ 创建患者档案失败: {str(e)}")
                # 不抛出异常，允许用户后续手动创建
        elif user_type == 'family':
            from families.models import Family
            try:
                Family.objects.create(
                    user=user,
                    name=user.name or user.username,
                    phone=user.phone or '',
                    relationship_note=''
                )
                print(f"Created family profile for {user.username}")
            except Exception as e:
                print(f"Failed to create family profile for {user.username}: {str(e)}")
        
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('必须提供用户名和密码')
        
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'name', 'phone', 'avatar', 'created_at')
        read_only_fields = ('id', 'created_at')
