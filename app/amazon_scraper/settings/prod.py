from .base import *

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'amazon_scraper',
    'USER': 'root',
    'HOST': 'localhost',
    'PASSWORD': 'P@ssw0rd1',
    'PORT': '3306'
  }
}

DEFAULT_FROM_EMAIL = 'amazon scraper admin<mailadmin@asin-jan.com>'
DEFAULT_CHARSET = 'utf-8'
EMAIL_HOST = 'mail.asin-jan.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'mailadmin@asin-jan.com'
EMAIL_HOST_PASSWORD = 'P@ssw0rd1'
EMAIL_USE_TLS = True
