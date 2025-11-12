from django.contrib import admin
from .models import Evento, Inscricao, CategoriaEvento, FotoEvento


@admin.register(CategoriaEvento)
class CategoriaEventoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'eventos_count']
    search_fields = ['nome']

    def eventos_count(self, obj):
        return obj.eventos.count()

    eventos_count.short_description = 'Nº de Eventos'


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nome_evento', 'categoria', 'data_e_hora', 'vagas_restantes', 'id_criador']
    list_filter = ['categoria', 'status', 'data_e_hora']
    search_fields = ['nome_evento', 'descricao_do_evento']
    date_hierarchy = 'data_e_hora'


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ['id_aluno', 'id_evento', 'created_at']
    list_filter = ['created_at']
    search_fields = ['id_aluno__usuario__email', 'id_evento__nome_evento']

admin.site.register(FotoEvento)
