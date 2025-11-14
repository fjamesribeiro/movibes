from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.events.views import home, subscribe_to_event, create_event, \
    gerenciar_galeria_evento, evento_detail_view, like_inscricao_view, \
    processar_curtida_presenca_view, mock_checkout_view, processar_pagamento_view
from apps.users.views import complete_aluno_profile, complete_profissional_profile, \
    set_profile_type, profile_view, gerenciar_galeria, public_profile_view, \
    adicionar_avaliacao_view, solicitar_conexao_view, listar_notificacoes_view, \
    responder_solicitacao_view, processar_like_back_view, \
    process_premium_payment_view, escolher_plano_view, checkout_assinatura_view, \
    processar_assinatura_view, cancelar_assinatura_view, historico_assinaturas_view, \
    mock_premium_checkout_view, escolher_plano_obrigatorio_view

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
    path('evento/<int:evento_id>/processar-pagamento/', processar_pagamento_view,
         name='processar_pagamento'),
    # Paths de Perfil
    path('perfil/profissional/<int:profissional_id>/avaliar/', adicionar_avaliacao_view,
         name='adicionar_avaliacao'),
    # PATHS PARA CONEXÕES
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
    # PATHS PARA PREMIUM (Sistema Antigo - pode ser removido futuramente)
    path('premium/process-payment/', process_premium_payment_view,
         name='process_premium_payment'),
    # URLs para Sistema de Assinaturas (Sistema Novo)
    path('assinatura/escolher-plano/', escolher_plano_view, name='escolher_plano'),
    path('assinatura/escolher-plano-obrigatorio/', escolher_plano_obrigatorio_view, name='escolher_plano_obrigatorio'),
    path('premium/checkout/', mock_premium_checkout_view, name='mock_premium_checkout'),

    path('assinatura/checkout/<int:plano_id>/', checkout_assinatura_view,
         name='checkout_assinatura'),
    path('assinatura/processar/<int:plano_id>/', processar_assinatura_view,
         name='processar_assinatura'),
    path('assinatura/cancelar/', cancelar_assinatura_view, name='cancelar_assinatura'),
    path('assinatura/historico/', historico_assinaturas_view,
         name='historico_assinaturas'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
