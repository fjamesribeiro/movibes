import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'uma-chave-secreta-padrao-caso-nao-ache-no-env')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS = ['movibes.linexa.com.br', '127.0.0.1', '192.168.56.1', '192.168.0.163']

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://movibes.linexa.com.br']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # Necessário para campos avançados (como ArrayField)
    # Nossas Apps
    'apps.users.apps.UsersConfig',   # <-- MUDE AQUI
    'apps.events.apps.EventsConfig', # <-- MUDE AQUI
    # Apps de Terceiros
    'tailwind',      # Gerenciamento do Tailwind CSS
    'theme',
    'django_htmx',          # Integração com HTMX
    'widget_tweaks', # Facilita estilizar formulários

    'allauth',              # Core do Allauth (autenticação)
    'allauth.account',      # Gerenciamento de contas (login, register, etc)
    'allauth.socialaccount', # Para login social (OAuth2)
    # ... aqui virão os provedores, ex: 'allauth.socialaccount.providers.google'
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
            ],
        },
    },
]

WSGI_APPLICATION = 'movibes_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Fortaleza'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Onde o Django vai procurar por arquivos estáticos (logo, fundo)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Onde o Django vai salvar os uploads dos usuários (fotos de perfil, etc)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Configuração do Modelo de Usuário ---
# CRÍTICO: Isso diz ao Django para usar o nosso modelo 'Usuario'
# (que vamos criar) em vez do User padrão.
# DEVE ser feito ANTES da primeira migração.
AUTH_USER_MODEL = 'users.Usuario'

# --- Configuração do Tailwind ---
# Define o nome da app que conterá os temas do Tailwind
TAILWIND_APP_NAME = 'theme'

# --- Configuração do Allauth (Autenticação) ---
# Necessário para o allauth funcionar
LOGOUT_REDIRECT_URL = '/'

# Configura o allauth para usar email como login (sem username)
ACCOUNT_AUTHENTICATION_METHOD = 'email' # Mantém para compatibilidade
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = 'apps.users.adapter.MyAccountAdapter'
