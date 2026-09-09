# config/settings.py

import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


# تشخیص محیط Railway
IS_RAILWAY = "RAILWAY_ENVIRONMENT" in os.environ or "RAILWAY_PROJECT_ID" in os.environ

# متغیرهای محیطی از .env
SECRET_KEY = config(
    "DJANGO_SECRET_KEY", default="django-insecure-figmax-store-secret-key-12345"
)

# در محیط تولید (Railway) DEBUG را False کن
if IS_RAILWAY:
    DEBUG = False
else:
    DEBUG = config("DEBUG", default=True, cast=bool)

# ALLOWED_HOSTS
if IS_RAILWAY:
    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        ".up.railway.app",  # تمام دامنه‌های Railway
        ".railway.app",
        "figmaxshoptest.devs.surf",
        ".devs.surf",
    ]
else:
    ALLOWED_HOSTS = config(
        "ALLOWED_HOSTS", default="127.0.0.1,localhost,10.166.3.143"
    ).split(",")
    # حذف فاصله‌های اضافی
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]

# URLs
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# APPS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "whitenoise.runserver_nostatic",  # ← برای مدیریت بهتر فایل‌های استاتیک
    "apps.accounts",
    "apps.shop",
    "apps.orders",
    "apps.payments",
    "axes",
]


# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← برای فایل‌های استاتیک
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",  # ← کش
    "django.middleware.cache.FetchFromCacheMiddleware",  # ← کش
]

# CACHES FOR IMPROVING SPEED
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = "figmax"
CACHE_MIDDLEWARE_ALIAS = "default"


# Axes - امنیت ورود
AXES_FAILURE_LIMIT = 5  # ۵ بار تلاش اشتباه
AXES_COOLOFF_TIME = 1  # ۱ ساعت قفل
AXES_LOCK_OUT_AT_FAILURE = True
AXES_USERNAME_FORM_FIELD = "username"
AXES_PASSWORD_FORM_FIELD = "password"
AXES_IPWARE_IP_ADDRESS_HEADER = "HTTP_X_FORWARDED_FOR"
AXES_ENABLED = True
AXES_LOCKOUT_TEMPLATE = None
AXES_LOCKOUT_URL = None
AXES_VERBOSE = False  # غیرفعال کردن لاگ‌های اضافی

ROOT_URLCONF = "config.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {
                "shop_extras": "apps.shop.templatetags.shop_extras",
            },
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# دیتابیس - SQLite برای توسعه، PostgreSQL برای تولید
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME", default="figmax_db"),
            "USER": config("DB_USER", default="figmax_user"),
            "PASSWORD": config("DB_PASSWORD", default=""),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
            "OPTIONS": {
                "client_encoding": "UTF8",
            },
        }
    }


# LANGUAGE AND TIME
LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True


# STATIC AND MEDIA FILES
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# استفاده از WhiteNoise برای فایل‌های استاتیک
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# امنیت - HTTPS و SSL (فقط در محیط تولید)
if not DEBUG:
    # هدایت به HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # کوکی‌های امن
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True

    # HSTS - HTTP Strict Transport Security
    SECURE_HSTS_SECONDS = 31536000  # 1 سال
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # امنیت بیشتر
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "same-origin"

    # محدودیت فایل‌های آپلودی
    DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 مگابایت
    FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 مگابایت


# Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# لاگ‌گیری (Logging)
# در محیط تولید (Railway) لاگ‌ها به کنسول ارسال می‌شوند
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}


# ایمیل (SMTP) - برای تولید
if not DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@figmax.com")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Security Headers - برای تولید
if not DEBUG:
    SECURE_REFERRER_POLICY = "same-origin"
    SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"


# Session Settings
SESSION_COOKIE_AGE = 1209600  # 2 هفته
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# CSRF Settings
CSRF_COOKIE_AGE = 31449600  # 1 سال
CSRF_TRUSTED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]


# SUCCES AND FAILED MESSAGES
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}


# NUMBERS AND FORMATS
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ","
NUMBER_GROUPING = 3


# نرخ‌گذاری (Rate Limiting) - برای تولید
if not DEBUG:
    RATELIMIT_VIEW = "apps.shop.views.ratelimit_view"
