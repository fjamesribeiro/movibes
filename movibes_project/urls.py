from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.events.views import homepage, subscribe_to_event, create_event
from apps.users.views import complete_aluno_profile, complete_profissional_profile, \
    select_profile_type, set_profile_type, profile_view

urlpatterns = [
    path('', homepage, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/set-profile-type/<str:profile_type>/', set_profile_type, name='account_set_profile_type'),
    path('accounts/select-profile-type/', select_profile_type, name='account_select_profile_type'),
    path('accounts/complete-profile/', complete_aluno_profile, name='account_complete_profile'),
    path('accounts/complete-profile-profissional/', complete_profissional_profile, name='account_complete_profile_profissional'),
    path('accounts/profile/', profile_view, name='profile'),
    path('subscribe-event/<int:event_id>/', subscribe_to_event, name='subscribe_event'),
    path('events/create/', create_event, name='create_event'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
