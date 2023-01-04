import environ
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1zxrl5l%&9$@1w!uy$*))#25&0entg4at4d(my2ls(-^0hiykf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = [env("ALLOWED_HOSTS")]


# Application definition
DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework', 
    'simple_history',
    'corsheaders',
    'django_filters',
    'rest_framework_simplejwt.token_blacklist',
    'django_rest_resetpassword',
    'drf_spectacular',
    'debug_toolbar',
]

RIMS_APPS = [
    'src.user', 
    'src.user_group', 
    'log_app',
    'src.core_app',
    'src.rims_setup',
    'src.customer',
    'src.item',
    'src.customer_order',
    'src.supplier',
    'src.advance_deposit',
    'src.party_payment',
    'src.purchase',
    'src.sale',
    'src.credit_management',
    'tenant']

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + RIMS_APPS    # list all all installed apps

# Middlewares 
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # django-cors-headers middlefor CSRF token
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',   # django debug toolbar
    'tenant.middlewares.TenantMiddleware',  # custom middleware for tenants

    'simple_history.middleware.HistoryRequestMiddleware',   # simple-history-middleware to track user

    # 'ipinfo_django.middleware.IPinfo',  # ipaddress, for detecting login location
]

# setting for Django debug toolbar
INTERNAL_IPS = [

    '127.0.0.1',
    # 'customer1.example.com'

]

ROOT_URLCONF = 'rims.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'rims.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT"),
    },
    'log_db': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('LOG_DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT"),
    }
}

# to route log_app to log_db and other apps to default database
DATABASE_ROUTERS = ["tenant.router.HistoryRouter"]

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

# ROOT for midia fies like images
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Max upload size ( in Bytes) for image fies 
MAX_UPLOAD_SIZE = 2000000

# DjangoRestFramework settings 
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',

    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        # custom JWT authentication to enforce Schema aware authentication
        "custom_jwt_authentication.JWTAuthentication",

        # for debugging purpose
        "rest_framework.authentication.SessionAuthentication",
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "DEFAULT_PERMISSION_CLASSES": (
        # 'rest_framework.permissions.AllowAny',
        "rest_framework.permissions.IsAuthenticated",
    ),

}
# json web token configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# Setting default User app
AUTH_USER_MODEL = 'user.User'


# django-cros-headers settings 
# CORS_ALLOWED_ORIGINS = [
#     "https://example.com",
#     "https://sub.example.com",
# ]
CORS_ALLOW_ALL_ORIGINS = True


# remove slash from end of api urls
APPEND_SLASH = False


# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'dipee.info@gmail.com'
SERVER_EMAIL = 'dipee.info@gmail.com'
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "dipee.info@gmail.com"
EMAIL_HOST_PASSWORD = "voqhmmpuaqidgxwg"
EMAIL_PORT = 587

SPECTACULAR_SETTINGS = {
    'TITLE': 'RIMS_NG_BACKEND',
    'DESCRIPTION': 'Next Gen Restaurant Management System',
    'VERSION': '1.0.0',
}
