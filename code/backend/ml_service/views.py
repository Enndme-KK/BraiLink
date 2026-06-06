"""
ML 服务视图
整合了图像分割和 AI 聊天功能
"""
import os
import time
from django.conf import settings
from django.http import JsonResponse, FileResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from werkzeug.utils import secure_filename
from datetime import datetime
import json

from .prediction import (
    preprocess_mri_image,
    predict_segmentation,
    create_visualization,
    generate_segmentation_report,
    validate_medical_scan_image,
    SCAN_MODES
)
from .deepseek_client import chat_with_deepseek, chat_with_deepseek_stream
from .models_loader import get_device

# 配置输出目录 - 统一保存到 image_predict/output
# 获取backend目录，然后向上两级到项目根目录，再进入image_predict/output
# 将输出目录统一放在 MEDIA_ROOT/outputs，避免依赖仓库目录结构
OUTPUT_FOLDER = os.path.join(settings.MEDIA_ROOT, 'outputs')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

CAPTURE_FOLDER = os.path.join(settings.MEDIA_ROOT, 'camera_captures')
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

print(f"🔧 ML输出目录: {OUTPUT_FOLDER}")


def _build_segmentation_result(image_path, scan_mode):
    """Run the existing MRI segmentation pipeline on an image file."""
    validation = validate_medical_scan_image(image_path)
    if not validation.get('is_medical_scan'):
        return None, validation

    image_data = preprocess_mri_image(image_path, scan_mode)
    pred_result = predict_segmentation(image_data, scan_mode)
    visualization_filename = create_visualization(
        image_data,
        pred_result['segmentation_mask'],
        scan_mode,
        OUTPUT_FOLDER
    )
    analysis = generate_segmentation_report(pred_result)

    processed_image_url = None
    if visualization_filename:
        processed_image_url = f"{settings.MEDIA_URL}outputs/{visualization_filename}"

    return {
        'tumor_detected': pred_result['tumor_detected'],
        'tumor_area': pred_result['tumor_area'],
        'confidence_score': pred_result['confidence_score'],
        'scan_mode': pred_result['scan_mode'],
        'analysis': analysis,
        'tumor_regions_count': len(pred_result['tumor_regions']),
        'processed_image': processed_image_url,
        'tumor_percentage': pred_result.get('tumor_percentage', 0),
        'class_statistics': pred_result.get('class_statistics', {}),
        'medical_validation': validation
    }, validation


def _save_frame_as_jpeg(cv2_module, frame, target_path):
    """Save a camera frame safely, including paths containing Chinese characters."""
    success, buffer = cv2_module.imencode(
        '.jpg',
        frame,
        [int(cv2_module.IMWRITE_JPEG_QUALITY), 95]
    )
    if not success:
        raise ValueError('相机图像编码失败，无法保存照片')

    with open(target_path, 'wb') as image_file:
        image_file.write(buffer.tobytes())


def _frame_quality(cv2_module, frame):
    """Measure whether a camera frame contains useful visual information."""
    if frame is None:
        return {
            'usable': False,
            'mean': 0.0,
            'std': 0.0,
            'min': 0,
            'max': 0,
            'bright_ratio': 0.0,
            'score': 0.0,
        }

    height, width = frame.shape[:2]
    gray = cv2_module.cvtColor(frame, cv2_module.COLOR_BGR2GRAY)
    mean_value = float(gray.mean())
    std_value = float(gray.std())
    min_value = int(gray.min())
    max_value = int(gray.max())
    bright_ratio = float((gray > 12).mean())
    score = mean_value + std_value * 2 + max_value * 0.15 + bright_ratio * 100

    # Fully black frames from capture cards are usually mean/std/max all near 0.
    usable = max_value > 18 and (std_value > 4 or bright_ratio > 0.01 or mean_value > 8)

    return {
        'usable': bool(usable),
        'mean': round(mean_value, 2),
        'std': round(std_value, 2),
        'min': min_value,
        'max': max_value,
        'width': int(width),
        'height': int(height),
        'bright_ratio': round(bright_ratio, 4),
        'score': round(float(score), 2),
    }


def _camera_backend_candidates(cv2_module):
    """Prefer Windows camera APIs but fall back to OpenCV automatic selection."""
    candidates = []
    if os.name == 'nt':
        if hasattr(cv2_module, 'CAP_DSHOW'):
            candidates.append(('DSHOW', cv2_module.CAP_DSHOW))
        if hasattr(cv2_module, 'CAP_MSMF'):
            candidates.append(('MSMF', cv2_module.CAP_MSMF))

    candidates.append(('AUTO', getattr(cv2_module, 'CAP_ANY', 0)))

    unique = []
    seen_flags = set()
    for name, flag in candidates:
        if flag in seen_flags:
            continue
        seen_flags.add(flag)
        unique.append((name, flag))
    return unique


def _capture_best_frame(cv2_module, camera_id, delay, warmup_frames, resolution_candidates=None):
    """Try camera backends and return the best non-black frame."""
    diagnostics = []
    best_frame = None
    best_stats = None
    best_backend = None
    best_resolution = None
    opened_any = False

    if resolution_candidates is None:
        resolution_candidates = [
            (3840, 2160),
            (2560, 1440),
            (1920, 1080),
            (1280, 720),
            None,
        ]

    for backend_name, backend_flag in _camera_backend_candidates(cv2_module):
        for requested_resolution in resolution_candidates:
            cap = None
            try:
                cap = cv2_module.VideoCapture(camera_id, backend_flag)
                if not cap.isOpened():
                    diagnostics.append({
                        'backend': backend_name,
                        'requested_resolution': requested_resolution,
                        'opened': False,
                        'reason': '无法打开设备'
                    })
                    continue

                opened_any = True

                if requested_resolution:
                    requested_width, requested_height = requested_resolution
                    try:
                        cap.set(cv2_module.CAP_PROP_FOURCC, cv2_module.VideoWriter_fourcc(*'MJPG'))
                    except Exception:
                        pass
                    cap.set(cv2_module.CAP_PROP_FRAME_WIDTH, requested_width)
                    cap.set(cv2_module.CAP_PROP_FRAME_HEIGHT, requested_height)
                    cap.set(cv2_module.CAP_PROP_FPS, 30)

                if delay:
                    time.sleep(delay)

                backend_best_frame = None
                backend_best_stats = None
                read_ok = 0
                frame_count = max(12, warmup_frames)

                for _ in range(frame_count):
                    ret, current_frame = cap.read()
                    if ret and current_frame is not None:
                        read_ok += 1
                        stats = _frame_quality(cv2_module, current_frame)
                        if backend_best_stats is None or stats['score'] > backend_best_stats['score']:
                            backend_best_stats = stats
                            backend_best_frame = current_frame
                        if stats['usable'] and read_ok >= 5:
                            # Give the device a few frames to settle, then accept a useful frame.
                            break
                    time.sleep(0.04)

                diagnostics.append({
                    'backend': backend_name,
                    'requested_resolution': requested_resolution,
                    'opened': True,
                    'read_ok': read_ok,
                    'best_stats': backend_best_stats,
                })

                should_replace = False
                backend_area = 0
                if backend_best_stats:
                    backend_area = backend_best_stats.get('width', 0) * backend_best_stats.get('height', 0)
                    best_area = (best_stats or {}).get('width', 0) * (best_stats or {}).get('height', 0)
                    should_replace = (
                        best_stats is None or
                        (
                            backend_best_stats['usable'] and not best_stats.get('usable')
                        ) or
                        (
                            backend_best_stats['usable'] == best_stats.get('usable') and
                            backend_area > best_area
                        ) or
                        (
                            backend_best_stats['usable'] == best_stats.get('usable') and
                            backend_area == best_area and
                            backend_best_stats['score'] > best_stats['score']
                        )
                    )

                if should_replace:
                    best_stats = backend_best_stats
                    best_frame = backend_best_frame
                    best_backend = backend_name
                    best_resolution = requested_resolution

                if backend_best_stats and backend_best_stats['usable'] and backend_area >= 1920 * 1080:
                    break
            finally:
                if cap is not None:
                    cap.release()

        if best_stats and best_stats.get('usable') and (
            best_stats.get('width', 0) * best_stats.get('height', 0) >= 1920 * 1080
        ):
            break

    return best_frame, best_stats, best_backend, best_resolution, opened_any, diagnostics


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_ct(request):
    """
    MRI脑瘤图像分割接口
    支持 T1, T2, T1CE, FLAIR 四种扫描模式
    """
    try:
        # 检查文件
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '未找到图像文件'
            }, status=400)
        
        image_file = request.FILES['image']
        scan_mode = request.POST.get('scan_mode', '').lower()
        
        # 验证文件和扫描模式
        if not image_file:
            return JsonResponse({
                'success': False,
                'error': '未选择文件'
            }, status=400)
        
        if scan_mode not in SCAN_MODES:
            return JsonResponse({
                'success': False,
                'error': f'无效的扫描模式，请选择: {", ".join(SCAN_MODES.keys())}'
            }, status=400)
        
        # 保存上传的文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(image_file.name)
        safe_filename = f"{scan_mode}_{timestamp}_{filename}"
        
        # 保存到 MEDIA_ROOT/uploads
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        upload_path = os.path.join(upload_dir, safe_filename)
        
        with open(upload_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        print(f"\n{'='*50}")
        print(f"收到新的分割请求")
        print(f"扫描模式: {SCAN_MODES[scan_mode]}")
        print(f"文件保存至: {upload_path}")
        print(f"{'='*50}\n")
        
        result, validation = _build_segmentation_result(upload_path, scan_mode)
        if result is None:
            return JsonResponse({
                'success': False,
                'error': validation.get('message') or '当前图片不像 CT/MRI 医学影像，已停止 AI 分析',
                'medical_validation': validation
            })
        
        print(f"\n分析完成:")
        print(f"- 肿瘤检测: {'是' if result['tumor_detected'] else '否'}")
        print(f"- 置信度: {result['confidence_score']:.2%}")
        print(f"- 肿瘤面积: {result['tumor_area']} 像素\n")
        
        return JsonResponse({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        print(f"分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def capture_camera(request):
    """
    USB相机拍照并执行MRI脑瘤图像分割。

    浏览器/H5页面无法直接控制本机USB硬件，因此由运行在同一台电脑上的
    Django后端打开摄像头、保存照片，再复用现有AI分析流程。
    """
    try:
        try:
            import cv2
        except ImportError:
            return JsonResponse({
                'success': False,
                'error': '后端未安装 OpenCV，无法调用USB相机。请安装 opencv-python。'
            }, status=500)

        data = request.data if hasattr(request, 'data') else {}
        camera_id = int(data.get('camera_id', 1))
        delay = float(data.get('delay', 1.2))
        warmup_frames = int(data.get('warmup_frames', 45))
        scan_mode = str(data.get('scan_mode', 't1ce')).strip().lower()

        if scan_mode not in SCAN_MODES:
            return JsonResponse({
                'success': False,
                'error': f'无效的扫描模式，请选择: {", ".join(SCAN_MODES.keys())}'
            }, status=400)

        delay = max(0.0, min(delay, 5.0))
        warmup_frames = max(12, min(warmup_frames, 90))

        frame, frame_stats, backend_name, requested_resolution, opened_any, diagnostics = _capture_best_frame(
            cv2,
            camera_id=camera_id,
            delay=delay,
            warmup_frames=warmup_frames
        )

        if not opened_any:
            return JsonResponse({
                'success': False,
                'error': f'无法打开USB相机（camera_id={camera_id}）。请确认设备已连接，或尝试修改相机ID。',
                'diagnostics': diagnostics
            }, status=400)

        if frame is None:
            return JsonResponse({
                'success': False,
                'error': '相机已打开，但未读取到画面。请检查设备画面或驱动。',
                'diagnostics': diagnostics
            }, status=500)

        if not frame_stats or not frame_stats.get('usable'):
            return JsonResponse({
                'success': False,
                'error': '相机画面过暗或为黑屏，已停止上传和AI分析。请检查硬件画面、光源、采集设备输入，或切换相机ID后重试。',
                'capture_quality': frame_stats,
                'backend': backend_name,
                'diagnostics': diagnostics
            })

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{scan_mode}_camera_{timestamp}.jpg"
        capture_path = os.path.join(CAPTURE_FOLDER, filename)
        _save_frame_as_jpeg(cv2, frame, capture_path)

        print(f"\n{'='*50}")
        print("收到USB相机拍照分析请求")
        print(f"相机ID: {camera_id}")
        print(f"相机后端: {backend_name}")
        print(f"请求分辨率: {requested_resolution or '默认'}")
        print(f"画面质量: {frame_stats}")
        print(f"扫描模式: {SCAN_MODES[scan_mode]}")
        print(f"照片保存至: {capture_path}")
        print(f"{'='*50}\n")

        capture_payload = {
            'filename': filename,
            'image': f"{settings.MEDIA_URL}camera_captures/{filename}",
            'camera_id': camera_id,
            'scan_mode': scan_mode,
            'backend': backend_name,
            'requested_resolution': requested_resolution,
            'quality': frame_stats
        }

        result, validation = _build_segmentation_result(capture_path, scan_mode)
        if result is None:
            return JsonResponse({
                'success': False,
                'error': validation.get('message') or '当前图片不像 CT/MRI 医学影像，已停止 AI 分析',
                'capture': capture_payload,
                'medical_validation': validation
            })

        return JsonResponse({
            'success': True,
            'capture': capture_payload,
            'result': result
        })

    except Exception as e:
        print(f"相机拍照分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    AI聊天接口 - 使用DeepSeek API（非流式）
    支持医疗咨询、报告解读、健康建议等
    """
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        
        messages = data.get('messages', [])
        patient_info = data.get('patient_info', {})
        scan_result = data.get('scan_result', None)
        
        # 调用 DeepSeek（一次性返回）
        result = chat_with_deepseek(messages, patient_info, scan_result)
        
        return JsonResponse(result)
        
    except Exception as e:
        print(f"❌ 聊天错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'response': '抱歉，AI服务出现异常。请稍后重试。',
            'error': 'INTERNAL_ERROR'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def chat_stream(request):
    """
    AI聊天接口（流式SSE）
    逐段返回生成内容：每段为一行以 data: 开头的JSON：{"content": "..."}
    最后发送 data: [DONE]
    """
    try:
        data = json.loads(request.body) if request.body else {}
        messages = data.get('messages', [])
        patient_info = data.get('patient_info', {})
        scan_result = data.get('scan_result', None)

        def sse_generator():
            try:
                for chunk in chat_with_deepseek_stream(messages, patient_info, scan_result):
                    if chunk:
                        yield f"data: {{\"content\": {json.dumps(chunk, ensure_ascii=False)} }}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                err = f"[SSE错误] {str(e)}"
                yield f"data: {{\"error\": {json.dumps(err, ensure_ascii=False)} }}\n\n"
                yield "data: [DONE]\n\n"

        response = StreamingHttpResponse(sse_generator(), content_type='text/event-stream')
        # 建议关闭各层缓冲
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    except Exception as e:
        print(f"❌ 流式聊天错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'response': '抱歉，AI服务出现异常。请稍后重试。',
            'error': 'INTERNAL_ERROR'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """健康检查接口"""
    from decouple import config
    
    return JsonResponse({
        'status': 'healthy',
        'service': 'Django ML Service',
        'device': str(get_device()),
        'deepseek_configured': bool(config('DEEPSEEK_API_KEY', default='')),
        'supported_scan_modes': list(SCAN_MODES.keys())
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_info(request):
    """获取模型信息"""
    from decouple import config
    
    model_path = config('MODEL_PATH', default='./models/brain_tumor_segmentation_model.pth')
    
    return JsonResponse({
        'model_type': 'Brain Tumor Segmentation Model',
        'device': str(get_device()),
        'model_path': model_path,
        'supported_modes': SCAN_MODES,
        'ai_provider': '硅基流动 (SiliconFlow)',
        'ai_model': 'deepseek-ai/DeepSeek-V3'
    })

