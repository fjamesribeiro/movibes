from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.urls import reverse
from django.contrib import messages


class MyAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        """
        Controla para onde o usuário vai DEPOIS de se CADASTRAR.
        """
        redirect_url = request.POST.get("next")
        if redirect_url:
            return redirect_url
        return reverse('account_complete_profile')

    # --- ESTE É O NOVO MÉTODO PARA O LOGIN ---
    def get_login_redirect_url(self, request):
        """
        Controla para onde o usuário vai DEPOIS de fazer LOGIN.
        """
        # 1. Verifica se o cadastro do usuário está completo
        if not request.user.cadastro_completo:
            # Se não estiver, FORÇA o redirecionamento para a página
            # de completar o perfil.
            return reverse('account_complete_profile')

        # 2. Se o cadastro ESTIVER completo, procure por um ?next=
        # (ex: se ele tentou acessar uma página protegida antes do login)
        redirect_url = request.POST.get("next") or request.GET.get("next")
        if redirect_url:
            return redirect_url

        # 3. Se estiver completo e não houver ?next=, use o padrão
        # (que definimos no settings.py como 'home')
        return reverse(settings.LOGIN_REDIRECT_URL)
    def add_message(self, request, level, message_template, message_context=None,
                    extra_tags=""):
        """
        Intercepta e bloqueia mensagens específicas do allauth.
        """
        blocked_messages = [
            "account/messages/logged_in.txt",
            "account/messages/logged_out.txt",
        ]
        if message_template in blocked_messages:
            return
        return super().add_message(
            request, level, message_template, message_context, extra_tags
        )
