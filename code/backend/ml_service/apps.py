from django.apps import AppConfig


class MlServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_service'
    verbose_name = 'ML服务'
    
    def ready(self):
        """应用启动时加载模型"""
        from . import models_loader
        models_loader.load_all_models()

