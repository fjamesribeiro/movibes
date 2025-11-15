"""
Adapters do Django-Allauth - VERSÃO FINAL CORRIGIDA
====================================================

PROBLEMA IDENTIFICADO:
Quando o formulário de signup é submetido (POST), o ?next= que estava
no GET se perde. Precisamos pegar o next de onde o allauth o armazena.

SOLUÇÃO:
O allauth armazena o 'next' em request.POST quando vem do formulário!
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse


class MyAccountAdapter(DefaultAccountAdapter):
    """
    Adapter para signup tradicional (email/senha).
    """

    def get_signup_redirect_url(self, request):
        """
        Define para onde vai após signup tradicional.

        O allauth preserva o 'next' automaticamente e passa para esta função.
        Precisamos apenas retorná-lo se existir.
        """
        # Tenta pegar de vários lugares onde pode estar
        next_url = None

        # 1. Tenta do POST (quando vem do formulário)
        if hasattr(request, 'POST'):
            next_url = request.POST.get('next', '')

        # 2. Se não achou, tenta do GET
        if not next_url and hasattr(request, 'GET'):
            next_url = request.GET.get('next', '')

        # 3. Tenta da sessão
        if not next_url and hasattr(request, 'session'):
            next_url = request.session.get('account_next_url', '')

        print(f"[DEBUG] get_signup_redirect_url")
        print(f"  - POST.next: {request.POST.get('next', 'N/A') if hasattr(request, 'POST') else 'N/A'}")
        print(f"  - GET.next: {request.GET.get('next', 'N/A') if hasattr(request, 'GET') else 'N/A'}")
        print(f"  - next_url escolhido: {next_url}")

        # Se tem next válido, usa ele
        if next_url and next_url.startswith('/'):
            print(f"  ✓ Redirecionando para: {next_url}")
            return next_url

        # Fallback: detecta pelo perfil criado
        user = request.user
        if hasattr(user, 'aluno'):
            print(f"  ✓ Fallback: redirecionando ALUNO para complete_profile")
            return reverse('account_complete_profile')
        elif hasattr(user, 'profissional'):
            print(f"  ✓ Fallback: redirecionando PROFISSIONAL para complete_profissional")
            return reverse('account_complete_profile_profissional')

        # Último fallback
        print(f"  ! Último fallback: redirecionando para home")
        return '/'

    def save_user(self, request, user, form, commit=True):
        """
        Salva o usuário durante signup tradicional.

        IMPORTANTE: Aqui precisamos pegar o 'next' de onde quer que ele esteja
        e criar o perfil apropriado.
        """
        # Salvamento padrão
        user = super().save_user(request, user, form, commit=False)

        user.metodo_registro = 'email'
        user.cadastro_completo = False

        # Tenta pegar o 'next' de vários lugares
        next_url = ''

        if hasattr(request, 'POST') and 'next' in request.POST:
            next_url = request.POST.get('next', '')
            print(f"[DEBUG] save_user - next veio do POST: {next_url}")
        elif hasattr(request, 'GET') and 'next' in request.GET:
            next_url = request.GET.get('next', '')
            print(f"[DEBUG] save_user - next veio do GET: {next_url}")

        # Se não achou ainda, tenta pegar do campo hidden do formulário
        if not next_url and hasattr(form, 'data'):
            next_url = form.data.get('next', '')
            print(f"[DEBUG] save_user - next veio do form.data: {next_url}")

        print(f"[DEBUG] save_user - next_url final: '{next_url}'")

        # Importa os modelos
        from apps.users.models import Perfil, Aluno, Profissional

        perfil_criado = False

        # Detecta qual perfil criar baseado no next_url
        if 'profissional' in next_url.lower():
            print(f"[INFO] Detectado PROFISSIONAL")
            user.perfil_escolhido = True

            if commit:
                user.save()
                perfil, _ = Perfil.objects.get_or_create(nome='profissional')
                user.perfis.add(perfil)
                Profissional.objects.get_or_create(usuario=user)
                perfil_criado = True
                print(f"[INFO] ✓ Perfil PROFISSIONAL criado para {user.email}")

        elif 'complete-profile' in next_url or 'aluno' in next_url.lower():
            print(f"[INFO] Detectado ALUNO")
            user.perfil_escolhido = True

            if commit:
                user.save()
                perfil, _ = Perfil.objects.get_or_create(nome='aluno')
                user.perfis.add(perfil)
                Aluno.objects.get_or_create(usuario=user)
                perfil_criado = True
                print(f"[INFO] ✓ Perfil ALUNO criado para {user.email}")

        if not perfil_criado:
            print(f"[WARNING] Não detectou perfil - next_url: '{next_url}'")
            user.perfil_escolhido = False
            if commit:
                user.save()

        return user


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter para signup via OAuth2 (Google).
    """

    def pre_social_login(self, request, sociallogin):
        """
        Vincula contas sociais a usuários existentes.
        """
        if request.user.is_authenticated:
            return

        try:
            email = sociallogin.account.extra_data.get('email', '').lower()
            if email:
                from apps.users.models import Usuario
                try:
                    user = Usuario.objects.get(email=email)
                    sociallogin.connect(request, user)
                    print(f"[INFO] OAuth2: Conta vinculada ao usuário existente: {email}")
                except Usuario.DoesNotExist:
                    pass
        except Exception as e:
            print(f"[ERROR] Erro em pre_social_login: {e}")

    def get_signup_redirect_url(self, request):
        """
        Define para onde vai após signup via Google.
        """
        # Para OAuth2, tenta da sessão
        next_url = request.session.get('socialaccount_next_url', '')

        print(f"[DEBUG] get_signup_redirect_url (OAuth2)")
        print(f"  - next da sessão: {next_url}")

        if next_url and next_url.startswith('/'):
            print(f"  ✓ Redirecionando OAuth2 para: {next_url}")
            return next_url

        # Fallback: detecta pelo perfil
        user = request.user
        if hasattr(user, 'aluno'):
            return reverse('account_complete_profile')
        elif hasattr(user, 'profissional'):
            return reverse('account_complete_profile_profissional')

        return '/'

    def save_user(self, request, sociallogin, form=None):
        """
        Salva usuário durante signup via Google.
        """
        user = super().save_user(request, sociallogin, form)

        user.metodo_registro = sociallogin.account.provider
        user.cadastro_completo = False

        # Pega dados do Google
        extra_data = sociallogin.account.extra_data
        if not user.first_name and 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        if not user.last_name and 'family_name' in extra_data:
            user.last_name = extra_data['family_name']

        # Para OAuth2, o next está na sessão
        next_url = request.session.get('socialaccount_next_url', '')

        print(f"[DEBUG] save_user (OAuth2) - next da sessão: '{next_url}'")

        from apps.users.models import Perfil, Aluno, Profissional

        perfil_criado = False

        if 'profissional' in next_url.lower():
            print(f"[INFO] OAuth2: Detectado PROFISSIONAL")
            user.perfil_escolhido = True
            user.save()

            perfil, _ = Perfil.objects.get_or_create(nome='profissional')
            user.perfis.add(perfil)
            Profissional.objects.get_or_create(usuario=user)
            perfil_criado = True
            print(f"[INFO] ✓ OAuth2: Perfil PROFISSIONAL criado para {user.email}")

        elif 'complete-profile' in next_url or 'aluno' in next_url.lower():
            print(f"[INFO] OAuth2: Detectado ALUNO")
            user.perfil_escolhido = True
            user.save()

            perfil, _ = Perfil.objects.get_or_create(nome='aluno')
            user.perfis.add(perfil)
            Aluno.objects.get_or_create(usuario=user)
            perfil_criado = True
            print(f"[INFO] ✓ OAuth2: Perfil ALUNO criado para {user.email}")

        if not perfil_criado:
            print(f"[WARNING] OAuth2: Não detectou perfil - next: '{next_url}'")
            user.perfil_escolhido = False
            user.save()

        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Após vincular conta social existente.
        """
        return reverse('profile')
