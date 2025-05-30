"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(env_file=str(BASE_DIR / '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', True)

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework',
    'django_celery_results',
    'drf_spectacular',
    'stackexchange.apps.StackExchangeConfig'
]

if DEBUG:
    # Add apps needed for development
    INSTALLED_APPS += ['debug_toolbar', 'django_extensions']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    # Debug toolbar configuration
    INTERNAL_IPS = ['127.0.0.1']
    # Display full SQL for runserver plus
    RUNSERVER_PLUS_PRINT_SQL_TRUNCATE = None

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': env('DB_HOST', default='localhost'),
        'NAME': env('DB_NAME', default='stackexchange'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'PORT': env('DB_PORT', default=5432),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
AUTH_USER_MODEL = 'stackexchange.User'

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'stackexchange.pagination.Pagination',
    'DEFAULT_SCHEMA_CLASS': 'stackexchange.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'stackexchange.exceptions.application_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': (
        'stackexchange.throttles.Burst',
        'stackexchange.throttles.Sustained'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'burst': '30/sec',
        'sustained': '10000/day'
    }
}

# DRF Spectacular configuration

SPECTACULAR_SETTINGS = {
    'TITLE': 'Stack Exchange API',
    'DESCRIPTION': open(BASE_DIR / 'stackexchange/templates/doc/description.md').read(),
    'VERSION': '2.3',
}

# Temporary directory in which the dump files will be extracted

TEMP_DIR = env('TEMP_DIR', default=None)

# Redis configuration

REDIS_URL = env('REDIS_URL', default="redis://127.0.0.1:6379")

# Celery configuration

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default="redis://127.0.0.1:6379/1")
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Cache settings

CACHE_LOCATION = env('CACHE_LOCATION', default="redis://127.0.0.1:6379/0")
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': CACHE_LOCATION,
    }
}
