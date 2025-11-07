from allauth.account.adapter import DefaultAccountAdapter
from .models import Perfil, Aluno
from django.urls import reverse


class MyAccountAdapter(DefaultAccountAdapter):


    def save_user(self, request, user, form, commit=True):
        """
        Esta função é chamada pelo allauth logo após o usuário
        ser criado e salvo na tabela 'Usuario' (User).
        """
        user = super().save_user(request, user, form, commit)
        if commit:
            user.save()
        try:
            perfil_aluno, _ = Perfil.objects.get_or_create(nome='aluno')
            user.perfis.add(perfil_aluno)
            Aluno.objects.get_or_create(usuario=user)
        except Exception as e:
            print(f"Erro ao atribuir perfil de aluno para {user.email}: {e}")
        return user


    def get_login_redirect_url(self, request):
        user = request.user
        if not user.cadastro_completo:
            return reverse('account_complete_profile')
        return reverse('home')



    def get_signup_redirect_url(self, request):
        """
        Chamado após o CADASTRO (signup) ser bem-sucedido.
        """
        user = request.user
        if not user.cadastro_completo:
            return reverse('account_complete_profile')
        return reverse('home')