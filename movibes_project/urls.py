from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.events.views import home, subscribe_to_event, create_event
from apps.users.views import complete_aluno_profile, complete_profissional_profile, \
    set_profile_type, profile_view, gerenciar_galeria, public_profile_view

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/set-profile-type/<str:profile_type>/', set_profile_type, name='account_set_profile_type'),
    path('accounts/complete-profile/', complete_aluno_profile, name='account_complete_profile'),
    path('accounts/complete-profile-profissional/', complete_profissional_profile, name='account_complete_profile_profissional'),
    path('accounts/profile/', profile_view, name='profile'),
    path('accounts/galeria/', gerenciar_galeria, name='account_galeria'),
    path('subscribe-event/<int:event_id>/', subscribe_to_event, name='subscribe_event'),
    path('events/create/', create_event, name='create_event'),
    path('perfil/<int:usuario_id>/', public_profile_view, name='public_profile'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
