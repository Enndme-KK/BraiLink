#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化演示数据脚本

创建一些示例账户和数据，方便测试使用
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain_tumor_api.settings')
django.setup()

from accounts.models import User
from patients.models import Patient
from doctors.models import Doctor
from datetime import date

def create_demo_users():
    """创建演示用户"""
    print("\n" + "="*60)
    print("  创建演示账户")
    print("="*60 + "\n")
    
    demo_users = []
    
    # 1. 管理员账户
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            user_type='doctor',
            name='系统管理员',
            phone='13800000000'
        )
        demo_users.append({
            'type': '管理员',
            'username': 'admin',
            'password': 'admin123',
            'name': '系统管理员'
        })
        print("✅ 创建管理员账户: admin")
    else:
        print("⏭️  管理员账户已存在")
    
    # 2. 医生账户
    doctor_data = [
        {
            'username': 'doctor1',
            'email': 'doctor1@example.com',
            'password': 'doctor123',
            'name': '张医生',
            'phone': '13800000001',
            'hospital': '华北医院',
            'department': '神经外科',
            'title': '主任医师',
            'specialty': 'neurosurgery',
            'license_number': 'DOC001',
            'bio': '擅长脑肿瘤诊断与治疗'
        },
        {
            'username': 'doctor2',
            'email': 'doctor2@example.com',
            'password': 'doctor123',
            'name': '李医生',
            'phone': '13800000002',
            'hospital': '华北医院',
            'department': '影像科',
            'title': '副主任医师',
            'specialty': 'radiology',
            'license_number': 'DOC002',
            'bio': '擅长MRI影像分析'
        },
    ]
    
    for data in doctor_data:
        if not User.objects.filter(username=data['username']).exists():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                user_type='doctor',
                name=data['name'],
                phone=data['phone']
            )
            # 创建医生档案
            Doctor.objects.create(
                user=user,
                name=data['name'],
                license_number=data['license_number'],
                specialty=data['specialty'],
                hospital=data['hospital'],
                department=data['department'],
                title=data['title'],
                phone=data['phone'],
                email=data['email'],
                bio=data.get('bio', ''),
                is_verified=True
            )
            demo_users.append({
                'type': '医生',
                'username': data['username'],
                'password': data['password'],
                'name': data['name']
            })
            print(f"✅ 创建医生账户: {data['username']} - {data['name']}")
        else:
            print(f"⏭️  医生账户已存在: {data['username']}")
    
    # 3. 患者账户
    patient_data = [
        {
            'username': 'patient1',
            'email': 'patient1@example.com',
            'password': 'patient123',
            'name': '王先生',
            'phone': '13900000001',
            'gender': 'M',
            'birth_date': date(1985, 6, 15),
            'id_card': '110101198506150011',
            'address': '北京市朝阳区',
            'emergency_contact': '李女士',
            'emergency_phone': '13900000002'
        },
        {
            'username': 'patient2',
            'email': 'patient2@example.com',
            'password': 'patient123',
            'name': '赵女士',
            'phone': '13900000003',
            'gender': 'F',
            'birth_date': date(1990, 3, 20),
            'id_card': '110101199003200022',
            'address': '北京市海淀区',
            'emergency_contact': '赵先生',
            'emergency_phone': '13900000004'
        },
    ]
    
    for data in patient_data:
        if not User.objects.filter(username=data['username']).exists():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                user_type='patient',
                name=data['name'],
                phone=data['phone']
            )
            # 创建患者档案
            Patient.objects.create(
                user=user,
                name=data['name'],
                gender=data['gender'],
                birth_date=data['birth_date'],
                id_card=data['id_card'],
                phone=data['phone'],
                address=data['address'],
                emergency_contact=data['emergency_contact'],
                emergency_phone=data['emergency_phone']
            )
            demo_users.append({
                'type': '患者',
                'username': data['username'],
                'password': data['password'],
                'name': data['name']
            })
            print(f"✅ 创建患者账户: {data['username']} - {data['name']}")
        else:
            print(f"⏭️  患者账户已存在: {data['username']}")
    
    # 打印账户信息
    if demo_users:
        print("\n" + "="*60)
        print("  演示账户信息")
        print("="*60 + "\n")
        
        for user in demo_users:
            print(f"【{user['type']}】")
            print(f"  用户名: {user['username']}")
            print(f"  密码: {user['password']}")
            print(f"  姓名: {user['name']}")
            print()
        
        print("-"*60)
        print("💡 提示: 请在首次登录后修改默认密码")
        print("="*60 + "\n")
    
    return len(demo_users)

def main():
    """主函数"""
    try:
        count = create_demo_users()
        if count > 0:
            print(f"\n✅ 成功创建 {count} 个演示账户\n")
        else:
            print("\n✅ 所有演示账户已存在\n")
        return 0
    except Exception as e:
        print(f"\n❌ 创建失败: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

