from django.apps import AppConfig

# A CLASSE DEVE SE CHAMAR UsersConfig
class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'