from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class MyAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        """
        Controla para onde o usuário vai DEPOIS de se cadastrar.
        Ele vai procurar por um parâmetro 'next' na URL.
        """

        # Pega o valor de ?next= da URL (que pode estar no GET ou no POST)
        redirect_url = (
            request.GET.get("next")
            or request.POST.get("next")
        )

        # Se o ?next= existir (ex: /accounts/complete-profile-profissional/)
        if redirect_url:
            return redirect_url

        # Se, por algum motivo, o ?next= não for passado, mande para a
        # página de Aluno como um fallback seguro.
        return reverse('account_complete_profile')
