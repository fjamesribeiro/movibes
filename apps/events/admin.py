from django.contrib import admin
# Importa os 2 modelos que você criou em models.py
from .models import Evento, Inscricao

# Registra os modelos para que eles apareçam no /admin
admin.site.register(Evento)
admin.site.register(Inscricao)