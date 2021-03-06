"""
Django settings for milk project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import platform
from sys import path
import datetime


# os.path 拼接路径
# sys.path 查看导包路径

def here(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)


PROJECT_ROOT = here("..")


def root(*x):
    return os.path.join(os.path.abspath(PROJECT_ROOT), *x)


# 追加系统导包路径（目的：1.注册子应用时代码可以更简洁 2.修改django认证模型类时，必须以 应用名.模型名）
path.append(root('apps'))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ijtxrj&t#pq(yv@6ju2g&aqr-x1a1*x-ebno6mm7ble!hi=mkk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

IS_DEV = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# CORS 追加⽩名单
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://localhost:8080',
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

# Set up logging for development use (logging to stdout)
level = 'DEBUG' if DEBUG else 'INFO'
hostname = platform.node().split(".")[0]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'ckeditor',  # 富文本编辑器
    'ckeditor_uploader',  # 富文本编辑器上传图片模块
    'django_crontab',
    'haystack',  # 全文搜索

    'xadmin',
    'crispy_forms',
    'reversion',

    'users',
    'oauth',
    'areas',
    'goods',
    'contents',
    'orders'
]

MIGRATE_APPS = []

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'milk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 指定模板文件加载路径
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'milk.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

# settings for cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 200,
            },
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
    },
    'session': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 200,
            },
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
    },
    'verify_codes': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 200,
            },
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
    },
    'history': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 200,
            },
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
    },
}

DJANGO_REDIS_IGNORE_EXCEPTIONS = True
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
DJANGO_REDIS_CONNECTION_FACTORY = "connectionfactory.DecodeConnectionFactory"

# 配置session存储3种方式
# 存储在数据库中，如下设置可写可不写，是默认存储模式
# SESSION_ENGINE = "django.contrib.sessions.backends.db"
# 存储在缓存中，存储在本机内存中，如果丢失则不能找回，比数据库的方式读写更快
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 混合存储：优先从本机内存中存取，如果没有则冲数据库中存取
# SESSION_ENGINE = "django.contrib.sessions.backends.cache_db"

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

syslog_address = 'log/'
if not os.path.exists(syslog_address):
    os.mkdir(syslog_address)

syslog_format = '%(asctime)s [service_variant=hysteria][%(name)s] %(levelname)s [{hostname}  %(process)d] ' \
                '[%(pathname)s:%(lineno)d] - %(message)s'.format(hostname=hostname)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(process)d [%(name)s] %(pathname)s:%(lineno)d - %(message)s',
        },
        'syslog_format': {
            'format': syslog_format
        },
    },
    'handlers': {
        'console': {
            'level': level,
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'default': {
            'level': level,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': syslog_address + 'milk.log',
            'formatter': 'syslog_format',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'default'],
            'propagate': True,
            'level': 'INFO'
        },
        'requests': {
            'handlers': ['console', 'default'],
            'propagate': True,
            'level': 'WARNING'
        },
        'urllib3': {
            'handlers': ['console', 'default'],
            'propagate': True,
            'level': 'WARNING'
        },
        'django.request': {
            'handlers': ['console', 'default'],
            'propagate': True,
            'level': 'ERROR'
        },
        'django_template': {
            'handlers': ['console', 'default'],
            'propagate': False,
            'level': 'WARNING'
        },
        'django.db.backends': {
            'handlers': ['console', 'default'],
            'propagate': False,
            'level': 'DEBUG',
        },
        '': {
            'handlers': ['console', 'default'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

# DRF配置项
REST_FRAMEWORK = {
    # 异常处理
    'EXCEPTION_HANDLER': 'milk.utils.exceptions.exception_handler',
    # 认证
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',  # JWT认证类，放在第一位是默认项
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    # 分页
    'DEFAULT_PAGINATION_CLASS': 'milk.utils.pagination.StandardResultsSetPagination',
}

# DRF扩展
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'default',
}

# JWT的有效期
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 为JWT登录视图补充返回值
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler',
}

# 修改默认的认证后端
AUTHENTICATION_BACKENDS = [
    'users.utils.UsernameMobileAuthBackend',
]

# Seperate Migrations
MIGRATION_MODULES = {app: '%s.dev_migrations' % app for app in MIGRATE_APPS}

# 修改Django认证系统的用户模型类
AUTH_USER_MODEL = 'users.User'

# QQ登录参数
QQ_CLIENT_ID = '101514053'
QQ_CLIENT_SECRET = '1075e75648566262ea35afa688073012'
QQ_REDIRECT_URI = 'http://www.milk.site:8080/oauth_callback.html'

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = ''
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = ''
# 收件⼈看到的发件⼈
EMAIL_FROM = ''

# django文件存储
DEFAULT_FILE_STORAGE = 'milk.utils.fastdfs.fdfs_storage.FastDFSStorage'
# FastDFS
FDFS_BASE_URL = 'http://192.168.103.210:8888/'
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')

# 富文本编辑器ckeditor配置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能
        'height': 300,  # 编辑器高度
        # 'width': 300, # 编辑器宽
    },
}
CKEDITOR_UPLOAD_PATH = ''  # 上传图片保存路径，使用了FastDFS，所以此处设为''

# 静态化主页存储路径
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc')

# 定时任务
CRONJOBS = [
    # 每1分钟执行⼀次生成主页静态⽂件
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>>/data/milk/crontab.log')
]

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': '',  # 此处为elasticsearch运行的服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'milk',  # 指定elasticsearch建立的索引库的名称
    },
}
# 当添加、修改、删除数据时，⾃动⽣成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 配置静态文件收集之后存放的⽬录
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc/static')