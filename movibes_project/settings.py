import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.getenv('SECRET_KEY', 'uma-chave-secreta-padrao-caso-nao-ache-no-env')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS = ['movibes.linexa.com.br', '127.0.0.1', '192.168.56.1', '192.168.0.163']
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://movibes.linexa.com.br']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # Necessário para campos avançados (como ArrayField)
    'django.contrib.sites',  # OBRIGATÓRIO para allauth
    'allauth',              # Core do Allauth (autenticação)
    'allauth.account',      # Gerenciamento de contas (login, register, etc)
    'allauth.socialaccount', # Para login social (OAuth2)
    'allauth.socialaccount.providers.google',  # Provider do Google
    'apps.users.apps.UsersConfig',
    'apps.events.apps.EventsConfig',
    'tailwind',      # Gerenciamento do Tailwind CSS
    'theme',
    'django_htmx',          # Integração com HTMX
    'widget_tweaks', # Facilita estilizar formulários
]

# ID do site atual (obrigatório para allauth)
SITE_ID = 1

# Configurações de autenticação
AUTHENTICATION_BACKENDS = [
    # Backend padrão do Django (username/password)
    'django.contrib.auth.backends.ModelBackend',

    # Backend do allauth para OAuth2
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'movibes_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'theme' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.users.context_processors.notificacoes_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'movibes_project.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}

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

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Fortaleza'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.Usuario'

TAILWIND_APP_NAME = 'theme'

LOGOUT_REDIRECT_URL = '/'

LOGIN_REDIRECT_URL = 'home'

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = [
    'email*',
    'password1*',
    'password2*',
]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = 'apps.users.adapter.MyAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'apps.users.adapter.MySocialAccountAdapter'
