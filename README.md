<p align="center">
  <img src="code/frontend/static/logo.png" width="120" alt="BraiLink Logo" />
</p>

<h1 align="center">BraiLink</h1>
<p align="center">AI-Powered Brain Tumor Diagnosis Assistant</p>

<p align="center">
  <a href="README.zh-CN.md">🇨🇳 中文</a>
  &nbsp;|&nbsp;
  <img src="https://img.shields.io/badge/backend-Django%20REST-0A5CFF?style=flat-square&logo=django" />
  <img src="https://img.shields.io/badge/frontend-UniApp-00C2D7?style=flat-square&logo=vue.js" />
  <img src="https://img.shields.io/badge/AI-DeepSeek%20%2B%20TransUNet-1FB877?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
</p>

---

## 📖 Introduction

**BraiLink** is an AI-powered medical assistant application designed for brain tumor diagnosis. It leverages deep learning (TransUNet) for automated MRI-based brain tumor segmentation and integrates a large language model (DeepSeek) for intelligent medical consultation. The system supports three user roles — **Doctors**, **Patients**, and **Family Members** — providing a comprehensive bridge for brain tumor diagnosis and communication.

---

## 🏗️ Architecture

```
BraiLink/
├── code/
│   ├── backend/                 # Django REST Framework
│   │   ├── accounts/            # User authentication (Doctor/Patient/Family)
│   │   ├── patients/            # Patient management
│   │   ├── doctors/             # Doctor management
│   │   ├── families/            # Family management
│   │   ├── appointments/        # Appointment scheduling
│   │   ├── medical_records/     # Electronic health records
│   │   ├── ai_chat/             # AI medical consultation
│   │   ├── ml_service/          # ML inference (TransUNet + DeepSeek)
│   │   ├── notifications/       # System notifications
│   │   └── brain_tumor_api/     # Django project config
│   ├── frontend/                # UniApp cross-platform frontend
│   │   ├── pages/               # 20+ pages
│   │   ├── components/          # Reusable components
│   │   ├── config/              # Environment config
│   │   └── utils/               # Utility functions
│   └── image_predict/           # ML models & inference scripts
└── data/                        # Training data (MRI: T1/T1ce/T2/FLAIR/Seg)
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Tumor Segmentation** | TransUNet-based automated brain tumor segmentation from multi-sequence MRI |
| 💬 **AI Medical Chat** | DeepSeek-powered medical consultation with patient history context |
| 📋 **EHR Management** | Complete electronic health records for patients |
| 📅 **Appointments** | Online appointment scheduling between patients and doctors |
| 👨‍👩‍👧 **Family Binding** | Family members can bind to patients for assisted management |
| 🔔 **Notifications** | Real-time system notifications for appointments and reports |
| 📰 **Medical News** | Curated medical news feed with category filtering |
| 🌐 **Cross-Platform** | UniApp-based: Android, iOS, H5, WeChat Mini Program |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **HBuilderX** (for UniApp mobile build)
- **Redis** (optional, for Celery async tasks)

### Backend

```bash
cd code/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DEEPSEEK_API_KEY and other configs

# Run migrations
python manage.py migrate

# (Optional) Load demo data
python init_demo_data.py

# Start server
python manage.py runserver 0.0.0.0:8000
```

### Frontend

```bash
cd code/frontend

# Install dependencies
npm install

# Configure API endpoint in config/env.config.js

# Run in browser (H5)
npm run dev:h5

# Or open in HBuilderX for Android / iOS / WeChat Mini Program build
```

### ML Model

Download the pre-trained TransUNet model weights and place them in `code/image_predict/models/`.

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | **Required in production** |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_ENGINE` | Database engine | `sqlite3` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | **Required for AI chat** |
| `FLASK_ML_SERVICE_URL` | ML service endpoint | `http://localhost:5000` |
| `CELERY_BROKER_URL` | Celery broker | `redis://localhost:6379/0` |

---

## 👥 User Roles

| Role | Capabilities |
|------|-------------|
| 🩺 **Doctor** | Patient management, image diagnosis, medical record review |
| 🏥 **Patient** | AI consultation, appointment booking, health records |
| 👨‍👩‍👧 **Family** | Assisted patient management, medical record viewing |

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Enndme-KK** — [GitHub](https://github.com/Enndme-KK)

---

<p align="center">
  <sub>Made with ❤️ for better brain tumor diagnosis</sub>
</p>
