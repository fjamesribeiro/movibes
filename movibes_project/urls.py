from django.contrib import admin
from django.urls import path, include
from apps.events.views import home, subscribe_to_event, create_event, \
    gerenciar_galeria_evento, evento_detail_view, like_inscricao_view, \
    processar_curtida_presenca_view, mock_checkout_view, processar_pagamento_view
from apps.users.views import complete_aluno_profile, complete_profissional_profile, \
     profile_view, gerenciar_galeria, public_profile_view, \
    adicionar_avaliacao_view, solicitar_conexao_view, listar_notificacoes_view, \
    responder_solicitacao_view, processar_like_back_view, \
    process_premium_payment_view, escolher_plano_view, checkout_assinatura_view, \
    processar_assinatura_view, cancelar_assinatura_view, historico_assinaturas_view, \
    mock_premium_checkout_view, escolher_plano_obrigatorio_view

urlpatterns = [
    # Página inicial
    path('', home, name='home'),

    # Admin do Django
    path('admin/', admin.site.urls),

    # URLs do django-allauth (login, logout, signup, OAuth2, etc.)
    # Isso inclui automaticamente todas as URLs necessárias para autenticação
    path('accounts/', include('allauth.urls')),

    # Rotas customizadas de perfil/conta
    path('accounts/complete-profile/', complete_aluno_profile,
         name='account_complete_profile'),
    path('accounts/complete-profile-profissional/', complete_profissional_profile,
         name='account_complete_profile_profissional'),
    path('accounts/profile/', profile_view, name='profile'),
    path('accounts/galeria/', gerenciar_galeria, name='account_galeria'),
    # Rotas de eventos
    path('subscribe-event/<int:event_id>/', subscribe_to_event, name='subscribe_event'),
    path('events/create/', create_event, name='create_event'),
    path('evento/<int:evento_id>/galeria/', gerenciar_galeria_evento,
         name='account_galeria_evento'),
    path('evento/<int:evento_id>/', evento_detail_view, name='evento_detail'),
    path('evento/<int:evento_id>/comprar/', mock_checkout_view, name='mock_checkout'),
    path('evento/<int:evento_id>/processar-pagamento/', processar_pagamento_view,
         name='processar_pagamento'),

    # Rotas de perfil público
    path('perfil/<int:usuario_id>/', public_profile_view, name='public_profile'),
    path('perfil/profissional/<int:profissional_id>/avaliar/', adicionar_avaliacao_view,
         name='adicionar_avaliacao'),

    # Rotas de conexões entre usuários
    path('solicitar-conexao/<int:usuario_id>/', solicitar_conexao_view,
         name='solicitar_conexao'),
    path('notificacoes/', listar_notificacoes_view, name='listar_notificacoes'),
    path('notificacoes/responder/<int:solicitacao_id>/<str:acao>/',
         responder_solicitacao_view, name='responder_solicitacao'),

    # Rotas de interações (likes, curtidas)
    path('inscricao/<int:inscricao_id>/like/', like_inscricao_view,
         name='like_inscricao'),
    path('inscricao/<int:inscricao_id>/curtir/', processar_curtida_presenca_view,
         name='curtir_presenca'),
    path('interacao/<int:interacao_id>/like-back/', processar_like_back_view,
         name='like_back'),

    # Rotas de sistema de premium/assinaturas
    path('premium/process-payment/', process_premium_payment_view,
         name='process_premium_payment'),
    path('premium/checkout/', mock_premium_checkout_view, name='mock_premium_checkout'),
    path('assinatura/escolher-plano/', escolher_plano_view, name='escolher_plano'),
    path('assinatura/escolher-plano-obrigatorio/', escolher_plano_obrigatorio_view,
         name='escolher_plano_obrigatorio'),
    path('assinatura/checkout/<int:plano_id>/', checkout_assinatura_view,
         name='checkout_assinatura'),
    path('assinatura/processar/<int:plano_id>/', processar_assinatura_view,
         name='processar_assinatura'),
    path('assinatura/cancelar/', cancelar_assinatura_view, name='cancelar_assinatura'),
    path('assinatura/historico/', historico_assinaturas_view,
         name='historico_assinaturas'),
]
