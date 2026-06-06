"""
Django管理命令：将数据库中的患者同步为医疗记录
为每个患者创建一个医疗记录，以便医生可以在首页看到并接诊
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from patients.models import Patient
from medical_records.models import MedicalRecord
import uuid


class Command(BaseCommand):
    help = '为数据库中的所有患者创建医疗记录，以便医生可以接诊'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制为所有患者创建记录，即使已有记录',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='跳过已有医疗记录的患者',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始同步患者到医疗记录...\n'))
        
        # 获取所有患者
        patients = Patient.objects.all()
        total_patients = patients.count()
        
        if total_patients == 0:
            self.stdout.write(self.style.WARNING('数据库中没有患者数据'))
            return
        
        self.stdout.write(f'找到 {total_patients} 个患者\n')
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for patient in patients:
            try:
                # 检查是否已有医疗记录
                existing_records = MedicalRecord.objects.filter(patient=patient)
                
                if existing_records.exists():
                    if options['skip_existing']:
                        self.stdout.write(
                            self.style.WARNING(f'  ⏭  跳过患者 {patient.name} (已有 {existing_records.count()} 条记录)')
                        )
                        skipped_count += 1
                        continue
                    elif not options['force']:
                        self.stdout.write(
                            self.style.WARNING(f'  ⏭  跳过患者 {patient.name} (已有记录，使用 --force 强制创建)')
                        )
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
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ 为患者 {patient.name} 创建医疗记录: {record_number}')
                )
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ 为患者 {patient.name} 创建记录失败: {str(e)}')
                )
                error_count += 1
        
        # 输出统计信息
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('同步完成！'))
        self.stdout.write(f'  总患者数: {total_patients}')
        self.stdout.write(self.style.SUCCESS(f'  成功创建: {created_count}'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'  跳过: {skipped_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  失败: {error_count}'))
        self.stdout.write('='*60 + '\n')
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ 已为 {created_count} 个患者创建医疗记录，医生现在可以在首页看到这些患者并选择接诊！'
                )
            )

