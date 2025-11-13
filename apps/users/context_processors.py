from apps.users.models import SolicitacaoConexao
from apps.events.models import InteracaoPresenca  # Importação do novo modelo


def notificacoes_context(request):
    """
    Disponibiliza a contagem TOTAL de notificações pendentes em todos os templates.
    Soma:
    1. Pedidos de conexão recebidos (pendentes).
    2. Pedidos de conexão aceitos (que eu enviei e não vi).
    3. Curtidas de presença recebidas (que não vi).
    4. Likes de volta recebidos (que não vi).
    """
    if request.user.is_authenticated:
        # --- LÓGICA DE CONEXÕES (WhatsApp) ---

        # 1. Pedidos de conexão que EU RECEBI e estão pendentes
        conexoes_pendentes = SolicitacaoConexao.objects.filter(
            solicitado=request.user,
            status='pendente'
        ).count()

        # 2. Pedidos que EU ENVIEI, foram aceitos, e eu NÃO VI AINDA
        conexoes_aceitas_nao_lidas = SolicitacaoConexao.objects.filter(
            solicitante=request.user,
            status='aceita',
            lida_pelo_solicitante=False
        ).count()

        # --- LÓGICA DE CURTIDAS (Presença em Eventos) ---

        # 3. Curtidas que RECEBI na minha presença (alguém me curtiu)
        # Buscamos interações onde a inscrição alvo pertence ao usuário logado
        curtidas_recebidas_nao_lidas = InteracaoPresenca.objects.filter(
            inscricao_alvo__id_aluno__usuario=request.user,
            lida_pelo_alvo=False
        ).count()

        # 4. "Likes de volta" que RECEBI (eu curti alguém, e a pessoa aceitou/retribuiu)
        # Buscamos interações onde EU sou o autor e o status agora é 'aceito'
        likes_back_nao_lidos = InteracaoPresenca.objects.filter(
            autor=request.user,
            status_retorno='aceito',
            lida_pelo_autor=False
        ).count()

        # --- SOMA TOTAL ---
        total_notificacoes = (
            conexoes_pendentes +
            conexoes_aceitas_nao_lidas +
            curtidas_recebidas_nao_lidas +
            likes_back_nao_lidos
        )

        return {'contagem_notificacoes': total_notificacoes}

    return {}
