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

# ============================================================
# INSTALLED APPS
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # Necessário para campos avançados (como ArrayField)

    # Django-allauth: ORDEM IMPORTA!
    'django.contrib.sites',  # OBRIGATÓRIO para allauth
    'allauth',  # Core do Allauth (autenticação)
    'allauth.account',  # Gerenciamento de contas (login, register, etc)
    'allauth.socialaccount',  # Para login social (OAuth2)
    'allauth.socialaccount.providers.google',  # Provider do Google

    # Apps do projeto
    'apps.users.apps.UsersConfig',
    'apps.events.apps.EventsConfig',

    # Outras bibliotecas
    'tailwind',  # Gerenciamento do Tailwind CSS
    'theme',
    'django_htmx',  # Integração com HTMX
    'widget_tweaks',  # Facilita estilizar formulários
]

# ============================================================
# CONFIGURAÇÕES DO ALLAUTH E AUTENTICAÇÃO
# ============================================================

# ID do site atual - obrigatório para o django-allauth funcionar
SITE_ID = 1

# Backends de autenticação: permite login tanto tradicional (email/senha) quanto OAuth2
AUTHENTICATION_BACKENDS = [
    # Backend padrão do Django (username/password)
    'django.contrib.auth.backends.ModelBackend',
    # Backend do allauth para OAuth2 (Google, Facebook, etc.)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# --- CONFIGURAÇÕES GERAIS DE CONTA ---

# Método de autenticação: vamos usar email como identificador, não username
ACCOUNT_AUTHENTICATION_METHOD = 'email'

# Email é obrigatório no cadastro
ACCOUNT_EMAIL_REQUIRED = True

# Username não é obrigatório (vamos usar só email)
ACCOUNT_USERNAME_REQUIRED = False

# Cada email pode ser usado apenas uma vez no sistema
ACCOUNT_UNIQUE_EMAIL = True

# --- CONFIGURAÇÕES DE VERIFICAÇÃO DE EMAIL ---

# 'mandatory' = usuário DEVE verificar o email antes de fazer login
# 'optional' = pode logar sem verificar, mas é enviado um email de confirmação
# 'none' = não pede verificação (útil para desenvolvimento)
# Para desenvolvimento, use 'none'. Para produção, use 'mandatory'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Mude para 'mandatory' em produção!

# Dias até o link de confirmação de email expirar
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

# Prefixo para o assunto dos emails enviados pelo sistema
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[MoVibes] '

# --- CONFIGURAÇÕES DE LOGIN/LOGOUT ---

# Para onde redirecionar após login (será controlado pelo middleware)
LOGIN_REDIRECT_URL = 'home'

# Para onde redirecionar após logout
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# --- CONFIGURAÇÕES DE SIGNUP (Cadastro) ---

# Pedir senha duas vezes no cadastro para evitar erros de digitação
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True

# Manter o usuário logado por padrão
ACCOUNT_SESSION_REMEMBER = True

# Fazer login automaticamente após confirmar o email
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Fazer login automaticamente após resetar a senha
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

# Campo usado como username (None = não usa username)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# --- CONFIGURAÇÕES DE SOCIAL ACCOUNTS (OAuth2) ---

# Permite criação automática de conta ao fazer login com Google
SOCIALACCOUNT_AUTO_SIGNUP = True

# Se o Google já verificou o email, não pede verificação novamente
# Para usuários OAuth2, o email já vem verificado pelo provedor
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

# --- CONFIGURAÇÕES DO GOOGLE OAUTH2 ---

# Aqui configuramos os escopos (permissões) que vamos pedir ao Google
# e as credenciais do OAuth2
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         # O que vamos pedir de informação ao Google
#         'SCOPE': [
#             'profile',  # Nome, foto, etc.
#             'email',  # Email do usuário
#         ],
#         # Parâmetros extras para o OAuth2
#         'AUTH_PARAMS': {
#             'access_type': 'online',  # 'online' = sem refresh token (mais simples)
#         },
#         # Credenciais da aplicação Google (IMPORTANTE!)
#         # Você vai pegar esses valores no Google Cloud Console
#         'APP': {
#             'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
#             'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
#             'key': ''  # Não usado para Google
#         }
#     }
# }

# --- ADAPTERS CUSTOMIZADOS ---

# Estes adapters permitem customizar o comportamento do allauth
# Por exemplo, para salvar dados extras no cadastro, redirecionar para páginas específicas, etc.
ACCOUNT_ADAPTER = 'apps.users.adapter.MyAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'apps.users.adapter.MySocialAccountAdapter'

# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware do allauth - DEVE vir após o AuthenticationMiddleware
    'allauth.account.middleware.AccountMiddleware',
    'apps.users.middleware.ProfileCompletionMiddleware',  # Nosso middleware
]
# ============================================================
# TEMPLATES
# ============================================================
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
                # Obrigatório para allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.users.context_processors.notificacoes_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'movibes_project.wsgi.application'

# ============================================================
# DATABASE
# ============================================================
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}

# ============================================================
# PASSWORD VALIDATION
# ============================================================
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

# ============================================================
# INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True

# ============================================================
# STATIC & MEDIA FILES
# ============================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# OTHER SETTINGS
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.Usuario'
TAILWIND_APP_NAME = 'theme'

# ============================================================
# CONFIGURAÇÕES DE EMAIL
# ============================================================

# Para DESENVOLVIMENTO: emails aparecem no console (terminal)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'VibeSports <noreply@vibesports.com>'

# Para PRODUÇÃO: descomente e configure um serviço SMTP real (Gmail, SendGrid, etc.)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # seu@email.com
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # senha de app do Gmail
# DEFAULT_FROM_EMAIL = 'VibeSports <noreply@vibesports.com>'
