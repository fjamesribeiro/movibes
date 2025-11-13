from django.contrib import admin
from .models import Usuario, Perfil, Aluno, Profissional, UsuarioPerfil, TipoConta, \
    StatusSocial, VibeAfterOpcao, Avaliacao, SolicitacaoConexao

admin.site.register(Usuario)
admin.site.register(Perfil)
admin.site.register(UsuarioPerfil)
admin.site.register(Aluno)
admin.site.register(Profissional)
admin.site.register(TipoConta)
admin.site.register(StatusSocial)
admin.site.register(VibeAfterOpcao)
admin.site.register(Avaliacao)
admin.site.register(SolicitacaoConexao)
