"""
Middleware de Completude de Cadastro - VERSÃO CORRIGIDA
========================================================

CORREÇÃO: Permite que profissionais acessem as páginas de escolher/comprar
plano mesmo sem ter assinatura ativa ainda.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class ProfileCompletionMiddleware:
    """
    Middleware que garante que usuários autenticados completem o cadastro.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # URLs que não devem ser interceptadas
        self.exempt_urls = [
            '/accounts/',  # Todas as URLs do allauth
            '/admin/',
            '/static/',
            '/media/',
        ]

        # URLs específicas que precisam ser acessíveis
        try:
            self.exempt_urls.extend([
                reverse('account_complete_profile'),
                reverse('account_complete_profile_profissional'),
                reverse('escolher_plano'),
                reverse('escolher_plano_obrigatorio'),
                reverse('account_logout'),
            ])
        except:
            pass

    def __call__(self, request):
        # Se não está autenticado, deixa passar
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Se é staff/superuser, deixa passar
        if request.user.is_staff or request.user.is_superuser:
            return self.get_response(request)

        # Pega o caminho atual
        path = request.path

        # Verifica se está nas URLs de exceção
        if any(path.startswith(exempt_url) for exempt_url in self.exempt_urls):
            return self.get_response(request)

        # ===== VERIFICAÇÃO 1: Cadastro completo? =====

        if not request.user.cadastro_completo:
            # Redireciona para a página de completar cadastro apropriada
            if hasattr(request.user, 'aluno'):
                if path != reverse('account_complete_profile'):
                    messages.info(
                        request,
                        'Complete seu perfil de aluno para começar a usar a plataforma.'
                    )
                    return redirect('account_complete_profile')

            elif hasattr(request.user, 'profissional'):
                if path != reverse('account_complete_profile_profissional'):
                    messages.info(
                        request,
                        'Complete seu perfil profissional para começar a divulgar seus serviços.'
                    )
                    return redirect('account_complete_profile_profissional')

        # ===== VERIFICAÇÃO 2: Profissional com assinatura? =====

        if hasattr(request.user, 'profissional'):
            if not request.user.tem_assinatura_ativa():
                # URLs relacionadas a planos que devem ser PERMITIDAS
                plano_related_paths = [
                    '/assinatura/escolher-plano',
                    '/assinatura/checkout',
                    '/assinatura/processar',
                    '/premium/',
                ]

                # Verifica se está em alguma página relacionada a planos
                is_plano_page = any(path.startswith(plano_path) for plano_path in plano_related_paths)

                # Se NÃO está em página de plano, redireciona
                if not is_plano_page:
                    try:
                        escolher_plano_path = reverse('escolher_plano_obrigatorio')
                        if path != escolher_plano_path:
                            messages.warning(
                                request,
                                'Profissionais precisam ter uma assinatura ativa. '
                                'Escolha seu plano para começar a usar a plataforma!'
                            )
                            return redirect('escolher_plano_obrigatorio')
                    except:
                        # Se a URL não existir, apenas deixa passar
                        pass

        # Tudo OK - pode acessar
        return self.get_response(request)
