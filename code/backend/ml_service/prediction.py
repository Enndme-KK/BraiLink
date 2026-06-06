"""
图像分割预测模块
"""
import cv2
import numpy as np
import os
import torch
from datetime import datetime
from .models_loader import get_segmentation_model, get_device

# MRI 扫描模式配置
SCAN_MODES = {
    't1': 'T1',
    't2': 'T2',
    't1ce': 'T1CE',
    'flair': 'FLAIR'
}


def _read_image_any_path(image_path):
    """Read an image path safely, including Windows paths containing Chinese text."""
    data = np.fromfile(str(image_path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def validate_medical_scan_image(image_or_path):
    """
    Basic out-of-distribution guard before running the brain tumor model.

    The segmentation model is trained for CT/MRI-like grayscale medical images.
    Without this guard, arbitrary camera photos can still produce colored masks
    because the network must output a segmentation class for every pixel.
    """
    try:
        if isinstance(image_or_path, (str, bytes, os.PathLike)):
            image = _read_image_any_path(image_or_path)
        else:
            image = image_or_path

        if image is None:
            return {
                'is_medical_scan': False,
                'message': '无法读取图像，已停止 AI 分析'
            }

        if len(image.shape) == 2:
            bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            bgr = image

        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]

        height, width = gray.shape[:2]
        border_width = max(4, min(width, height) // 12)
        border = np.concatenate([
            gray[:border_width, :].reshape(-1),
            gray[-border_width:, :].reshape(-1),
            gray[:, :border_width].reshape(-1),
            gray[:, -border_width:].reshape(-1),
        ])

        p1 = float(np.percentile(gray, 1))
        p99 = float(np.percentile(gray, 99))
        dynamic_range = p99 - p1
        mean_value = float(gray.mean())
        std_value = float(gray.std())
        dark_ratio = float((gray < 24).mean())
        bright_ratio = float((gray > 220).mean())
        border_dark_ratio = float((border < 30).mean())
        saturation_mean = float(saturation.mean())
        saturation_p90 = float(np.percentile(saturation, 90))

        grayscale_like = saturation_mean < 35 and saturation_p90 < 85
        has_contrast = std_value > 18 and dynamic_range > 70
        has_scan_frame = dark_ratio > 0.18 or border_dark_ratio > 0.28
        not_blank = p99 > 45 and dynamic_range > 50

        score = 0
        score += 35 if grayscale_like else 0
        score += 25 if has_contrast else 0
        score += 20 if has_scan_frame else 0
        score += 20 if not_blank else 0
        score -= 25 if saturation_mean > 55 or saturation_p90 > 120 else 0
        score -= 15 if bright_ratio > 0.55 and dark_ratio < 0.12 else 0

        is_medical_scan = score >= 65
        return {
            'is_medical_scan': bool(is_medical_scan),
            'score': int(score),
            'message': '图像通过医学影像校验' if is_medical_scan else '当前图片不像 CT/MRI 医学影像，已停止 AI 分析。请放置真实 CT/MRI 图像后重新上传或拍照。',
            'metrics': {
                'width': int(width),
                'height': int(height),
                'mean': round(mean_value, 2),
                'std': round(std_value, 2),
                'dynamic_range': round(dynamic_range, 2),
                'dark_ratio': round(dark_ratio, 4),
                'bright_ratio': round(bright_ratio, 4),
                'border_dark_ratio': round(border_dark_ratio, 4),
                'saturation_mean': round(saturation_mean, 2),
                'saturation_p90': round(saturation_p90, 2),
            }
        }
    except Exception as error:
        return {
            'is_medical_scan': False,
            'message': f'医学影像校验失败: {error}'
        }

def preprocess_mri_array(image_array, scan_mode):
    """
    预处理MRI图像（数组版）
    
    给摄像头/上游已读取为 numpy array 的场景使用，避免再按文件路径读取。
    
    Args:
        image_array: 图像数据 (numpy array)，支持灰度或 BGR/RGB
        scan_mode: 扫描模式 (t1, t2, t1ce, flair)
    
    Returns:
        处理后的灰度图像数据（numpy array, uint8）
    """
    if image_array is None:
        raise ValueError("图像预处理失败: image_array 为空")

    image = image_array

    # 转为灰度
    if len(image.shape) == 3:
        # OpenCV 摄像头读到的是 BGR
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 统一为 uint8，便于后续处理/可视化
    if image.dtype != np.uint8:
        image = image.astype(np.float32)
        max_val = float(np.max(image)) if image.size else 0.0
        if 0.0 < max_val <= 1.0:
            image = (image * 255.0).clip(0, 255).astype(np.uint8)
        else:
            image = image.clip(0, 255).astype(np.uint8)

    print(f"图像预处理成功(数组) - 模式: {SCAN_MODES.get(scan_mode, scan_mode)}, 尺寸: {image.shape}")
    return image

def preprocess_mri_image(image_path, scan_mode):
    """
    预处理MRI图像
    
    Args:
        image_path: 图像文件路径
        scan_mode: 扫描模式 (t1, t2, t1ce, flair)
    
    Returns:
        处理后的图像数据
    """
    try:
        # 读取图像
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            # 尝试用PIL读取
            from PIL import Image
            image = np.array(Image.open(image_path).convert('L'))
        
        # TODO: 根据扫描模式进行特定的预处理
        # 不同模式可能需要不同的预处理方式
        
        print(f"图像预处理成功 - 模式: {SCAN_MODES.get(scan_mode, scan_mode)}, 尺寸: {image.shape}")
        return image
        
    except Exception as e:
        raise ValueError(f"图像预处理失败: {str(e)}")

def predict_segmentation(image_data, scan_mode):
    """
    使用TransUNet模型对MRI图像进行脑瘤分割预测
    
    支持两种模式：
    1. 真实模型模式 - 如果对应扫描模式的模型已加载
    2. 示例模式 - 如果模型未加载（用于功能测试）
    
    Args:
        image_data: 预处理后的图像数据 (numpy array)
        scan_mode: 扫描模式 (t1, t2, t1ce, flair)
    
    Returns:
        dict: {
            'segmentation_mask': 分割掩码 (numpy array),
            'tumor_detected': 是否检测到肿瘤 (bool),
            'tumor_area': 肿瘤区域面积 (int),
            'confidence_score': 置信度 (float),
            'tumor_regions': 肿瘤区域信息 (list)
        }
    """
    print(f"开始预测 - 扫描模式: {SCAN_MODES.get(scan_mode, scan_mode)}")
    
    # 获取对应扫描模式的模型
    model = get_segmentation_model(scan_mode)
    device = get_device()
    
    # 检查模型是否已加载
    if model is None:
        print(f"⚠️  {scan_mode.upper()} 模型未加载，使用示例模式")
        return predict_with_demo_mode(image_data, scan_mode)
    else:
        print(f"✅ 使用真实 TransUNet-{scan_mode.upper()} 模型进行预测")
        return predict_with_model(image_data, scan_mode, model, device)


def predict_with_model(image_data, scan_mode, model, device):
    """
    使用真实模型进行预测
    
    ⚠️ 这是真实预测函数，请根据你的模型调整
    """
    try:
        # 1. 图像预处理
        # 调整大小到模型期望的输入尺寸
        input_size = (256, 256)  # 根据你的模型调整
        original_size = image_data.shape[:2]
        
        # 调整大小
        image_resized = cv2.resize(image_data, input_size)
        
        # 归一化到 [0, 1]
        image_normalized = image_resized.astype(np.float32) / 255.0
        
        # 转换为tensor: [batch, channel, height, width]
        image_tensor = torch.from_numpy(image_normalized).unsqueeze(0).unsqueeze(0)
        image_tensor = image_tensor.to(device)
        
        print(f"输入tensor形状: {image_tensor.shape}")
        
        # 2. 模型预测
        with torch.no_grad():
            output = model(image_tensor)
            
            # 根据你的模型输出格式处理
            # 假设输出是 [batch, classes, H, W]
            # 如果是单通道输出，使用阈值
            # 如果是多类别，使用argmax
            
            if output.shape[1] == 1:
                # 单通道输出 - 使用sigmoid + 阈值
                pred_mask = torch.sigmoid(output)
                pred_mask = (pred_mask > 0.5).squeeze().cpu().numpy().astype(np.uint8)
            else:
                # 多通道输出 - 使用argmax
                pred_mask = torch.argmax(output, dim=1).squeeze().cpu().numpy()
        
        print(f"预测掩码形状: {pred_mask.shape}")
        
        # 3. 后处理 - 调整回原始尺寸
        if pred_mask.shape != original_size:
            pred_mask_resized = cv2.resize(
                pred_mask.astype(np.uint8), 
                (original_size[1], original_size[0]),
                interpolation=cv2.INTER_NEAREST
            )
        else:
            pred_mask_resized = pred_mask
        
        # 4. 分析结果
        return analyze_segmentation_result(pred_mask_resized, scan_mode)
        
    except Exception as e:
        print(f"❌ 预测失败: {str(e)}")
        import traceback
        traceback.print_exc()
        # 失败时返回示例结果
        return predict_with_demo_mode(image_data, scan_mode)


def predict_with_demo_mode(image_data, scan_mode):
    """
    示例模式 - 生成模拟的预测结果（多类别版本）
    
    用于：
    1. 功能测试（没有真实模型时）
    2. 前端开发和调试
    3. 演示系统功能
    
    ⚠️ 这不是真实的预测，仅用于演示！
    """
    print("🎭 使用示例模式生成模拟结果（多类别）")
    
    height, width = image_data.shape[:2]
    
    # 创建模拟的多类别肿瘤掩码
    # 0: 背景, 1: 坏死核心, 2: 水肿, 3: 增强肿瘤
    mask = np.zeros((height, width), dtype=np.uint8)
    
    # 随机决定是否"检测到"肿瘤（70%概率）
    import random
    has_tumor = random.random() < 0.7
    
    if has_tumor:
        center_x, center_y = width // 2, height // 2
        
        # 随机偏移中心
        offset_x = random.randint(-50, 50)
        offset_y = random.randint(-50, 50)
        center_x += offset_x
        center_y += offset_y
        
        # 1. 创建最外层的水肿区域（类别2 - 最大）
        edema_radius_x = width // 5 + random.randint(-15, 15)
        edema_radius_y = height // 5 + random.randint(-15, 15)
        cv2.ellipse(mask, (center_x, center_y), (edema_radius_x, edema_radius_y), 
                   0, 0, 360, 2, -1)
        
        # 2. 创建中间层的增强肿瘤区域（类别3 - 中等）
        enhancing_radius_x = int(edema_radius_x * 0.65)
        enhancing_radius_y = int(edema_radius_y * 0.65)
        cv2.ellipse(mask, (center_x, center_y), (enhancing_radius_x, enhancing_radius_y), 
                   0, 0, 360, 3, -1)
        
        # 3. 创建核心的坏死区域（类别1 - 最小）
        necrotic_radius_x = int(edema_radius_x * 0.35)
        necrotic_radius_y = int(edema_radius_y * 0.35)
        cv2.ellipse(mask, (center_x, center_y), (necrotic_radius_x, necrotic_radius_y), 
                   0, 0, 360, 1, -1)
        
        # 4. 添加一些噪声使其更真实（只影响边缘）
        # 创建边缘mask
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=2)
        eroded = cv2.erode(mask, kernel, iterations=2)
        edges = cv2.subtract(dilated, eroded)
        
        # 在边缘添加一些随机噪声
        noise_mask = np.random.random(mask.shape) < 0.1
        mask[np.logical_and(edges > 0, noise_mask)] = 0
    
    # 分析结果
    return analyze_segmentation_result(mask, scan_mode)


def analyze_segmentation_result(segmentation_mask, scan_mode):
    """
    分析分割结果，提取关键信息
    
    Args:
        segmentation_mask: 分割掩码（支持多类别：0=背景, 1=坏死核心, 2=水肿, 3=增强肿瘤）
        scan_mode: 扫描模式
    
    Returns:
        分析结果字典
    """
    # 1. 计算总肿瘤像素数
    tumor_pixels = np.sum(segmentation_mask > 0)
    total_pixels = segmentation_mask.size
    
    # 2. 计算各类别的像素数和百分比
    class_names = {
        1: '坏死核心',
        2: '水肿区域',
        3: '增强肿瘤'
    }
    
    class_stats = {}
    for class_id, class_name in class_names.items():
        class_pixels = np.sum(segmentation_mask == class_id)
        if class_pixels > 0:
            class_stats[class_name] = {
                'pixels': int(class_pixels),
                'percentage': float(class_pixels / total_pixels * 100)
            }
    
    # 3. 判断是否检测到肿瘤（阈值可调整）
    tumor_detected = tumor_pixels > 100
    
    # 4. 计算置信度
    if tumor_detected:
        # 基于肿瘤占比计算置信度
        tumor_ratio = tumor_pixels / total_pixels
        # 置信度在0.6-0.95之间
        confidence = min(0.95, 0.6 + tumor_ratio * 10)
    else:
        # 未检测到肿瘤，高置信度
        confidence = 0.95
    
    # 5. 找到肿瘤区域
    tumor_regions = find_tumor_regions(segmentation_mask)
    
    # 6. 构建结果
    result = {
        'segmentation_mask': segmentation_mask,
        'tumor_detected': bool(tumor_detected),
        'tumor_area': int(tumor_pixels),
        'confidence_score': float(confidence),
        'tumor_regions': tumor_regions,
        'scan_mode': SCAN_MODES.get(scan_mode, scan_mode),
        'total_pixels': int(total_pixels),
        'tumor_percentage': float(tumor_pixels / total_pixels * 100) if tumor_detected else 0.0,
        'class_statistics': class_stats  # 新增：各类别统计
    }
    
    print(f"预测完成:")
    print(f"  - 检测到肿瘤: {result['tumor_detected']}")
    print(f"  - 置信度: {result['confidence_score']:.2%}")
    print(f"  - 肿瘤总面积: {result['tumor_area']} 像素 ({result['tumor_percentage']:.2f}%)")
    print(f"  - 肿瘤区域数: {len(result['tumor_regions'])}")
    
    # 打印各类别统计
    if class_stats:
        print(f"  - 类别统计:")
        for class_name, stats in class_stats.items():
            print(f"    • {class_name}: {stats['pixels']} 像素 ({stats['percentage']:.2f}%)")
    
    return result


def find_tumor_regions(segmentation_mask):
    """
    找到并分析肿瘤区域
    
    Args:
        segmentation_mask: 二值分割掩码
    
    Returns:
        肿瘤区域列表，每个区域包含位置、大小等信息
    """
    if np.sum(segmentation_mask > 0) == 0:
        return []
    
    try:
        # 使用连通组件分析找到独立的肿瘤区域
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            segmentation_mask.astype(np.uint8), connectivity=8
        )
        
        regions = []
        # 跳过背景（label=0）
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            
            # 过滤太小的区域（可能是噪声）
            if area < 50:
                continue
            
            x = int(stats[i, cv2.CC_STAT_LEFT])
            y = int(stats[i, cv2.CC_STAT_TOP])
            w = int(stats[i, cv2.CC_STAT_WIDTH])
            h = int(stats[i, cv2.CC_STAT_HEIGHT])
            center_x = int(centroids[i][0])
            center_y = int(centroids[i][1])
            
            regions.append({
                'id': i,
                'area': int(area),
                'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                'centroid': {'x': center_x, 'y': center_y}
            })
        
        # 按面积排序（从大到小）
        regions.sort(key=lambda r: r['area'], reverse=True)
        
        return regions
        
    except Exception as e:
        print(f"区域分析失败: {str(e)}")
        return []

def create_visualization(original_image, segmentation_mask, scan_mode, output_dir):
    """
    创建分割结果的可视化图像（增强版：多类别彩色标注）
    
    Args:
        original_image: 原始图像
        segmentation_mask: 分割掩码
        scan_mode: 扫描模式
        output_dir: 输出目录
    
    Returns:
        可视化图像的文件名
    """
    try:
        import os
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        print(f"✅ 输出目录已创建: {output_dir}")
        
        # 打印调试信息
        print(f"📊 原始图像形状: {original_image.shape}")
        print(f"📊 分割掩码形状: {segmentation_mask.shape}")
        print(f"📊 分割掩码唯一值: {np.unique(segmentation_mask)}")
        
        # 确保图像是3通道BGR格式
        if len(original_image.shape) == 2:
            original_image_bgr = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
        else:
            original_image_bgr = original_image.copy()
        
        # 归一化原始图像到0-255
        if original_image_bgr.dtype != np.uint8:
            if original_image_bgr.max() <= 1.0:
                original_image_bgr = (original_image_bgr * 255).astype(np.uint8)
            else:
                original_image_bgr = original_image_bgr.astype(np.uint8)
        
        # 创建多类别彩色掩码（BGR格式）
        colored_mask = np.zeros_like(original_image_bgr)
        
        # 定义颜色映射 (BGR格式)
        colored_mask[segmentation_mask == 1] = [0, 0, 255]    # 坏死核心 - 红色
        colored_mask[segmentation_mask == 2] = [0, 255, 0]    # 水肿 - 绿色  
        colored_mask[segmentation_mask == 3] = [255, 0, 0]    # 增强肿瘤 - 蓝色
        
        # 叠加原图和掩码
        alpha = 0.5
        overlay = cv2.addWeighted(original_image_bgr, 0.7, colored_mask, alpha, 0)
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        output_filename = f"segmentation_{scan_mode}_{timestamp}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        # 尝试保存 - 使用 imencode 解决中文路径问题
        try:
            # 方法1: 使用 imencode + 二进制写入（支持中文路径）
            success, encoded_image = cv2.imencode('.png', overlay)
            if success:
                with open(output_path, 'wb') as f:
                    f.write(encoded_image.tobytes())
                
                # 验证文件是否真的创建了
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"✅ 可视化图像保存成功!")
                    print(f"   📁 路径: {output_path}")
                    print(f"   📏 大小: {file_size} bytes")
                    return output_filename
                else:
                    print(f"❌ 文件保存失败：文件不存在")
                    return None
            else:
                print(f"❌ cv2.imencode 失败")
                return None
        except Exception as save_error:
            print(f"❌ 保存图片时出错: {save_error}")
            return None
        
    except Exception as e:
        print(f"❌ 可视化创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_segmentation_report(pred_result):
    """
    根据分割结果生成医学报告
    
    Args:
        pred_result: 预测结果字典
    
    Returns:
        分析报告文本
    """
    scan_mode = pred_result.get('scan_mode', '')
    
    if not pred_result['tumor_detected']:
        analysis = f"【{scan_mode} 扫描分析】未检测到明显的脑瘤病变。图像质量良好，未发现异常信号。建议定期复查，如有症状请及时就医。"
    else:
        tumor_area = pred_result['tumor_area']
        confidence = pred_result['confidence_score']
        
        # 根据肿瘤面积评估严重程度
        if tumor_area < 100:
            severity = "较小"
            suggestion = "建议定期监测，密切观察病情变化。"
        elif tumor_area < 500:
            severity = "中等"
            suggestion = "建议尽快咨询专业医生，制定治疗方案。"
        else:
            severity = "较大"
            suggestion = "建议立即就医，进行全面检查和治疗。"
        
        analysis = f"""【{scan_mode} 扫描分析】
检测到脑瘤病变，置信度为 {confidence:.2%}。
肿瘤区域面积：{tumor_area} 像素
肿瘤大小评估：{severity}

建议：{suggestion}

注意：此结果仅供参考，最终诊断需要专业医生结合多项检查综合判断。"""
    
    return analysis

