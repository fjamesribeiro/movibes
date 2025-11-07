from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.events.views import homepage, subscribe_to_event
from apps.users.views import complete_aluno_profile


urlpatterns = [
    path('', homepage, name='home'),
    path('admin/', admin.site.urls),
    path('subscribe-event/<int:event_id>/', subscribe_to_event, name='subscribe_event'),
    path('accounts/complete-profile/', complete_aluno_profile, name='account_complete_profile'),
    # Adiciona todas as URLs do django-allauth (como /login/, /signup/, /logout/, etc.)
    path('accounts/', include('allauth.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)