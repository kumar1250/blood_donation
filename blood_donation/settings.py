# settings.py
from pathlib import Path
import os
from django.urls import reverse_lazy

# ---------------------------
# Base
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-your-secret-key'
DEBUG = True
ALLOWED_HOSTS = []

# ---------------------------
# Installed Apps
# ---------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your Apps
    'accounts',
    'blood_requests',
    'chat',
    'blood_camp',
    'channels',

    # Third-party
    'widget_tweaks',
]

# ---------------------------
# Authentication & Login/Logout
# ---------------------------
AUTH_USER_MODEL = "accounts.User"

# After login, redirect to root home page
LOGIN_REDIRECT_URL = reverse_lazy('home')    # matches path("", home_views.home, name="home") in urls.py

# Login page URL
LOGIN_URL = "/accounts/login/"

# After logout, redirect to login page
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ---------------------------
# Middleware
# ---------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------
# URL Config
# ---------------------------
ROOT_URLCONF = 'blood_donation.urls'

# ---------------------------
# Templates
# ---------------------------
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
        },
    },
]

# ---------------------------
# WSGI & ASGI
# ---------------------------
WSGI_APPLICATION = 'blood_donation.wsgi.application'
ASGI_APPLICATION = "blood_donation.asgi.application"

# ---------------------------
# Database (MySQL)
# ---------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blood_db',
        'USER': 'root',
        'PASSWORD': 'kumar@8121644559',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# ---------------------------
# Channels
# ---------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# ---------------------------
# Password Validators
# ---------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------
# Internationalization
# ---------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ---------------------------
# Static Files
# ---------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")] 
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------
# Email Settings
# ---------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "blood.2.3.4.doners@gmail.com"
EMAIL_HOST_PASSWORD = "wwjcpqhwtglajlan"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
