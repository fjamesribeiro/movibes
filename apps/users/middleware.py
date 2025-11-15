from django.shortcuts import redirect
from django.contrib import messages


class ProfileCompletionMiddleware:
    """
    Middleware que garante que usuários autenticados completem
    todas as etapas do cadastro antes de acessar o sistema.

    Fluxo de verificação:
    1. Usuário tem perfil escolhido? Se não → escolher_perfil
    2. Usuário tem cadastro completo? Se não → complete_profile
    3. Profissional tem assinatura? Se não → escolher_plano_obrigatorio
    4. Tudo OK → pode acessar o sistema normalmente
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # URLs que não devem ser interceptadas pelo middleware
        self.exempt_urls = [
            '/accounts/',  # Todas as URLs do allauth
            '/admin/',
            '/static/',
            '/media/',
        ]

        # Nomes de URLs que não devem ser bloqueadas
        self.exempt_url_names = [
            'account_select_profile_type',
            'account_set_profile_type',
            'account_complete_profile',
            'account_complete_profile_profissional',
            'escolher_plano',
            'escolher_plano_obrigatorio',
            'account_logout',
        ]

    def __call__(self, request):
        # Se o usuário não está autenticado, deixa passar
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Se é staff/superuser, deixa passar (para não bloquear admin)
        if request.user.is_staff or request.user.is_superuser:
            return self.get_response(request)

        # Verifica se a URL atual está na lista de exceções
        path = request.path
        if any(path.startswith(exempt_url) for exempt_url in self.exempt_urls):
            return self.get_response(request)

        # Verifica se o nome da URL está na lista de exceções
        if request.resolver_match and request.resolver_match.url_name in self.exempt_url_names:
            return self.get_response(request)

        # ===== VERIFICAÇÃO 1: Perfil escolhido? =====
        if not request.user.perfil_escolhido:
            # Usuário ainda não escolheu se é Aluno ou Profissional
            messages.info(
                request,
                'Para começar a usar a plataforma, escolha seu tipo de perfil.'
            )
            return redirect('account_select_profile_type')

        # ===== VERIFICAÇÃO 2: Cadastro completo? =====
        if not request.user.cadastro_completo:
            # Redireciona para a página de completar cadastro apropriada
            if hasattr(request.user, 'aluno'):
                messages.info(
                    request,
                    'Complete seu perfil de aluno para continuar.'
                )
                return redirect('account_complete_profile')

            elif hasattr(request.user, 'profissional'):
                messages.info(
                    request,
                    'Complete seu perfil profissional para continuar.'
                )
                return redirect('account_complete_profile_profissional')

        # ===== VERIFICAÇÃO 3: Profissional com assinatura? =====
        if hasattr(request.user, 'profissional'):
            if not request.user.tem_assinatura_ativa():
                messages.warning(
                    request,
                    'Profissionais precisam ter uma assinatura ativa. Escolha seu plano!'
                )
                return redirect('escolher_plano_obrigatorio')

        # Se passou por todas as verificações, deixa acessar normalmente
        return self.get_response(request)
