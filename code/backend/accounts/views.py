from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .models import User, Feedback

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': '注册成功'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """用户登录"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': '登录成功'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """用户登出"""
    try:
        request.user.auth_token.delete()
        return Response({'message': '登出成功'})
    except:
        return Response({'message': '登出失败'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """获取用户信息"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """更新用户信息"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """修改密码：校验原密码后写入新密码并刷新 token。"""
    old_password = request.data.get('old_password', '')
    new_password = request.data.get('new_password', '')

    if not old_password:
        return Response({'error': '请输入原密码'}, status=status.HTTP_400_BAD_REQUEST)
    if not new_password or len(new_password) < 6:
        return Response({'error': '新密码至少 6 位'}, status=status.HTTP_400_BAD_REQUEST)
    if len(new_password) > 32:
        return Response({'error': '新密码过长'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    if not user.check_password(old_password):
        return Response({'error': '原密码不正确'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save(update_fields=['password'])

    # 旧 token 失效，签发新 token 让用户继续使用
    Token.objects.filter(user=user).delete()
    new_token = Token.objects.create(user=user)

    return Response({
        'message': '密码修改成功',
        'token': new_token.key
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """提交意见反馈。"""
    content = (request.data.get('content') or '').strip()
    if not content:
        return Response({'error': '反馈内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    if len(content) > 500:
        return Response({'error': '反馈内容过长（最多 500 字）'}, status=status.HTTP_400_BAD_REQUEST)

    feedback = Feedback.objects.create(user=request.user, content=content)
    return Response({
        'message': '反馈提交成功，感谢您的支持',
        'id': feedback.id,
        'created_at': feedback.created_at
    }, status=status.HTTP_201_CREATED)
