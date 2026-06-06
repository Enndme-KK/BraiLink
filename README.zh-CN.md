<p align="center">
  <img src="code/frontend/static/logo.png" width="120" alt="BraiLink Logo" />
</p>

<h1 align="center">BraiLink</h1>
<p align="center">AI 驱动的脑瘤智能辅助诊断系统</p>

<p align="center">
  <a href="README.md">🇬🇧 English</a>
  &nbsp;|&nbsp;
  <img src="https://img.shields.io/badge/backend-Django%20REST-0A5CFF?style=flat-square&logo=django" />
  <img src="https://img.shields.io/badge/frontend-UniApp-00C2D7?style=flat-square&logo=vue.js" />
  <img src="https://img.shields.io/badge/AI-DeepSeek%20%2B%20TransUNet-1FB877?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
</p>

---

## 📖 项目简介

**BraiLink** 是一款基于人工智能的脑瘤辅助诊断医疗助手。系统采用 TransUNet 深度学习模型实现 MRI 脑瘤自动分割，并集成 DeepSeek 大语言模型提供智能医疗咨询。系统支持 **医生**、**患者**、**家属** 三种角色，为脑瘤诊疗提供一站式数字化桥梁。

---

## 🏗️ 技术架构

```
BraiLink/
├── code/
│   ├── backend/                 # Django REST Framework 后端
│   │   ├── accounts/            # 用户认证（医生 / 患者 / 家属）
│   │   ├── patients/            # 患者管理
│   │   ├── doctors/             # 医生管理
│   │   ├── families/            # 家属管理
│   │   ├── appointments/        # 预约挂号
│   │   ├── medical_records/     # 电子病历
│   │   ├── ai_chat/             # AI 医疗咨询
│   │   ├── ml_service/          # ML 推理服务（TransUNet + DeepSeek）
│   │   ├── notifications/       # 系统通知
│   │   └── brain_tumor_api/     # Django 项目配置
│   ├── frontend/                # UniApp 跨平台前端
│   │   ├── pages/               # 20+ 业务页面
│   │   ├── components/          # 可复用组件
│   │   ├── config/              # 环境配置
│   │   └── utils/               # 工具函数
│   └── image_predict/           # ML 模型与推理脚本
└── data/                        # 训练数据（MRI 序列：T1 / T1ce / T2 / FLAIR / Seg）
```

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🧠 **AI 肿瘤分割** | 基于 TransUNet 的多序列 MRI 脑瘤自动分割 |
| 💬 **AI 智能问诊** | DeepSeek 驱动的医疗咨询，支持患者病历上下文 |
| 📋 **电子病历管理** | 完整的患者电子健康档案 |
| 📅 **在线预约** | 患者与医生之间的在线预约挂号 |
| 👨‍👩‍👧 **家属绑定** | 家属可绑定患者，协助管理 |
| 🔔 **消息通知** | 预约、报告等实时系统通知 |
| 📰 **医学资讯** | 精选医学新闻，支持分类筛选 |
| 🌐 **跨平台** | 基于 UniApp，支持 Android / iOS / H5 / 微信小程序 |

---

## 🚀 快速开始

### 环境要求

- **Python** 3.10+
- **Node.js** 18+
- **HBuilderX**（用于 UniApp 移动端打包）
- **Redis**（可选，用于 Celery 异步任务）

### 后端

```bash
cd code/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置 DEEPSEEK_API_KEY 等配置

# 数据库迁移
python manage.py migrate

# （可选）加载演示数据
python init_demo_data.py

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 前端

```bash
cd code/frontend

# 安装依赖
npm install

# 在 config/env.config.js 中配置后端地址

# 浏览器预览（H5）
npm run dev:h5

# 或在 HBuilderX 中打开，打包为 Android / iOS / 微信小程序
```

### ML 模型

下载预训练的 TransUNet 模型权重，放入 `code/image_predict/models/` 目录。

---

## ⚙️ 环境变量

复制 `.env.example` 为 `.env`，配置以下变量：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Django 密钥 | **生产环境必须修改** |
| `DEBUG` | 调试模式 | `True` |
| `DATABASE_ENGINE` | 数据库引擎 | `sqlite3` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | **AI 聊天功能必需** |
| `FLASK_ML_SERVICE_URL` | ML 服务地址 | `http://localhost:5000` |
| `CELERY_BROKER_URL` | Celery 消息队列 | `redis://localhost:6379/0` |

---

## 👥 用户角色

| 角色 | 功能 |
|------|------|
| 🩺 **医生** | 患者管理、影像诊断、病历查阅 |
| 🏥 **患者** | AI 咨询、预约挂号、健康档案 |
| 👨‍👩‍👧 **家属** | 协助管理患者、查看病历 |

---

## 📄 许可证

本项目基于 MIT License 开源。

---

## 👤 作者

**Enndme-KK** — [GitHub](https://github.com/Enndme-KK)

---

<p align="center">
  <sub>为更好的脑瘤诊断而构建 ❤️</sub>
</p>
