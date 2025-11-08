from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class MyAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Esta função é chamada pelo allauth logo após o usuário
        ser criado e salvo na tabela 'Usuario' (User).
        """
        user = super().save_user(request, user, form, commit)
        user.cadastro_completo = False
        if commit:
            user.save()
        return user

    def get_login_redirect_url(self, request):
        """
        Define para onde o usuário vai após o login.
        """
        user = request.user
        if not user.cadastro_completo:
            return reverse('account_select_profile_type')

        return reverse('home')

    def get_signup_redirect_url(self, request):
        """
        Chamado após o CADASTRO (signup) ser bem-sucedido.
        """
        user = request.user
        if not user.cadastro_completo:
            return reverse('account_select_profile_type')
        return reverse('home')