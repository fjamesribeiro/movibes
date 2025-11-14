from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.events.views import home, subscribe_to_event, create_event, \
    gerenciar_galeria_evento, evento_detail_view, like_inscricao_view, \
    processar_curtida_presenca_view, mock_checkout_view
from apps.users.views import complete_aluno_profile, complete_profissional_profile, \
    set_profile_type, profile_view, gerenciar_galeria, public_profile_view, \
    adicionar_avaliacao_view, solicitar_conexao_view, listar_notificacoes_view, \
    responder_solicitacao_view, processar_like_back_view

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/set-profile-type/<str:profile_type>/', set_profile_type,
         name='account_set_profile_type'),
    path('accounts/complete-profile/', complete_aluno_profile,
         name='account_complete_profile'),
    path('accounts/complete-profile-profissional/', complete_profissional_profile,
         name='account_complete_profile_profissional'),
    path('accounts/profile/', profile_view, name='profile'),
    path('accounts/galeria/', gerenciar_galeria, name='account_galeria'),
    path('subscribe-event/<int:event_id>/', subscribe_to_event, name='subscribe_event'),
    path('events/create/', create_event, name='create_event'),
    path('perfil/<int:usuario_id>/', public_profile_view, name='public_profile'),
    # Paths de Eventos
    path('evento/<int:evento_id>/galeria/', gerenciar_galeria_evento,
         name='account_galeria_evento'),
    path('evento/<int:evento_id>/', evento_detail_view, name='evento_detail'),
    path('evento/<int:evento_id>/comprar/', mock_checkout_view, name='mock_checkout'),
    # Paths de Perfil
    path('perfil/profissional/<int:profissional_id>/avaliar/', adicionar_avaliacao_view,
         name='adicionar_avaliacao'),
    # PATHS PARA CONEXÕES ---
    path('solicitar-conexao/<int:usuario_id>/', solicitar_conexao_view,
         name='solicitar_conexao'),
    path('notificacoes/', listar_notificacoes_view, name='listar_notificacoes'),
    path('notificacoes/responder/<int:solicitacao_id>/<str:acao>/',
         responder_solicitacao_view, name='responder_solicitacao'),
    path('inscricao/<int:inscricao_id>/like/', like_inscricao_view,
         name='like_inscricao'),
    # Rota para curtir alguém na lista de participantes do evento
    path('inscricao/<int:inscricao_id>/curtir/', processar_curtida_presenca_view,
         name='curtir_presenca'),
    # Rota para curtir de volta na tela de notificações
    path('interacao/<int:interacao_id>/like-back/', processar_like_back_view,
         name='like_back'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
