"""
Django settings for convabout project.

Generated by 'django-admin startproject' using Django 2

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from os.path import join

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('CONVABOUT_SECRET_KEY', '7(%1a$pzgdnr%tt3g(^wd@vn_8ryc6fkbdf$ct@%$xa2*+2ku1')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'False'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps
    'core',

    # 3rd party
    'rest_framework',
    'channels',
    'django_eventstream',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_grip.GripMiddleware',
]

#https://stackoverflow.com/questions/58917396/fetch-not-sending-cookies
SESSION_COOKIE_SAMESITE=None

# as localhost is http not https
SESSION_COOKIE_SECURE = False if DEBUG else True

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = ['http://127.0.0.1:8081'] if DEBUG else ['https://convabout.com']
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'convabout.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'convabout.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Heroku: Update database configuration from $DATABASE_URL.
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

# {
#     'NAME':
#  'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
# },
# {
#     'NAME':
# 'django.contrib.auth.password_validation.MinimumLengthValidator',
# },
# {
#     'NAME':
# 'django.contrib.auth.password_validation.CommonPasswordValidator',
# },
# {
#     'NAME':
# 'django.contrib.auth.password_validation.NumericPasswordValidator',
# },

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
    # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

MESSAGES_TO_LOAD = 15

# In settings.py
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgiref.inmemory.ChannelLayer",
        "ROUTING": "core.routing.channel_routing",
    },
}
# Could be changed to the config below to scale:
# "BACKEND": "asgi_redis.RedisChannelLayer",
# "CONFIG": {
#     "hosts": [("localhost", 6379)],
# },

# > 100 years
SESSION_COOKIE_AGE = 5000000000 

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

# Collect static files here
STATIC_ROOT = join(PROJECT_ROOT, 'run', 'static_root')

# Collect media files here
MEDIA_ROOT = join(PROJECT_ROOT, 'run', 'media_root')
MEDIA_URL = '/media/'

# look for static assets here
STATICFILES_DIRS = [
    join(PROJECT_ROOT, 'static'),
]

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

ALLOWED_HOSTS = ['convabout.herokuapp.com','127.0.0.1']
EVENTSTREAM_ALLOW_ORIGIN = '*' if DEBUG else 'convabout.herokuapp.com'
print(EVENTSTREAM_ALLOW_ORIGIN)
EVENTSTREAM_ALLOW_CREDENTIALS = True

ASGI_APPLICATION = 'convabout.routing.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

# for testing next keys can be used:
# Site key: 6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI, Secret key: 6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
# https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do
GOOGLE_RECAPTCHA_SECRET_KEY = (os.environ.get('LOCALHOST_RECAPTCHA_SECRET_KEY','')
                               if DEBUG
                               else os.environ.get('RECAPTCHA_SECRET_KEY','') )