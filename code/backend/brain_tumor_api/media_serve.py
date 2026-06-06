"""
受保护的媒体文件服务视图。
生产环境下，CT 原图、AI 分割图、报告等敏感文件需要鉴权后才能访问。
新闻图片（media/news/）属于公开内容，无需鉴权。
"""
import os
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.views.static import serve as static_serve
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


# 公开可访问的子目录前缀（无需 token）
PUBLIC_PREFIXES = ('news/',)


def _authenticate_request(request):
    """尝试从 Authorization header 或 ?token= 查询参数中验证用户。"""
    # 1. 标准 Authorization: Token xxx
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Token '):
        token_key = auth_header[6:].strip()
    else:
        # 2. 查询参数 ?token=xxx（App 端 image src 无法设 header）
        token_key = request.GET.get('token', '').strip()

    if not token_key:
        return None

    from rest_framework.authtoken.models import Token
    try:
        token_obj = Token.objects.select_related('user').get(key=token_key)
        return token_obj.user
    except Token.DoesNotExist:
        return None


def protected_media_serve(request, path):
    """
    替代 django.views.static.serve，对敏感路径要求鉴权。
    公开路径（news/）直接放行。
    """
    # 公开内容直接 serve
    if any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
        return static_serve(request, path, document_root=settings.MEDIA_ROOT)

    # 敏感内容需要鉴权
    user = _authenticate_request(request)
    if user is None:
        return HttpResponseForbidden('认证失败：请提供有效的 token')

    if not user.is_active:
        return HttpResponseForbidden('账户已被禁用')

    # 文件存在性检查
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.isfile(full_path):
        raise Http404('文件不存在')

    # 防止路径穿越
    full_path = os.path.realpath(full_path)
    media_root = os.path.realpath(str(settings.MEDIA_ROOT))
    if not full_path.startswith(media_root):
        raise Http404('非法路径')

    return static_serve(request, path, document_root=settings.MEDIA_ROOT)
