from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalRecordViewSet, get_medical_news, get_today_patients

router = DefaultRouter()
router.register(r'', MedicalRecordViewSet, basename='medical-record')

urlpatterns = [
    path('', include(router.urls)),
    path('home/news/', get_medical_news, name='medical-news'),  # 获取医学界新闻
    path('home/today-patients/', get_today_patients, name='today-patients'),  # 获取今日就诊患者
]
