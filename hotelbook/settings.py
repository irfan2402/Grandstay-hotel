import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Load secrets from .env file

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-secret-key-change-in-production')  # Secret key from .env — never hardcoded

DEBUG = os.environ.get('DEBUG', 'True') == 'True'  # Disable in production

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')  # Restrict allowed hostnames

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',      # Brute-force protection
    'accounts',
    'rooms',
    'audit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',        # Adds HTTPS security headers
    'django.contrib.sessions.middleware.SessionMiddleware', # Manages user sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',            # CSRF protection — prevents cross-site request forgery
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',                       # Locks account after 5 failed logins
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Prevents clickjacking
    'hotelbook.middleware.SecurityHeadersMiddleware',       # Adds CSP, X-Frame, X-Content headers
    'hotelbook.middleware.AuditMiddleware',                 # Logs all security events
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
                'django.contrib.messages.context_processors.messages', # Auto-escapes output — prevents XSS
            ],
        },
    },
]

WSGI_APPLICATION = 'hotelbook.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # SQLite database
    }
}

# Strong password rules — OWASP ASVS V2.1
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # No similar to username
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},  # Min 10 chars
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},  # No common passwords
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},  # No all-numbers
]

# bcrypt hashing — more secure than MD5 or SHA1
# OWASP ASVS V2.4.1
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  # Strong password hashing
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',        # Fallback hasher
]

SESSION_COOKIE_HTTPONLY = True    # JavaScript cannot access session cookie — prevents XSS theft
SESSION_COOKIE_SECURE = False     # Set True in production with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'  # Prevents CSRF via cookie
SESSION_COOKIE_AGE = 1800         # Session expires after 30 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CSRF_COOKIE_HTTPONLY = True       # JavaScript cannot access CSRF cookie
CSRF_COOKIE_SECURE = False        # Set True in production with HTTPS
CSRF_COOKIE_SAMESITE = 'Lax'     # Prevents cross-site cookie sending

SECURE_BROWSER_XSS_FILTER = True    # Enable browser XSS filter
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'            # Block all iframe embedding — prevents clickjacking

# django-axes brute force settings — OWASP ASVS V2.2.1
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',          # Axes must be first
    'django.contrib.auth.backends.ModelBackend',    # Default Django auth
]
AXES_FAILURE_LIMIT = 5              # Lock after 5 failed attempts
AXES_COOLOFF_TIME = 1               # Lockout for 1 hour
AXES_LOCKOUT_TEMPLATE = 'accounts/locked.html'  # Custom locked page
AXES_RESET_ON_SUCCESS = True        # Reset counter on successful login

MEDIA_ROOT = BASE_DIR / 'media_private'  # Uploads stored outside web root
MEDIA_URL = '/media/'
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880    # Max upload 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880    # Max data upload 5MB

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

_log_dir = BASE_DIR / 'logs'
_log_dir.mkdir(exist_ok=True)

# Security logging — OWASP ASVS V7.1
# Logs login attempts, admin actions, errors
# Passwords are NEVER logged
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '[{asctime}] [{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # Rotating — max 10MB per file
            'filename': str(BASE_DIR / 'logs/security.log'),
            'maxBytes': 10485760,   # 10MB
            'backupCount': 5,       # Keep 5 backups
            'formatter': 'security',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'security',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

LOGIN_URL = '/accounts/login/'          # Redirect to login if not authenticated
LOGIN_REDIRECT_URL = '/dashboard/'      # Redirect after successful login
LOGOUT_REDIRECT_URL = '/accounts/login/'  # Redirect after logout

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kuala_Lumpur'  # Malaysia timezone
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'