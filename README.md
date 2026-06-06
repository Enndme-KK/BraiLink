<p align="center">
  <img src="code/frontend/static/logo.png" width="120" alt="BraiLink Logo" />
</p>

<h1 align="center">BraiLink</h1>
<p align="center">AI-Powered Brain Tumor Diagnosis Assistant<br/>AI 驱动的脑瘤智能辅助诊断系统</p>

<p align="center">
  <img src="https://img.shields.io/badge/backend-Django%20REST-0A5CFF?style=flat-square&logo=django" />
  <img src="https://img.shields.io/badge/frontend-UniApp-00C2D7?style=flat-square&logo=vue.js" />
  <img src="https://img.shields.io/badge/AI-DeepSeek%20%2B%20TransUNet-1FB877?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
</p>

---

## 📖 Introduction | 项目简介

**BraiLink** is an AI-powered medical assistant application designed for brain tumor diagnosis. It leverages deep learning (TransUNet) for automated MRI-based brain tumor segmentation and integrates a large language model (DeepSeek) for intelligent medical consultation. The system supports three user roles — **Doctors**, **Patients**, and **Family Members** — providing a comprehensive bridge for brain tumor diagnosis and communication.

**BraiLink（慧联脑图）** 是一款基于人工智能的脑瘤辅助诊断医疗助手。系统采用 TransUNet 深度学习模型实现 MRI 脑瘤自动分割，并集成 DeepSeek 大语言模型提供智能医疗咨询。系统支持 **医生**、**患者**、**家属**三种角色，为脑瘤诊疗提供一站式数字化桥梁。

---

## 🏗️ Architecture | 技术架构

```
BraiLink/
├── code/
│   ├── backend/                 # Django REST Framework 后端
│   │   ├── accounts/            # 用户认证 (医生/患者/家属)
│   │   ├── patients/            # 患者管理
│   │   ├── doctors/             # 医生管理
│   │   ├── families/            # 家属管理
│   │   ├── appointments/        # 预约挂号
│   │   ├── medical_records/     # 电子病历
│   │   ├── ai_chat/             # AI 医疗咨询
│   │   ├── ml_service/          # ML 推理服务 (TransUNet + DeepSeek)
│   │   ├── notifications/       # 系统通知
│   │   └── brain_tumor_api/     # Django 项目配置
│   ├── frontend/                # UniApp 跨平台前端
│   │   ├── pages/               # 20+ 业务页面
│   │   ├── components/          # 可复用组件
│   │   ├── config/              # 环境配置
│   │   └── utils/               # 工具函数
│   └── image_predict/           # ML 模型与推理脚本
└── data/                        # 训练数据 (MRI 序列: T1/T1ce/T2/FLAIR/Seg)
```

---

## ✨ Features | 核心功能

| Feature | 功能 | Description |
|---------|------|-------------|
| 🧠 **AI Tumor Segmentation** | AI 肿瘤分割 | TransUNet-based automated brain tumor segmentation from multi-sequence MRI |
| 💬 **AI Medical Chat** | AI 智能问诊 | DeepSeek-powered medical consultation with patient history context |
| 📋 **EHR Management** | 电子病历管理 | Complete electronic health records for patients |
| 📅 **Appointments** | 在线预约 | Online appointment scheduling between patients and doctors |
| 👨‍👩‍👧 **Family Binding** | 家属绑定 | Family members can bind to patients for assisted management |
| 🔔 **Notifications** | 消息通知 | Real-time system notifications for appointments and reports |
| 📰 **Medical News** | 医学资讯 | Curated medical news feed with category filtering |
| 🌐 **Cross-Platform** | 跨平台 | UniApp-based: Android, iOS, H5, WeChat Mini Program |

---

## 🚀 Quick Start | 快速开始

### Prerequisites | 环境要求

- **Python** 3.10+
- **Node.js** 18+
- **HBuilderX** (for UniApp mobile build)
- **Redis** (optional, for Celery async tasks)

### Backend | 后端

```bash
# 1. Enter backend directory
cd code/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set your DEEPSEEK_API_KEY and other configs

# 5. Run database migrations
python manage.py migrate

# 6. (Optional) Load demo data
python init_demo_data.py

# 7. Start development server
python manage.py runserver 0.0.0.0:8000
```

### Frontend | 前端

```bash
# 1. Enter frontend directory
cd code/frontend

# 2. Install dependencies
npm install  # or yarn

# 3. Configure API endpoint
# Edit config/env.config.js to set your backend server address

# 4. Run in browser (H5)
npm run dev:h5

# 5. Or open in HBuilderX for Android/iOS/WeChat build
```

### ML Model Setup | 模型配置

Download the pre-trained TransUNet model weights and place them in `code/image_predict/models/`.

---

## ⚙️ Environment Variables | 环境变量

Copy `.env.example` to `.env` and configure the following:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | **Required in production** |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_ENGINE` | Database engine | `sqlite3` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | **Required for AI chat** |
| `FLASK_ML_SERVICE_URL` | ML service endpoint | `http://localhost:5000` |
| `CELERY_BROKER_URL` | Celery broker | `redis://localhost:6379/0` |

---

## 👥 User Roles | 用户角色

| Role | 角色 | Capabilities |
|------|------|-------------|
| 🩺 **Doctor** | 医生 | Patient management, image diagnosis, medical record review |
| 🏥 **Patient** | 患者 | AI consultation, appointment booking, health records |
| 👨‍👩‍👧 **Family** | 家属 | Assisted patient management, medical record viewing |

---

## 📸 Screenshots | 界面预览

<p align="center">
  <em>Login · 登录</em> &nbsp;|&nbsp;
  <em>Identity Selection · 身份选择</em> &nbsp;|&nbsp;
  <em>AI Chat · AI 咨询</em> &nbsp;|&nbsp;
  <em>CT Scanner · 影像扫描</em>
</p>

---

## 📄 License | 许可证

This project is licensed under the MIT License.

---

## 👤 Author | 作者

**Enndme-KK** — [GitHub](https://github.com/Enndme-KK)

---

<p align="center">
  <sub>Made with ❤️ for better brain tumor diagnosis</sub>
</p>
