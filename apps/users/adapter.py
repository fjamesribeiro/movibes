from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from django.urls import reverse


class MyAccountAdapter(DefaultAccountAdapter):
    """
    Adapter customizado para redirecionar usuários após login e signup
    dependendo do estado do cadastro.
    """

    def get_login_redirect_url(self, request):
        """
        Controla para onde o usuário vai DEPOIS de fazer LOGIN.
        Este é o método que estava faltando!
        """
        user = request.user

        # 1. Se o cadastro já está completo, vai para home
        if user.cadastro_completo:
            return resolve_url('home')

        # 2. Se não está completo, verifica qual tipo de perfil
        # Verifica se é aluno
        if hasattr(user, 'aluno'):
            return reverse('account_complete_profile')

        # Verifica se é profissional
        elif hasattr(user, 'profissional'):
            return reverse('account_complete_profile_profissional')

        # 3. Se não tem nenhum perfil ainda, manda escolher
        else:
            return reverse('account_select_profile_type')

    def get_signup_redirect_url(self, request):
        """
        Controla para onde o usuário vai DEPOIS de se CADASTRAR.
        Sempre vai para escolher o tipo de perfil.
        """
        # Pega o valor de ?next= da URL (se existir)
        redirect_url = (
            request.GET.get("next")
            or request.POST.get("next")
        )

        # Se o ?next= existir, usa ele
        if redirect_url:
            return redirect_url

        # Senão, manda para escolher o tipo de perfil
        return reverse('account_select_profile_type')
