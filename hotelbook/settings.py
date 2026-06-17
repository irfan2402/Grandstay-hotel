# hotelbook/settings.py — HARDENED VERSION
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Core ──────────────────────────────────────────────────────────────────────
# SECRET_KEY loaded from .env — never hardcoded
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# Debug MUST be False in production; read from .env
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

# ── Apps ──────────────────────────────────────────────────────────────────────
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

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',          # CSRF protection ON
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',                      # Brute-force protection ON
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'hotelbook.middleware.SecurityHeadersMiddleware',       # CSP / security headers ON
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

# ── Password security ─────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# bcrypt via django-bcrypt compatible hasher (Argon2 / bcrypt both acceptable)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  # bcrypt — replaces MD5
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',        # fallback for legacy hashes
]

# ── Session / Cookie hardening ────────────────────────────────────────────────
SESSION_COOKIE_HTTPONLY  = True    # JS cannot read session cookie (XSS protection)
SESSION_COOKIE_SECURE    = True    # HTTPS only
SESSION_COOKIE_SAMESITE  = 'Lax'  # CSRF via cookie mitigated
SESSION_COOKIE_AGE       = 3600   # 1 hour idle timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_HTTPONLY  = True
CSRF_COOKIE_SECURE    = True
CSRF_COOKIE_SAMESITE  = 'Lax'

# ── Security headers ──────────────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER    = True
SECURE_CONTENT_TYPE_NOSNIFF  = True
X_FRAME_OPTIONS              = 'DENY'        # Clickjacking: deny all framing
SECURE_HSTS_SECONDS          = 31536000      # HSTS 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT          = not DEBUG     # Force HTTPS in production

# ── Brute-force protection (django-axes) ──────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AXES_FAILURE_LIMIT    = 5         # Lock after 5 failed attempts
AXES_COOLOFF_TIME     = 1         # Cooloff 1 hour
AXES_LOCKOUT_TEMPLATE = 'accounts/locked.html'
AXES_RESET_ON_SUCCESS = True

# ── File upload security ──────────────────────────────────────────────────────
# Files are stored in media_private/ which is NOT served by Django's
# static/media URL — preventing direct web access to uploaded files.
# Individual file validation (extension, MIME, size) happens in RoomForm.clean_image().
MEDIA_ROOT = BASE_DIR / 'media_private'   # outside web root
MEDIA_URL  = '/media/'                    # only served in dev; use nginx X-Accel-Redirect in prod

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024   # 5 MB hard cap (request layer)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024   # 5 MB

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_URL      = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT     = BASE_DIR / 'staticfiles'

# ── Logging ───────────────────────────────────────────────────────────────────
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
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ── URL / Auth ────────────────────────────────────────────────────────────────
LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kuala_Lumpur'
USE_I18N      = True
USE_TZ        = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
