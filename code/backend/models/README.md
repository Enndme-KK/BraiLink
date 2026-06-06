# 🧠 模型文件目录

## 📂 说明

这个目录用于存放机器学习模型文件。

## 📥 如何添加模型

### 方法1：放置已训练的模型

如果你已经有训练好的PyTorch模型：

```
backend/models/
└── brain_tumor_segmentation.pth  # 你的模型文件
```

### 方法2：训练新模型

如果需要训练新模型，请参考：
- `backend/ml_service/模型集成指南.md`
- `backend/ml_service/model_architectures.py`

## 📋 支持的模型格式

### PyTorch (.pth / .pt)
```python
# 保存模型（推荐方式）
torch.save(model.state_dict(), 'model.pth')

# 或保存完整模型
torch.save(model, 'model.pth')
```

### ONNX (.onnx)
```python
torch.onnx.export(model, dummy_input, 'model.onnx')
```

## 🔧 配置模型路径

在 `backend/.env` 中配置：

```env
# 相对路径
MODEL_PATH=backend/models/brain_tumor_segmentation.pth

# 或绝对路径
MODEL_PATH=/absolute/path/to/model.pth
```

## ⚙️ 模型要求

### 输入格式
- **图像尺寸**: 256x256（可调整）
- **通道数**: 1（灰度图）
- **数值范围**: [0, 1] 归一化
- **Tensor形状**: [batch, 1, 256, 256]

### 输出格式
- **分割掩码**: 与输入同尺寸
- **类别数**: 
  - 二分类: [背景, 肿瘤]
  - 多分类: [背景, 肿瘤类型1, 肿瘤类型2, ...]

### 支持的扫描模式
- T1
- T2
- T1CE
- FLAIR

## 📊 推荐的模型架构

### 1. U-Net（推荐）
- 经典的医学图像分割架构
- 参数量适中
- 效果稳定

### 2. ResU-Net
- 带残差连接的U-Net
- 训练更稳定
- 可以做得更深

### 3. Attention U-Net
- 加入注意力机制
- 更关注重要区域
- 精度更高

## 🎯 快速测试

### 使用示例模式（无需模型）

即使没有模型文件，系统也能运行：

```bash
cd backend
python test_ml_service.py
```

系统会自动使用示例模式生成模拟结果。

### 使用真实模型

1. 将模型文件放入此目录
2. 配置环境变量
3. 运行测试

```bash
cd backend
python test_ml_service.py
```

## 📚 获取预训练模型

### 选项1：从GitHub下载

搜索 "brain tumor segmentation pytorch" 或 "medical image segmentation"

推荐项目：
- [MONAI](https://github.com/Project-MONAI/MONAI)
- [nnU-Net](https://github.com/MIC-DKFZ/nnUNet)
- [Medical-Image-Segmentation](https://github.com/topics/medical-image-segmentation)

### 选项2：使用BraTS数据集训练

1. 下载BraTS数据集
2. 使用提供的架构训练模型
3. 保存训练好的权重

### 选项3：联系我们

如果需要帮助获取或训练模型，请联系项目维护者。

## 🔒 注意事项

### Git忽略

大型模型文件不应提交到Git：

```gitignore
# .gitignore
*.pth
*.pt
*.onnx
```

### 模型下载

如果模型文件较大，建议：
1. 使用Git LFS
2. 提供下载链接
3. 或使用云存储服务

## 📖 更多信息

详细的集成指南请查看：
- `backend/ml_service/模型集成指南.md`
- `backend/ml_service/model_architectures.py`

---

💡 **提示**: 即使没有模型文件，系统也可以正常运行，会自动使用示例模式进行功能演示。

