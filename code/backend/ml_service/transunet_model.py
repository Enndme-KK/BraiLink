"""
TransUNet模型架构（真实训练版本）
用于脑瘤MRI图像分割
从 image_predict/predict.py 复制的真实模型架构
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange, repeat

class Rearrange(nn.Module):
    def __init__(self, pattern, **kwargs):
        super().__init__()
        self.pattern = pattern
        self.kwargs = kwargs
        
    def forward(self, x):
        return rearrange(x, self.pattern, **self.kwargs)

class Attention(nn.Module):
    def __init__(self, dim, heads=8, dim_head=64, dropout=0.):
        super().__init__()
        inner_dim = dim_head * heads
        project_out = not (heads == 1 and dim_head == dim)

        self.heads = heads
        self.scale = dim_head ** -0.5

        self.attend = nn.Softmax(dim=-1)
        self.dropout = nn.Dropout(dropout)

        self.to_qkv = nn.Linear(dim, inner_dim * 3, bias=False)

        self.to_out = nn.Sequential(
            nn.Linear(inner_dim, dim),
            nn.Dropout(dropout)
        ) if project_out else nn.Identity()

    def forward(self, x):
        qkv = self.to_qkv(x).chunk(3, dim=-1)
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h=self.heads), qkv)

        dots = torch.matmul(q, k.transpose(-1, -2)) * self.scale

        attn = self.attend(dots)
        attn = self.dropout(attn)

        out = torch.matmul(attn, v)
        out = rearrange(out, 'b h n d -> b n (h d)')
        return self.to_out(out)

class PreNorm(nn.Module):
    def __init__(self, dim, fn):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.fn = fn

    def forward(self, x, **kwargs):
        return self.fn(self.norm(x), **kwargs)

class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim, dropout=0.):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, dim),
            nn.Dropout(dropout)
        )

    def forward(self, x):
        return self.net(x)

class Transformer(nn.Module):
    def __init__(self, dim, depth, heads, dim_head, mlp_dim, dropout=0.):
        super().__init__()
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(nn.ModuleList([
                PreNorm(dim, Attention(dim, heads=heads, dim_head=dim_head, dropout=dropout)),
                PreNorm(dim, FeedForward(dim, mlp_dim, dropout=dropout))
            ]))
    
    def forward(self, x):
        for attn, ff in self.layers:
            x = attn(x) + x
            x = ff(x) + x
        return x

class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)

class UpConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.up = nn.Sequential(
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.up(x)

class AttentionBlock(nn.Module):
    def __init__(self, F_g, F_l):
        super(AttentionBlock, self).__init__()
        self.W_g = nn.Sequential(
            nn.Conv2d(F_g, F_l, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_l)
        )
        
        self.W_x = nn.Sequential(
            nn.Conv2d(F_l, F_l, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_l)
        )
        
        self.psi = nn.Sequential(
            nn.Conv2d(F_l, 1, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(1),
            nn.Sigmoid()
        )
        
        self.relu = nn.ReLU(inplace=True)
        
    def forward(self, g, x):
        g1 = self.W_g(g)
        x1 = self.W_x(x)

        if g1.shape[2:] != x1.shape[2:]:
            g1 = F.interpolate(g1, size=x1.shape[2:], mode='bilinear', align_corners=False)

        psi = self.relu(g1 + x1)
        psi = self.psi(psi)

        if psi.shape[2:] != x.shape[2:]:
            psi = F.interpolate(psi, size=x.shape[2:], mode='bilinear', align_corners=False)

        return x * psi

class TransUNet(nn.Module):
    def __init__(
        self,
        img_size=256,
        in_channels=1,
        num_classes=4,
        embed_dim=512,
        patch_size=2,
        transformer_layers=8,
        transformer_heads=8,
        transformer_dim_head=64,
        transformer_mlp_dim=1024,
        skip_channels=[512, 256, 128, 64],
        dropout_rate=0.2
    ):
        super().__init__()
        
        self.img_size = img_size
        self.patch_size = patch_size
        self.in_channels = in_channels
        
        # 编码器
        self.enc1 = ConvBlock(in_channels, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = ConvBlock(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.enc3 = ConvBlock(128, 256)
        self.pool3 = nn.MaxPool2d(2)
        self.enc4 = ConvBlock(256, 512)
        self.pool4 = nn.MaxPool2d(2)
        
        # Bottleneck
        self.bottleneck = nn.Sequential(
            ConvBlock(512, embed_dim),
            nn.Dropout2d(dropout_rate)
        )
        
        # 计算patch数量
        feature_size = img_size // 16
        num_patches = (feature_size // patch_size) ** 2
        
        # Transformer
        self.patch_embed = nn.Sequential(
            nn.Conv2d(embed_dim, embed_dim, kernel_size=patch_size, stride=patch_size),
            Rearrange('b c h w -> b (h w) c')
        )
        
        self.transformer = Transformer(
            dim=embed_dim,
            depth=transformer_layers,
            heads=transformer_heads,
            dim_head=transformer_dim_head,
            mlp_dim=transformer_mlp_dim,
            dropout=0.1
        )
        
        # Position embedding
        self.pos_embedding = nn.Parameter(torch.randn(1, num_patches + 1, embed_dim))
        self.cls_token = nn.Parameter(torch.randn(1, 1, embed_dim))
        
        # Transformer to feature map
        self.transformer_to_feature = nn.Sequential(
            Rearrange('b (h w) c -> b c h w', 
                     h=feature_size // patch_size, 
                     w=feature_size // patch_size),
            nn.Conv2d(embed_dim, embed_dim, 1)
        )
        
        # 解码器
        self.up4 = UpConv(embed_dim, skip_channels[0])
        self.attention4 = AttentionBlock(skip_channels[0], 512)
        self.dec4 = ConvBlock(skip_channels[0] + 512, skip_channels[0])
        
        self.up3 = UpConv(skip_channels[0], skip_channels[1])
        self.attention3 = AttentionBlock(skip_channels[1], 256)
        self.dec3 = ConvBlock(skip_channels[1] + 256, skip_channels[1])
        
        self.up2 = UpConv(skip_channels[1], skip_channels[2])
        self.attention2 = AttentionBlock(skip_channels[2], 128)
        self.dec2 = ConvBlock(skip_channels[2] + 128, skip_channels[2])
        
        self.up1 = UpConv(skip_channels[2], skip_channels[3])
        self.attention1 = AttentionBlock(skip_channels[3], 64)
        self.dec1 = ConvBlock(skip_channels[3] + 64, skip_channels[3])
        
        # 最终输出
        self.final_conv = nn.Sequential(
            nn.Conv2d(skip_channels[3], 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Dropout2d(dropout_rate),
            nn.Conv2d(32, num_classes, 1)
        )
        
    def forward(self, x):
        # 编码器
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        e4 = self.enc4(self.pool3(e3))
        
        # Bottleneck
        b = self.bottleneck(self.pool4(e4))
        
        # Transformer
        patches = self.patch_embed(b)
        
        # Add cls token and position embedding
        cls_tokens = repeat(self.cls_token, '1 n d -> b n d', b=patches.shape[0])
        patches = torch.cat((cls_tokens, patches), dim=1)
        patches += self.pos_embedding[:, :(patches.shape[1])]
        
        # Apply transformer
        transformer_out = self.transformer(patches)
        transformer_out = transformer_out[:, 1:]  # remove cls token
        transformer_features = self.transformer_to_feature(transformer_out)
        
        # 解码器
        d4 = self.up4(transformer_features)
        e4_resized = F.interpolate(e4, size=d4.shape[2:], mode='bilinear', align_corners=False)
        e4_att = self.attention4(d4, e4_resized)
        d4 = torch.cat([d4, e4_att], dim=1)
        d4 = self.dec4(d4)

        d3 = self.up3(d4)
        e3_resized = F.interpolate(e3, size=d3.shape[2:], mode='bilinear', align_corners=False)
        e3_att = self.attention3(d3, e3_resized)
        d3 = torch.cat([d3, e3_att], dim=1)
        d3 = self.dec3(d3)

        d2 = self.up2(d3)
        e2_resized = F.interpolate(e2, size=d2.shape[2:], mode='bilinear', align_corners=False)
        e2_att = self.attention2(d2, e2_resized)
        d2 = torch.cat([d2, e2_att], dim=1)
        d2 = self.dec2(d2)

        d1 = self.up1(d2)
        e1_resized = F.interpolate(e1, size=d1.shape[2:], mode='bilinear', align_corners=False)
        e1_att = self.attention1(d1, e1_resized)
        d1 = torch.cat([d1, e1_att], dim=1)
        d1 = self.dec1(d1)

        out = self.final_conv(d1)
        out = F.interpolate(out, size=(self.img_size, self.img_size), 
                           mode='bilinear', align_corners=False)
        return out

def create_transunet(in_channels=1, num_classes=4, img_size=256):
    """
    创建TransUNet模型（真实训练配置）
    
    Args:
        in_channels: 输入通道数（MRI灰度图为1）
        num_classes: 输出类别数（背景+3种肿瘤类型=4）
        img_size: 输入图像尺寸
    
    Returns:
        TransUNet模型实例
    """
    model_config = {
        'img_size': img_size,
        'in_channels': in_channels,
        'num_classes': num_classes,
        'embed_dim': 512,
        'patch_size': 2,
        'transformer_layers': 8,
        'transformer_heads': 8,
        'dropout_rate': 0.3
    }
    
    return TransUNet(**model_config)

