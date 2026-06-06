#!/usr/bin/env python
"""
数据库查看工具 - 实时查看后端数据库中的所有数据
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain_tumor_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from medical_records.models import MedicalRecord, CTScan
from ai_chat.models import ChatSession, ChatMessage

User = get_user_model()

def print_separator(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def view_users():
    """查看用户数据"""
    print_separator("用户列表 (User)")
    users = User.objects.all()
    if users.exists():
        for user in users:
            print(f"\n[用户ID: {user.id}]")
            print(f"  用户名: {user.username}")
            print(f"  姓名: {user.name or '(未设置)'}")
            print(f"  邮箱: {user.email}")
            print(f"  用户类型: {user.get_user_type_display()}")
            print(f"  手机: {user.phone or '(未设置)'}")
            print(f"  创建时间: {user.created_at}")
    else:
        print("  (暂无用户数据)")

def view_patients():
    """查看患者数据"""
    print_separator("患者列表 (Patient)")
    patients = Patient.objects.all()
    if patients.exists():
        for patient in patients:
            print(f"\n[患者ID: {patient.id}]")
            print(f"  姓名: {patient.name}")
            print(f"  用户: {patient.user.username}")
            print(f"  性别: {patient.get_gender_display()}")
            print(f"  年龄: {patient.age}岁")
            print(f"  身份证: {patient.id_card}")
            print(f"  电话: {patient.phone}")
            print(f"  创建时间: {patient.created_at}")
    else:
        print("  (暂无患者数据)")

def view_doctors():
    """查看医生数据"""
    print_separator("医生列表 (Doctor)")
    doctors = Doctor.objects.all()
    if doctors.exists():
        for doctor in doctors:
            print(f"\n[医生ID: {doctor.id}]")
            print(f"  姓名: {doctor.name}")
            print(f"  用户: {doctor.user.username}")
            print(f"  执业证号: {doctor.license_number}")
            print(f"  专科: {doctor.get_specialty_display()}")
            print(f"  医院: {doctor.hospital}")
            print(f"  科室: {doctor.department}")
            print(f"  职称: {doctor.title}")
            print(f"  已验证: {'是' if doctor.is_verified else '否'}")
            print(f"  创建时间: {doctor.created_at}")
    else:
        print("  (暂无医生数据)")

def view_medical_records():
    """查看医疗记录"""
    print_separator("医疗记录列表 (MedicalRecord)")
    records = MedicalRecord.objects.all().select_related('patient', 'doctor')
    if records.exists():
        for record in records:
            print(f"\n[记录ID: {record.id}]")
            print(f"  记录编号: {record.record_number}")
            print(f"  患者: {record.patient.name}")
            print(f"  医生: {record.doctor.name if record.doctor else '(未分配)'}")
            print(f"  就诊日期: {record.visit_date}")
            print(f"  状态: {record.get_status_display()}")
            print(f"  诊断: {record.diagnosis or '(未填写)'}")
            print(f"  创建时间: {record.created_at}")
            
            # 查看关联的CT扫描
            ct_scans = record.ct_scans.all()
            if ct_scans.exists():
                print(f"  CT扫描数量: {ct_scans.count()}")
    else:
        print("  (暂无医疗记录)")

def view_ct_scans():
    """查看CT扫描记录"""
    print_separator("CT扫描列表 (CTScan)")
    scans = CTScan.objects.all().select_related('medical_record')
    if scans.exists():
        for scan in scans:
            print(f"\n[CT扫描ID: {scan.id}]")
            print(f"  医疗记录: {scan.medical_record.record_number}")
            print(f"  扫描模式: {scan.scan_mode}")
            print(f"  扫描日期: {scan.scan_date}")
            print(f"  检测到肿瘤: {'是' if scan.tumor_detected else '否'}")
            print(f"  置信度: {scan.confidence_score:.2%}")
            print(f"  已验证: {'是' if scan.is_verified else '否'}")
    else:
        print("  (暂无CT扫描记录)")

def view_chat_sessions():
    """查看AI聊天会话"""
    print_separator("AI聊天会话列表 (ChatSession)")
    sessions = ChatSession.objects.all().select_related('patient')
    if sessions.exists():
        for session in sessions:
            print(f"\n[会话ID: {session.id}]")
            print(f"  会话编号: {session.session_id}")
            print(f"  患者: {session.patient.name}")
            print(f"  标题: {session.title}")
            print(f"  消息数量: {session.messages.count()}")
            print(f"  创建时间: {session.created_at}")
            print(f"  是否活跃: {'是' if session.is_active else '否'}")
    else:
        print("  (暂无聊天会话)")

def view_statistics():
    """查看统计信息"""
    print_separator("数据库统计信息")
    print(f"  用户总数: {User.objects.count()}")
    print(f"  - 患者用户: {User.objects.filter(user_type='patient').count()}")
    print(f"  - 医生用户: {User.objects.filter(user_type='doctor').count()}")
    print(f"  患者档案数: {Patient.objects.count()}")
    print(f"  医生档案数: {Doctor.objects.count()}")
    print(f"  医疗记录数: {MedicalRecord.objects.count()}")
    print(f"  CT扫描数: {CTScan.objects.count()}")
    print(f"  聊天会话数: {ChatSession.objects.count()}")
    print(f"  聊天消息数: {ChatMessage.objects.count()}")

def view_test_accounts():
    """查看测试账户信息"""
    print_separator("测试账户登录信息")
    
    # 医生账户
    doctors = User.objects.filter(user_type='doctor', username__in=['doctor1', 'doctor2'])
    if doctors.exists():
        print("\n【医生账户】")
        for user in doctors:
            print(f"  用户名: {user.username}")
            print(f"  密码: doctor123")
            print(f"  姓名: {user.name}")
            print()
    
    # 患者账户
    patients = User.objects.filter(user_type='patient', username__in=['patient1', 'patient2'])
    if patients.exists():
        print("【患者账户】")
        for user in patients:
            print(f"  用户名: {user.username}")
            print(f"  密码: patient123")
            print(f"  姓名: {user.name}")
            print()
    
    # 管理员账户
    admin = User.objects.filter(username='admin').first()
    if admin:
        print("【管理员账户】")
        print(f"  用户名: admin")
        print(f"  密码: admin123")
        print()

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  🗄️  颅内管家数据库查看工具")
    print("="*60)
    print(f"\n数据库路径: {os.path.abspath('db.sqlite3')}")
    
    # 查看统计信息
    view_statistics()
    
    # 查看各表数据
    view_users()
    view_patients()
    view_doctors()
    view_medical_records()
    view_ct_scans()
    view_chat_sessions()
    
    # 查看测试账户
    view_test_accounts()
    
    print("\n" + "="*60)
    print("  查看完成！")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()

