# 启动文件
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'milk.settings.dev')

# 创建celery实例对象
celery_app = Celery('milk')
# 加载配置文件
celery_app.config_from_object('celery_tasks.config')
# 自动注册异步任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])
