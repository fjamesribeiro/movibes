from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def assinatura_ativa_requerida(view_func):
    """
    Decorator que verifica se o usuário profissional tem assinatura ativa.
    Se não tiver, redireciona para página de renovação.

    Use em todas as views que profissionais precisam ter assinatura para acessar.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verifica se é profissional
        if hasattr(request.user, 'profissional'):
            # Profissionais DEVEM ter assinatura ativa
            if not request.user.tem_assinatura_ativa():
                messages.error(
                    request,
                    'Sua assinatura expirou. Renove agora para continuar usando a plataforma.'
                )
                return redirect('escolher_plano')

        # Se não for profissional ou tiver assinatura ativa, continua normalmente
        return view_func(request, *args, **kwargs)

    return wrapper
