"""
模型加载器
在 Django 启动时自动加载所有 ML 模型
"""
import os
import torch
from pathlib import Path
from decouple import config

# 全局变量：存储加载的模型（4个不同扫描模式的模型）
segmentation_models = {
    't1': None,
    't2': None,
    't1ce': None,
    'flair': None
}
DEVICE = None

# 配置
# 模型文件夹路径，从 .env 读取或使用相对路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = config('MODEL_DIR', default='../../image_predict/models')

def load_all_models():
    """
    加载所有 TransUNet 模型（4个扫描模式）
    
    支持两种模式：
    1. 如果找到模型文件 - 加载真实模型
    2. 如果没有模型文件 - 使用示例模式（不加载模型）
    """
    global segmentation_models, DEVICE
    
    try:
        # 设置设备
        DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"\n{'='*70}")
        print("  TransUNet 模型加载 - 脑瘤MRI分割")
        print(f"{'='*70}")
        print(f"设备: {DEVICE}")
        print(f"CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU设备: {torch.cuda.get_device_name(0)}")
        
        # 构建模型目录路径（强制相对路径，避免绝对盘符依赖）
        raw_model_dir = MODEL_DIR
        if os.path.isabs(raw_model_dir):
            try:
                # 转为相对 backend 根目录（manage.py 所在目录）
                model_dir = os.path.relpath(raw_model_dir, start=str(BASE_DIR))
            except Exception:
                # 跨盘符等无法转换时，回退到默认相对目录
                model_dir = '../../image_predict/models'
        else:
            model_dir = raw_model_dir
        model_dir = os.path.normpath(model_dir)
        print(f"模型目录: {model_dir}")
        
        # 模型文件名配置
        model_files = {
            't1': 'TransUNet_t1.pth',
            't2': 'TransUNet_t2.pth',
            't1ce': 'TransUNet_t1ce.pth',
            'flair': 'TransUNet_flair.pth'
        }
        
        loaded_count = 0
        print(f"\n正在加载模型...")
        
        # 加载每个扫描模式的模型
        for scan_mode, model_file in model_files.items():
            model_path = os.path.join(model_dir, model_file)
            
            if os.path.exists(model_path):
                try:
                    print(f"\n  [{scan_mode.upper()}] 加载中... ", end='')
                    model = load_transunet_model(model_path, DEVICE)
                    
                    if model is not None:
                        segmentation_models[scan_mode] = model
                        print("[OK] 成功")
                        loaded_count += 1
                    else:
                        print("[WARN] 失败")
                        
                except Exception as e:
                    print(f"[ERR] 错误: {str(e)}")
                    segmentation_models[scan_mode] = None
            else:
                print(f"\n  [{scan_mode.upper()}] 未找到: {model_file}")
                segmentation_models[scan_mode] = None
        
        # 总结
        print(f"\n{'='*70}")
        if loaded_count > 0:
            print(f"[OK] 成功加载 {loaded_count}/4 个模型")
            print(f"已加载模式: {[mode.upper() for mode, model in segmentation_models.items() if model is not None]}")
        else:
            print("[WARN] 未加载任何模型，将使用示例模式（生成模拟结果）")
            print(f"\n如需使用真实模型，请：")
            print(f"  1. 将模型文件放到: {model_dir}")
            print(f"  2. 确保文件名为: TransUNet_t1.pth, TransUNet_t2.pth, TransUNet_t1ce.pth, TransUNet_flair.pth")
            print(f"  3. 或在 .env 中配置 MODEL_DIR")
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n[ERR] 模型加载失败: {str(e)}")
        import traceback
        traceback.print_exc()
        # 重置所有模型为None
        for key in segmentation_models:
            segmentation_models[key] = None
        print("\n将使用示例模式")
        print(f"{'='*70}\n")


def load_transunet_model(model_path, device):
    """
    加载TransUNet分割模型
    
    Args:
        model_path: 模型文件路径
        device: 运行设备
    
    Returns:
        加载的模型或None
    """
    try:
        # 导入TransUNet架构
        from .transunet_model import create_transunet
        
        # 创建TransUNet模型实例（使用真实训练配置）
        # 参数：1通道输入（灰度MRI）, 4通道输出（背景+3种肿瘤类型）, 256x256输入
        model = create_transunet(in_channels=1, num_classes=4, img_size=256)
        
        # 加载权重
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        
        # 处理不同的checkpoint格式
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            elif 'state_dict' in checkpoint:
                model.load_state_dict(checkpoint['state_dict'])
            elif 'model' in checkpoint:
                model.load_state_dict(checkpoint['model'])
            else:
                # 尝试直接加载
                model.load_state_dict(checkpoint)
        else:
            # checkpoint直接是state_dict
            model.load_state_dict(checkpoint)
        
        # 移到指定设备
        model = model.to(device)
        
        # 设置为评估模式
        model.eval()
        
        return model
        
    except Exception as e:
        print(f"详细错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def count_parameters(model):
    """计算模型参数数量"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def get_segmentation_model(scan_mode='t1'):
    """
    获取指定扫描模式的分割模型
    
    Args:
        scan_mode: 扫描模式 ('t1', 't2', 't1ce', 'flair')
    
    Returns:
        对应模式的模型或None
    """
    return segmentation_models.get(scan_mode.lower())

def get_device():
    """获取设备"""
    return DEVICE

def get_all_loaded_models():
    """获取所有已加载的模型"""
    return {mode: model for mode, model in segmentation_models.items() if model is not None}

