from django.contrib import admin
from .models import Usuario, Perfil, Aluno, Profissional

admin.site.register(Usuario)
admin.site.register(Perfil)
admin.site.register(Aluno)
admin.site.register(Profissional)