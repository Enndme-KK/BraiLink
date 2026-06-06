"""
模型架构定义

在这里定义你的深度学习模型架构
根据你训练的模型类型修改
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class UNet(nn.Module):
    """
    U-Net 架构 - 用于医学图像分割
    
    经典的编码器-解码器结构，适合脑瘤分割任务
    参考论文：U-Net: Convolutional Networks for Biomedical Image Segmentation
    
    参数:
        in_channels: 输入通道数（灰度图=1, RGB=3）
        out_channels: 输出通道数（类别数，如背景+肿瘤类型）
        init_features: 初始特征数
    """
    
    def __init__(self, in_channels=1, out_channels=4, init_features=32):
        super(UNet, self).__init__()
        
        features = init_features
        
        # 编码器（下采样路径）
        self.encoder1 = self._block(in_channels, features, name="enc1")
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.encoder2 = self._block(features, features * 2, name="enc2")
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.encoder3 = self._block(features * 2, features * 4, name="enc3")
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.encoder4 = self._block(features * 4, features * 8, name="enc4")
        self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # 瓶颈层
        self.bottleneck = self._block(features * 8, features * 16, name="bottleneck")
        
        # 解码器（上采样路径）
        self.upconv4 = nn.ConvTranspose2d(features * 16, features * 8, kernel_size=2, stride=2)
        self.decoder4 = self._block((features * 8) * 2, features * 8, name="dec4")
        self.upconv3 = nn.ConvTranspose2d(features * 8, features * 4, kernel_size=2, stride=2)
        self.decoder3 = self._block((features * 4) * 2, features * 4, name="dec3")
        self.upconv2 = nn.ConvTranspose2d(features * 4, features * 2, kernel_size=2, stride=2)
        self.decoder2 = self._block((features * 2) * 2, features * 2, name="dec2")
        self.upconv1 = nn.ConvTranspose2d(features * 2, features, kernel_size=2, stride=2)
        self.decoder1 = self._block(features * 2, features, name="dec1")
        
        # 输出层
        self.conv = nn.Conv2d(features, out_channels, kernel_size=1)
    
    def forward(self, x):
        # 编码器
        enc1 = self.encoder1(x)
        enc2 = self.encoder2(self.pool1(enc1))
        enc3 = self.encoder3(self.pool2(enc2))
        enc4 = self.encoder4(self.pool3(enc3))
        
        # 瓶颈层
        bottleneck = self.bottleneck(self.pool4(enc4))
        
        # 解码器（带跳跃连接）
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat((dec4, enc4), dim=1)
        dec4 = self.decoder4(dec4)
        
        dec3 = self.upconv3(dec4)
        dec3 = torch.cat((dec3, enc3), dim=1)
        dec3 = self.decoder3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat((dec2, enc2), dim=1)
        dec2 = self.decoder2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat((dec1, enc1), dim=1)
        dec1 = self.decoder1(dec1)
        
        # 输出
        return self.conv(dec1)
    
    def _block(self, in_channels, features, name):
        """U-Net基本卷积块"""
        return nn.Sequential(
            nn.Conv2d(in_channels, features, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(features),
            nn.ReLU(inplace=True),
            nn.Conv2d(features, features, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(features),
            nn.ReLU(inplace=True),
        )


class SimpleSegmentationModel(nn.Module):
    """
    简化的分割模型 - 用于快速原型
    
    如果U-Net太大或训练困难，可以使用这个简化版本
    """
    
    def __init__(self, in_channels=1, out_channels=4):
        super(SimpleSegmentationModel, self).__init__()
        
        self.encoder = nn.Sequential(
            # 卷积块1
            nn.Conv2d(in_channels, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # 卷积块2
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # 卷积块3
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )
        
        self.decoder = nn.Sequential(
            # 上采样1
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
            nn.Conv2d(256, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            
            # 上采样2
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
            nn.Conv2d(128, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            
            # 输出层
            nn.Conv2d(64, out_channels, kernel_size=1),
        )
    
    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x


class ResUNet(nn.Module):
    """
    ResUNet - U-Net with Residual Blocks
    
    结合了U-Net和ResNet的优点，训练更稳定
    适合深层网络和复杂任务
    """
    
    def __init__(self, in_channels=1, out_channels=4):
        super(ResUNet, self).__init__()
        
        # 编码器
        self.encoder1 = self._res_block(in_channels, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.encoder2 = self._res_block(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.encoder3 = self._res_block(128, 256)
        self.pool3 = nn.MaxPool2d(2)
        
        # 瓶颈层
        self.bottleneck = self._res_block(256, 512)
        
        # 解码器
        self.upconv3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.decoder3 = self._res_block(512, 256)
        self.upconv2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.decoder2 = self._res_block(256, 128)
        self.upconv1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.decoder1 = self._res_block(128, 64)
        
        # 输出层
        self.out = nn.Conv2d(64, out_channels, kernel_size=1)
    
    def forward(self, x):
        # 编码
        enc1 = self.encoder1(x)
        enc2 = self.encoder2(self.pool1(enc1))
        enc3 = self.encoder3(self.pool2(enc2))
        
        # 瓶颈
        bottleneck = self.bottleneck(self.pool3(enc3))
        
        # 解码
        dec3 = self.upconv3(bottleneck)
        dec3 = torch.cat([dec3, enc3], dim=1)
        dec3 = self.decoder3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)
        dec2 = self.decoder2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)
        dec1 = self.decoder1(dec1)
        
        return self.out(dec1)
    
    def _res_block(self, in_channels, out_channels):
        """残差块"""
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )


# ============================================
# 使用说明
# ============================================
"""
选择合适的模型架构：

1. UNet - 推荐用于脑瘤分割
   - 经典架构，效果好
   - 参数量适中
   - 训练稳定

2. SimpleSegmentationModel - 快速原型
   - 参数少，训练快
   - 适合资源有限的情况
   - 准确率可能较低

3. ResUNet - 高精度需求
   - 训练更稳定
   - 可以做得更深
   - 需要更多计算资源

使用示例：

```python
# 创建模型实例
model = UNet(in_channels=1, out_channels=4)

# 加载预训练权重
checkpoint = torch.load('model.pth')
model.load_state_dict(checkpoint)

# 设置为评估模式
model.eval()

# 进行预测
with torch.no_grad():
    output = model(input_tensor)
```

输出说明：
- out_channels=4: [背景, 肿瘤类型1, 肿瘤类型2, 肿瘤类型3]
- out_channels=2: [背景, 肿瘤]
"""


def get_model(model_name='unet', **kwargs):
    """
    工厂函数 - 根据名称创建模型
    
    Args:
        model_name: 模型名称 ('unet', 'simple', 'resunet')
        **kwargs: 模型参数
    
    Returns:
        模型实例
    """
    models = {
        'unet': UNet,
        'simple': SimpleSegmentationModel,
        'resunet': ResUNet,
    }
    
    if model_name not in models:
        raise ValueError(f"未知模型: {model_name}. 可选: {list(models.keys())}")
    
    return models[model_name](**kwargs)


if __name__ == '__main__':
    # 测试模型
    print("测试模型架构...")
    
    # 创建模型
    model = UNet(in_channels=1, out_channels=4)
    
    # 创建测试输入
    test_input = torch.randn(1, 1, 256, 256)
    
    # 前向传播
    with torch.no_grad():
        output = model(test_input)
    
    print(f"输入形状: {test_input.shape}")
    print(f"输出形状: {output.shape}")
    print(f"模型参数数量: {sum(p.numel() for p in model.parameters()):,}")
    print("\n模型测试通过！")

