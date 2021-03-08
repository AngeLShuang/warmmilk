# flake8: noqa
import MySQLdb  # noqa: F401

from milk.settings.base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ['*']

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'milk',
#         'USER': 'root',
#         'PASSWORD': '123456',
#         'HOST': '',
#         'PORT': '3306',
#         'OPTIONS': {
#             'init_command': 'SET default_storage_engine=InnoDB',
#             'sql_mode': 'STRICT_TRANS_TABLES',
#             'charset': 'utf8mb4'
#         }
#     }
# }

# Determine which requests should render Django Debug Toolbar
INTERNAL_IPS = ('127.0.0.1',)

ENABLE_AUTO_AUTH = True

# Setting logging level
LOGGING['handlers']['default']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'

# settings for cronjobs
CRONTAB_DJANGO_SETTINGS_MODULE = 'milk.settings.dev'

# Seperate Migrations
MIGRATION_MODULES = {app: '%s.dev_migrations' % app for app in MIGRATE_APPS}
