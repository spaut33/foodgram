import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', default='django-secret-key')
DEBUG = os.getenv('DEBUG', default=False) == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', default='127.0.0.1').split()

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',  # shell_plus --ipython
    'drf_yasg',
    'rest_framework.authtoken',
    'corsheaders',
    'djoser',
    'colorfield',
    'django_filters',
    'core',
    'users',
    'recipes',
    'api',
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
]

ROOT_URLCONF = 'foodgram.urls'

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
            ]
        },
    }
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': os.getenv('POSTGRES_DB', default=BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('POSTGRES_USER', default='postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
        'HOST': os.getenv('DB_HOST', default='db'),
        'PORT': os.getenv('DB_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'PAGE_SIZE': 6,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
}

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Foodgram settings
USERNAME_LENGTH = 150
EMAIL_LENGTH = 150
USER_FIRSTNAME_LENGTH = 150
USER_LASTNAME_LENGTH = 254
USER_PASSWORD_LENGTH = 150
RECIPE_NAME_MAX_LENGTH = 200
RECIPE_MIN_COOKING_TIME = 1
INGREDIENT_NAME_MAX_LENGTH = 200
INGREDIENT_MIN_VALUE = 1
UNIT_NAME_MAX_LENGTH = 200
TAG_MAX_LENGTH = 200
MAX_TAG_SLUG_LENGTH = 200

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_ALLOW_ALL = False
    # https://dev.to/ashiqursuperfly/all-things-security-dockerizing-django-for-deploying-anywhere-5eo2
    SECURE_HSTS_SECONDS = 86400
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    X_FRAME_OPTIONS = 'DENY'

CORS_URLS_REGEX = r'^/api/.*$'
CORS_ORIGIN_WHITELIST = os.environ.get(
    'CORS_WHITELIST', default='http://localhost'
).split()

# Djoser
DJOSER = {
    'LOGIN_FIELD': 'email',
    'SEND_ACTIVATION_EMAIL': False,
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user': ['rest_framework.permissions.IsAuthenticated'],
    },
    'SERIALIZERS': {
        'user': 'api.serializers.user_serializers.UserSerializer',
        'current_user': 'api.serializers.user_serializers.UserSerializer',
        'user_create': 'api.serializers.user_serializers.RegisterUserSerializer',
    },
}

# Swagger auth settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {'name': 'Authorization', 'type': 'apiKey', 'in': 'header'}
    }
}
