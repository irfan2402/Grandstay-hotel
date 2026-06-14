# hotelbook/settings.py - VULNERABLE VERSION (BEFORE HARDENING)
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# VULNERABLE: Hardcoded secret key
SECRET_KEY = 'hardcoded-insecure-secret-key-do-not-use-in-production-12345'

# VULNERABLE: Debug mode exposes stack traces and system info
DEBUG = True

ALLOWED_HOSTS = ['*']  # VULNERABLE: Accepts all hostnames

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',
    'accounts',
    'rooms',
    'audit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # VULNERABLE: CSRF protection disabled — forms vulnerable to CSRF attacks
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # VULNERABLE: No brute force protection — unlimited login attempts
    # 'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # VULNERABLE: No security headers — missing CSP, X-Frame, X-Content
    # 'hotelbook.middleware.SecurityHeadersMiddleware',
    'hotelbook.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'hotelbook.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'hotelbook.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# VULNERABLE: No password validation — accepts weak passwords like "123"
AUTH_PASSWORD_VALIDATORS = []

# VULNERABLE: MD5 password hashing — easily cracked
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# VULNERABLE: Session cookie accessible to JavaScript — XSS can steal it
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False
# VULNERABLE: No SameSite — CSRF via cookie possible
SESSION_COOKIE_SAMESITE = None
# VULNERABLE: Session never expires — session hijacking risk
SESSION_COOKIE_AGE = 999999
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# VULNERABLE: CSRF cookie accessible to JavaScript
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = None

# VULNERABLE: No XSS filter
SECURE_BROWSER_XSS_FILTER = False
# VULNERABLE: MIME sniffing allowed
SECURE_CONTENT_TYPE_NOSNIFF = False
# VULNERABLE: Clickjacking possible via iframe
X_FRAME_OPTIONS = 'SAMEORIGIN'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
# VULNERABLE: No brute force limit
AXES_FAILURE_LIMIT = 999
AXES_COOLOFF_TIME = 0
AXES_LOCKOUT_TEMPLATE = 'accounts/locked.html'
AXES_RESET_ON_SUCCESS = True

MEDIA_ROOT = BASE_DIR / 'media_private'
MEDIA_URL = '/media/'
# VULNERABLE: No file size limit
FILE_UPLOAD_MAX_MEMORY_SIZE = 999999999
DATA_UPLOAD_MAX_MEMORY_SIZE = 999999999

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

_log_dir = BASE_DIR / 'logs'
_log_dir.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {'format': '[{asctime}] [{levelname}] {message}', 'style': '{'},
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(BASE_DIR / 'logs/security.log'),
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'security',
        },
        'console': {'class': 'logging.StreamHandler', 'formatter': 'security'},
    },
    'loggers': {
        'security': {'handlers': ['security_file', 'console'], 'level': 'INFO', 'propagate': False},
    },
}

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kuala_Lumpur'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'