from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.urls import reverse


class MyAccountAdapter(DefaultAccountAdapter):
    """
    Adapter customizado para controlar o comportamento do signup tradicional.
    """

    def get_signup_redirect_url(self, request):
        """
        Controla para onde o usuário vai DEPOIS de se CADASTRAR.
        """
        redirect_url = request.POST.get("next")
        if redirect_url:
            return redirect_url
        return reverse('account_complete_profile')

    def get_login_redirect_url(self, request):
        """
        Controla para onde o usuário vai DEPOIS de fazer LOGIN.
        O middleware ProfileCompletionMiddleware vai fazer as verificações
        necessárias e redirecionar conforme apropriado.
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

    def save_user(self, request, user, form, commit=True):
        """
        Customiza o salvamento do usuário no signup tradicional.
        Adiciona os novos campos para controle de OAuth2.
        """
        user = super().save_user(request, user, form, commit=False)

        # Marca o método de registro
        user.metodo_registro = 'email'

        # Por padrão, perfil não foi escolhido ainda
        user.perfil_escolhido = False
        user.cadastro_completo = False

        if commit:
            user.save()

        return user


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter customizado para controlar o comportamento do signup via OAuth2.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Chamado antes do login social ser processado.
        Aqui vinculamos contas existentes com o mesmo email.
        """
        # Se o usuário já está autenticado, não faz nada
        if request.user.is_authenticated:
            return

        # Tenta encontrar um usuário existente com o mesmo email
        try:
            email = sociallogin.account.extra_data.get('email', '').lower()
            if email:
                # Busca usuário existente com este email
                from apps.users.models import Usuario
                user = Usuario.objects.get(email=email)

                # Vincula a conta social ao usuário existente
                sociallogin.connect(request, user)

        except Usuario.DoesNotExist:
            pass  # Nenhuma conta existente, vai criar uma nova
        except Exception as e:
            # Log do erro mas não quebra o fluxo
            print(f"Erro ao vincular conta social: {e}")

    def save_user(self, request, sociallogin, form=None):
        """
        Customiza o salvamento do usuário no signup via OAuth2.
        """
        user = super().save_user(request, sociallogin, form)

        # Marca o método de registro
        user.metodo_registro = 'google'

        # Usuário OAuth2 ainda não escolheu o perfil
        user.perfil_escolhido = False
        user.cadastro_completo = False

        # Tenta pegar nome do Google
        extra_data = sociallogin.account.extra_data
        if not user.first_name and 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        if not user.last_name and 'family_name' in extra_data:
            user.last_name = extra_data['family_name']

        user.save()

        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Após vincular uma conta social a uma conta existente.
        """
        return reverse('profile')
