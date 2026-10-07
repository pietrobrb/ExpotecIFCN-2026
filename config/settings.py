from pathlib import Path
import os
from dotenv import  load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False').lower() == 'true')

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", default="127.0.0.1").split(" ")

if os.getenv("CSRF_TRUSTED_ORIGINS"):
    CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split()

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'suap_oauth',
    'crispy_bootstrap5',
    "crispy_forms",
    'django_extensions',
    'django_filters',
    'django_tables2',
    'simple_menu',
    'django_htmx',
    "django_select2",
    "betterforms",
    "jquery",
    "djangoformsetjs",
    "django_summernote",
    "rules.apps.AutodiscoverRulesConfig",
    'rest_framework',
    'imagekit',
    'core',
    'portal',
    'usuarios',
    "eventos",
    "atividades",
    "enderecos",
    "documentos",
    "chamadas",
    "submissao",
    "credenciamento"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'eventos.middleware.EventoSelecionadoMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.google_maps',
            ],
        },
    },
]


FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"


WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
if (DEBUG):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv("DB_NAME"),
            'HOST': os.getenv("DB_HOST"),
            'PORT': os.getenv("DB_PORT"),
            'USER': os.getenv("DB_USER"),
            'PASSWORD': os.getenv("DB_PASSWORD"),
        }
    }

# Using Redis as cache in production
if (not DEBUG):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        },
        'select2': {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/2",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    # Set the cache backend to select2
    SELECT2_CACHE_BACKEND = 'select2'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# URL para arquivos estáticos
STATIC_URL = 'static/'
MEDIA_URL = "media/"

# Diretórios adicionais para arquivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Diretório onde os arquivos estáticos coletados serão armazenados
if (DEBUG):
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    STATIC_ROOT = os.getenv("STATIC_ROOT")
    MEDIA_ROOT = os.getenv("MEDIA_ROOT")


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# config users
AUTH_USER_MODEL = 'usuarios.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'user:index'
LOGOUT_REDIRECT_URL = 'portal:index'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_CHANGE_EMAIL = True
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_FORMS = {
    'signup': 'usuarios.forms.UserSignupForm',
    'login': 'usuarios.forms.UserLoginForm',
    'reset_password': 'usuarios.forms.UserResetPasswordForm',
    'reset_password_from_key': 'usuarios.forms.UserResetPasswordKeyForm',
}

SOCIALACCOUNT_ADAPTER = 'suap_oauth.adapter.SuapAdapter'
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    "suap": {
        "VERIFIED_EMAIL": True,
        'EMAIL_AUTHENTICATION': True,
        "APPS": [
            {
                "client_id": os.getenv("SUAP_CLIENT_ID"),
                "secret": os.getenv("SUAP_CLIENT_SECRET"),
            },
        ],
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True


SELECT2_CSS = ""
SELECT2_JS = ""
SELECT2_THEME = "bootstrap-5"


SUMMERNOTE_THEME = 'bs5'
SUMMERNOTE_CONFIG = {
    'summernote': {
        'airMode': False,
        'width': '100%',
        'height': '250px',
        'lang': "pt-br",
        'toolbar': [
            ['style', []],
            ['font', ['bold', 'underline', 'clear']],
            ['color', []],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['view', ['fullscreen', 'help']],
        ],
        'disableResizeEditor': True,
    },
    'lazy': True,
    # You can completely disable the attachment feature.
    'disable_attachment': True,

}


X_FRAME_OPTIONS = "SAMEORIGIN"

