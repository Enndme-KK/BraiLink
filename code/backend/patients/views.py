from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Patient
from .serializers import PatientSerializer, PatientListSerializer

class PatientViewSet(viewsets.ModelViewSet):
    """病人管理视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return Patient.objects.filter(user=user)
        elif user.user_type == 'doctor':
            return Patient.objects.all()
        return Patient.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
    def create(self, request, *args, **kwargs):
        """创建病人档案"""
        if request.user.user_type != 'patient':
            return Response({'error': '只有病人可以创建档案'}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查是否已有档案
        try:
            existing_patient = request.user.patient_profile
            # 如果已有档案，返回错误提示使用更新接口
            return Response({
                'error': '您已有档案，请使用更新接口',
                'patient_id': existing_patient.id
            }, status=status.HTTP_400_BAD_REQUEST)
        except Patient.DoesNotExist:
            pass  # 没有档案，继续创建
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            patient = serializer.save()
            return Response(PatientSerializer(patient, context={'request': request}).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'创建档案失败: {str(e)}',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """更新病人档案"""
        if request.user.user_type != 'patient':
            return Response({'error': '只有病人可以更新档案'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            patient = self.get_object()
            # 确保只能更新自己的档案
            if patient.user != request.user:
                return Response({'error': '您只能更新自己的档案'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(patient, data=request.data, partial=kwargs.get('partial', False), context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            try:
                updated_patient = serializer.save()
                return Response(PatientSerializer(updated_patient, context={'request': request}).data, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                # 检查是否是身份证号重复错误
                if 'id_card' in str(e).lower() or 'unique' in str(e).lower():
                    return Response({
                        'error': '身份证号已被其他用户使用',
                        'detail': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
                return Response({
                    'error': f'更新档案失败: {str(e)}',
                    'detail': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        except Patient.DoesNotExist:
            return Response({'error': '未找到病人档案'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'更新档案失败: {str(e)}',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """获取当前用户的病人档案"""
        if request.user.user_type != 'patient':
            return Response({'error': '只有病人可以查看档案'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            patient = request.user.patient_profile
            serializer = PatientSerializer(patient, context={'request': request})
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response({'error': '未找到病人档案'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def medical_records(self, request, pk=None):
        """获取病人的医疗记录"""
        from medical_records.models import MedicalRecord
        from medical_records.serializers import MedicalRecordListSerializer

        patient = self.get_object()

        # 权限：患者只能看自己；医生看与自己有医患关系的；其他不可见
        user = request.user
        if user.user_type == 'patient' and patient.user_id != user.id:
            return Response({'error': '只能查看自己的病历'}, status=status.HTTP_403_FORBIDDEN)

        records = (
            MedicalRecord.objects
            .filter(patient=patient)
            .select_related('patient', 'patient__user', 'doctor', 'doctor__user')
            .prefetch_related('ct_scans')
            .order_by('-visit_date', '-created_at')
        )

        if user.user_type == 'doctor':
            from appointments.models import Appointment
            doctor_profile = getattr(user, 'doctor_profile', None)
            if not doctor_profile:
                return Response({'error': '未找到医生档案'}, status=status.HTTP_403_FORBIDDEN)
            has_relation = (
                records.filter(doctor=doctor_profile).exists()
                or Appointment.objects
                .filter(doctor=doctor_profile, patient=patient, status__in=['accepted', 'completed'])
                .exists()
            )
            if not has_relation:
                return Response({'error': '未与该患者建立医患关系'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalRecordListSerializer(records, many=True, context={'request': request})
        return Response({'medical_records': serializer.data})
