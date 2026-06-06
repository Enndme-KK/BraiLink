"""
ML 服务路由
"""
from django.urls import path
from . import views

urlpatterns = [
    # MRI图像分割
    path('analyze_ct', views.analyze_ct, name='analyze_ct'),
    path('capture_camera', views.capture_camera, name='capture_camera'),
    
    # AI聊天
    path('chat', views.chat, name='ml_chat'),
    # AI聊天（流式SSE）
    path('chat/stream', views.chat_stream, name='ml_chat_stream'),
    
    # 健康检查
    path('health', views.health_check, name='ml_health'),
    
    # 模型信息
    path('model_info', views.model_info, name='ml_model_info'),
]

