from .models import SolicitacaoConexao


def notificacoes_context(request):
    """
    Disponibiliza a contagem de notificações pendentes em todos os templates.
    """
    if request.user.is_authenticated:
        # 1. Pedidos que EU RECEBI e estão pendentes
        count_pendentes = SolicitacaoConexao.objects.filter(
            solicitado=request.user,
            status='pendente'
        ).count()

        # 2. Pedidos que EU ENVIEI, foram aceitos, e eu NÃO VI AINDA
        count_aceitos = SolicitacaoConexao.objects.filter(
            solicitante=request.user,
            status='aceita',
            lida_pelo_solicitante=False  # <-- A nova lógica!
        ).count()

        return {'contagem_notificacoes': count_pendentes + count_aceitos}

    return {}
