#!/usr/bin/env python
"""
快速脚本：将数据库中的患者同步为医疗记录
运行方式：python sync_patients.py
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain_tumor_api.settings')
django.setup()

from django.utils import timezone
from patients.models import Patient
from medical_records.models import MedicalRecord
import uuid

def sync_patients_to_records(force=False, skip_existing=False):
    """为所有患者创建医疗记录"""
    print('='*60)
    print('开始同步患者到医疗记录...\n')
    
    # 获取所有患者
    patients = Patient.objects.all()
    total_patients = patients.count()
    
    if total_patients == 0:
        print('⚠️  数据库中没有患者数据')
        return
    
    print(f'找到 {total_patients} 个患者\n')
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for patient in patients:
        try:
            # 检查是否已有医疗记录
            existing_records = MedicalRecord.objects.filter(patient=patient)
            
            if existing_records.exists():
                if skip_existing:
                    print(f'  ⏭  跳过患者 {patient.name} (已有 {existing_records.count()} 条记录)')
                    skipped_count += 1
                    continue
                elif not force:
                    print(f'  ⏭  跳过患者 {patient.name} (已有记录，如需强制创建请修改脚本参数)')
                    skipped_count += 1
                    continue
            
            # 生成唯一的记录号
            record_number = f"MR{str(uuid.uuid4())[:8].upper()}"
            
            # 确保记录号唯一
            while MedicalRecord.objects.filter(record_number=record_number).exists():
                record_number = f"MR{str(uuid.uuid4())[:8].upper()}"
            
            # 创建医疗记录
            medical_record = MedicalRecord.objects.create(
                patient=patient,
                doctor=None,  # 初始状态未分配医生
                record_number=record_number,
                visit_date=timezone.now(),  # 就诊日期设为当前时间
                department='',  # 可以后续填写
                bed_num='',
                check_project='',
                position='',
                symptoms='',  # 可以后续填写
                diagnosis='',
                treatment_plan='',
                notes='',
                status='pending',  # 初始状态为待处理
            )
            
            print(f'  ✓ 为患者 {patient.name} 创建医疗记录: {record_number}')
            created_count += 1
            
        except Exception as e:
            print(f'  ✗ 为患者 {patient.name} 创建记录失败: {str(e)}')
            error_count += 1
    
    # 输出统计信息
    print('\n' + '='*60)
    print('同步完成！')
    print(f'  总患者数: {total_patients}')
    print(f'  成功创建: {created_count}')
    if skipped_count > 0:
        print(f'  跳过: {skipped_count}')
    if error_count > 0:
        print(f'  失败: {error_count}')
    print('='*60 + '\n')
    
    if created_count > 0:
        print(f'✅ 已为 {created_count} 个患者创建医疗记录，医生现在可以在首页看到这些患者并选择接诊！\n')

if __name__ == '__main__':
    # 默认跳过已有记录的患者，如需强制创建，将 skip_existing 改为 False
    sync_patients_to_records(force=False, skip_existing=True)

