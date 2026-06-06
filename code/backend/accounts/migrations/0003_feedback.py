from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_user_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=500, verbose_name='反馈内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='提交时间')),
                ('is_resolved', models.BooleanField(default=False, verbose_name='是否处理')),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='feedbacks', to=settings.AUTH_USER_MODEL, verbose_name='提交用户')),
            ],
            options={
                'verbose_name': '意见反馈',
                'verbose_name_plural': '意见反馈',
                'ordering': ['-created_at'],
            },
        ),
    ]
