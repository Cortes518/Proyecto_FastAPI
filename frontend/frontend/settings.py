# frontend/frontend/settings.py
from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-your-secret-key-change-in-prod')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*').split(',') if h.strip()]

# CSRF Trusted Origins for Render and Vercel
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in config(
        'CSRF_TRUSTED_ORIGINS',
        default='https://*.onrender.com,https://*.vercel.app,http://localhost:8000,http://127.0.0.1:8000'
    ).split(',') if o.strip()
]

# Application definition
INSTALLED_APPS = [
    'daphne',  # Para ASGI
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'frontend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'app' / 'templates'],
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

WSGI_APPLICATION = 'frontend.wsgi.application'
ASGI_APPLICATION = 'frontend.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'app' / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# FastAPI Backend URL
_raw_fastapi_url = config('FASTAPI_URL', default='http://localhost:8001').strip().rstrip('/')

if not _raw_fastapi_url.startswith(('http://', 'https://')):
    # Si Render pasó solo el host, ej: "aforo-fastapi-backend" o "aforo-fastapi-backend.onrender.com"
    if '.' not in _raw_fastapi_url and 'localhost' not in _raw_fastapi_url:
        _raw_fastapi_url = f"{_raw_fastapi_url}.onrender.com"
    FASTAPI_URL = f"https://{_raw_fastapi_url}"
elif 'localhost' not in _raw_fastapi_url and '127.0.0.1' not in _raw_fastapi_url and not _raw_fastapi_url.startswith('https://'):
    if 'onrender.com' in _raw_fastapi_url:
        FASTAPI_URL = _raw_fastapi_url.replace('http://', 'https://')
    elif '.' not in _raw_fastapi_url.split('://')[1].split(':')[0]:
        _host = _raw_fastapi_url.split('://')[1].split(':')[0]
        FASTAPI_URL = f"https://{_host}.onrender.com"
    else:
        FASTAPI_URL = _raw_fastapi_url
else:
    FASTAPI_URL = _raw_fastapi_url

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 7  # 7 días
