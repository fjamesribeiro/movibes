from django.contrib import admin
# Importa os 4 modelos que você criou em models.py
from .models import Usuario, Perfil, Aluno, Profissional

# Registra os modelos para que eles apareçam no /admin
admin.site.register(Usuario)
admin.site.register(Perfil)
admin.site.register(Aluno)
admin.site.register(Profissional)