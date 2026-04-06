# Security Configuration for Docker
# Add these security settings to your Django settings.py

import os
from pathlib import Path
import environ

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECURE_SSL_REDIRECT=(bool, True),
    SECURE_HSTS_SECONDS=(int, 31536000),
    SESSION_COOKIE_SECURE=(bool, True),
    CSRF_COOKIE_SECURE=(bool, True),
)

# Take environment variables from .env file
# Try to read .env from multiple possible locations
env_file_paths = [
    BASE_DIR / '.env',
    Path('.env'),
    Path(__file__).parent.parent / '.env'
]

for env_path in env_file_paths:
    if env_path.exists():
        environ.Env.read_env(str(env_path))
        break

# Security Settings from Environment Variables
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=not DEBUG)
SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS', default=0 if DEBUG else 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=not DEBUG)
SECURE_HSTS_PRELOAD = env('SECURE_HSTS_PRELOAD', default=not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = env('SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = env('SECURE_BROWSER_XSS_FILTER', default=True)
SECURE_REFERRER_POLICY = env('SECURE_REFERRER_POLICY', default='strict-origin-when-cross-origin')

# Session Security
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=not DEBUG)
SESSION_COOKIE_HTTPONLY = env('SESSION_COOKIE_HTTPONLY', default=True)
SESSION_COOKIE_SAMESITE = env('SESSION_COOKIE_SAMESITE', default='Strict')
SESSION_COOKIE_AGE = env('SESSION_COOKIE_AGE', default=3600)  # 1 hour

# CSRF Security
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=not DEBUG)
CSRF_COOKIE_HTTPONLY = env('CSRF_COOKIE_HTTPONLY', default=True)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = env('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880)  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = env('DATA_UPLOAD_MAX_MEMORY_SIZE', default=5242880)  # 5MB
FILE_UPLOAD_PERMISSIONS = env('FILE_UPLOAD_PERMISSIONS', default=0o644)

# JWT Security
JWT_SECRET_KEY = env('JWT_SECRET_KEY', default=SECRET_KEY)
SIMPLE_JWT.update({
    'SIGNING_KEY': JWT_SECRET_KEY,
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env('JWT_ACCESS_TOKEN_LIFETIME', default=60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env('JWT_REFRESH_TOKEN_LIFETIME', default=7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
})

# Email Security (use environment-specific backend)
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': env('LOG_LEVEL', default='INFO'),
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': env('LOG_LEVEL', default='INFO'),
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': env('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'shop': {
            'handlers': ['console', 'file'],
            'level': env('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

# Create logs directory
os.makedirs('/app/logs', exist_ok=True)
