"""
URL configuration for brain_tumor_api project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/families/', include('families.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/medical-records/', include('medical_records.urls')),
    path('api/ai-chat/', include('ai_chat.urls')),
    path('api/ml/', include('ml_service.urls')),  # ML服务路由
    path('api/notifications/', include('notifications.urls')),  # 通知路由
]

if settings.DEBUG:
    # 先添加对news目录的特殊处理（更具体的路由要放在前面，避免被通用MEDIA路由覆盖）
    news_media_root = os.path.join(settings.MEDIA_ROOT, 'news')
    if os.path.exists(news_media_root):
        urlpatterns += [
            re_path(r'^media/news/(?P<path>.*)$', serve, {
                'document_root': news_media_root,
                'show_indexes': False,
            }),
        ]
    
    # 然后添加通用的MEDIA和STATIC文件服务
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # 输出文件现在统一保存在 MEDIA_ROOT/outputs 下，直接通过 MEDIA_URL 提供（无需单独路由）

# 生产环境：敏感媒体文件需鉴权访问（CT 原图、AI 分割图、报告等）
if not settings.DEBUG:
    from brain_tumor_api.media_serve import protected_media_serve
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', protected_media_serve),
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': False,
        }),
    ]
