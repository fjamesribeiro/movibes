from django.contrib.auth.models import User
from .forms import AlunoProfileForm, ProfissionalProfileForm, UsuarioProfileForm, \
    FotoUsuarioForm, AvaliacaoForm
from .models import Aluno, Profissional, Perfil, Usuario, Avaliacao, SolicitacaoConexao, \
    TipoConta
from django.db import models
from django.db.models import Q
from apps.events.models import InteracaoPresenca
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import AssinaturaPremium, TipoPlano


# Em apps/users/views.py

@login_required
def complete_profissional_profile(request):
    """
    Completa o perfil do profissional.
    Após salvar, OBRIGATORIAMENTE redireciona para escolha de plano Pro.
    """
    usuario = request.user

    # Verifica se já tem perfil profissional
    try:
        profissional = usuario.profissional
    except Profissional.DoesNotExist:
        # Se não existe, cria um novo
        profissional = Profissional(usuario=usuario)

    if request.method == 'POST':
        user_form = UsuarioProfileForm(request.POST, request.FILES, instance=usuario)
        profile_form = ProfissionalProfileForm(request.POST, instance=profissional)

        if user_form.is_valid() and profile_form.is_valid():
            # Salva o usuário
            user_form.save()

            # Salva o profissional
            prof = profile_form.save(commit=False)
            prof.usuario = usuario
            prof.save()

            # MUDANÇA IMPORTANTE: Verifica se já tem assinatura
            if usuario.tem_assinatura_ativa():
                # Se já tem assinatura (caso de renovação ou reativação), vai direto pro perfil
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('profile')
            else:
                # Se NÃO tem assinatura, DEVE escolher um plano antes de continuar
                messages.info(
                    request,
                    'Perfil salvo! Agora escolha seu plano Pro para ativar sua conta profissional.'
                )
                return redirect('escolher_plano_obrigatorio')
    else:
        user_form = UsuarioProfileForm(instance=usuario)
        profile_form = ProfissionalProfileForm(instance=profissional)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'account/complete_profile_profissional.html', context)


@login_required
def complete_aluno_profile(request):
    """
    Completa o perfil do aluno.
    Se o aluno escolheu tipo de conta Premium, redireciona para escolha de plano.
    Se escolheu Free, vai direto para a home.
    """
    usuario = request.user

    try:
        aluno = usuario.aluno
    except Aluno.DoesNotExist:
        aluno = Aluno(usuario=usuario)

    if request.method == 'POST':
        user_form = UsuarioProfileForm(request.POST, request.FILES, instance=usuario)
        profile_form = AlunoProfileForm(request.POST, instance=aluno)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            # Salva o aluno mas ainda não marca o cadastro como completo
            alu = profile_form.save(commit=False)
            alu.usuario = usuario
            alu.save()

            # Precisamos salvar as relações ManyToMany
            profile_form.save_m2m()

            # MUDANÇA PRINCIPAL: Verifica qual tipo de conta foi escolhido
            tipo_conta_escolhido = alu.tipo_conta

            # Verifica se o tipo de conta escolhido é Premium
            # (assumindo que existe um TipoConta com nome "Premium")
            try:
                tipo_premium = TipoConta.objects.get(nome='Premium')
                eh_premium = (tipo_conta_escolhido == tipo_premium)
            except TipoConta.DoesNotExist:
                # Se não existe tipo Premium no banco, trata como Free
                eh_premium = False

            # Marca o cadastro como completo
            usuario.cadastro_completo = True
            usuario.save()

            if eh_premium:
                # Se escolheu Premium, DEVE escolher um plano antes de continuar
                messages.info(
                    request,
                    'Perfil salvo! Agora escolha seu plano Premium para ativar todos os recursos exclusivos.'
                )
                return redirect('escolher_plano')
            else:
                # Se escolheu Free, pode ir direto para a home
                messages.success(
                    request,
                    'Perfil criado com sucesso! Bem-vindo à plataforma.'
                )
                return redirect('home')
    else:
        user_form = UsuarioProfileForm(instance=usuario)
        profile_form = AlunoProfileForm(instance=aluno)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'account/complete_profile.html', context)


@login_required
def profile_view(request):
    """
    Página "Meu Perfil" para ver e editar os dados do
    Usuário e do perfil (Aluno ou Profissional).
    """
    user: User = request.user
    profile_form = None
    profile_form_class = None
    profile_instance = None
    profile_type = None  # Vamos usar isso no template

    # 1. Tenta identificar o tipo de perfil do usuário
    if hasattr(user, 'aluno'):
        profile_instance = user.aluno
        profile_form_class = AlunoProfileForm
        profile_type = 'aluno'
    elif hasattr(user, 'profissional'):
        profile_instance = user.profissional
        profile_form_class = ProfissionalProfileForm
        profile_type = 'profissional'

    # 2. Processa o formulário se for um POST (salvando)
    if request.method == 'POST':
        user_form = UsuarioProfileForm(request.POST, request.FILES, instance=user)

        # Instancia o formulário de perfil (Aluno ou Profissional) se ele existir
        if profile_form_class:
            profile_form = profile_form_class(request.POST, instance=profile_instance)

        # Verifica se ambos os formulários são válidos
        if user_form.is_valid() and (not profile_form or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()

            # 3. Adiciona uma mensagem de sucesso
            messages.success(request, 'Perfil atualizado com sucesso!')

            # Redireciona de volta para a mesma página
            return redirect('profile')
        else:
            # Se houver erros, eles aparecerão no formulário
            messages.error(request, 'Houve um erro ao atualizar seu perfil. Verifique os campos.')

    # 3. Se for um GET (apenas vendo a página)
    else:
        user_form = UsuarioProfileForm(instance=user)
        if profile_form_class:
            profile_form = profile_form_class(instance=profile_instance)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile_type': profile_type  # 'aluno', 'profissional' ou None
    }

    return render(request, 'account/profile.html', context)


@login_required
def gerenciar_galeria(request):
    if request.method == 'POST':
        form = FotoUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            foto = form.save(commit=False)
            foto.usuario = request.user
            foto.save()
            messages.success(request, 'Foto adicionada com sucesso!')

            # --- CORRIGIDO AQUI ---
            return redirect('account_galeria')
    else:
        form = FotoUsuarioForm()

    # Pega todas as fotos do usuário para listar na galeria
    fotos_do_usuario = request.user.galeria.all()

    return render(request, 'account/galeria.html', {
        'form': form,
        'fotos': fotos_do_usuario
    })


def public_profile_view(request, usuario_id):
    """
    Mostra a página de perfil público (somente leitura)
    de qualquer usuário (Aluno ou Profissional).
    """
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    profile_type = None
    fotos_galeria = None

    # --- NOVAS VARIÁVEIS ---
    lista_avaliacoes = None
    avaliacao_form = None
    can_review = False
    avg_nota = 0
    total_avaliacoes = 0

    # --- CORREÇÃO 1: INICIALIZAR 'profissional' COMO None ---
    # Isso corrige o 'UnboundLocalError' em perfis de Aluno
    profissional = None

    if hasattr(usuario, 'aluno'):
        profile_type = 'aluno'
        fotos_galeria = usuario.galeria.all()

    elif hasattr(usuario, 'profissional'):
        profile_type = 'profissional'
        profissional = usuario.profissional  # 'profissional' é definido AQUI

        # Busca todas as avaliações
        lista_avaliacoes = profissional.avaliacoes.all().order_by('-created_at')
        total_avaliacoes = lista_avaliacoes.count()

        # Calcula a média de notas
        if total_avaliacoes > 0:
            avg_nota = lista_avaliacoes.aggregate(models.Avg('nota'))['nota__avg']

        # Lógica para mostrar o formulário de avaliação:
        if request.user.is_authenticated and hasattr(request.user, 'aluno'):
            # CORREÇÃO 2: Comparar PKs, não objetos
            if request.user.pk != profissional.pk:  # Não pode avaliar a si mesmo
                if not Avaliacao.objects.filter(
                    autor=request.user.aluno,
                    profissional_avaliado=profissional
                ).exists():
                    can_review = True
                    avaliacao_form = AvaliacaoForm()  # Prepara um formulário em branco

    context = {
        'perfil_usuario': usuario,
        'profile_type': profile_type,
        'fotos_galeria': fotos_galeria,
        'lista_avaliacoes': lista_avaliacoes,
        'avaliacao_form': avaliacao_form,
        'can_review': can_review,
        'total_avaliacoes': total_avaliacoes,
        'avg_nota': avg_nota,
        'profissional': profissional,
    }

    return render(request, 'account/public_profile.html', context)


@login_required
def adicionar_avaliacao_view(request, profissional_id):
    """
    View dedicada a RECEBER O POST do formulário de avaliação.
    """
    # Garante que o usuário logado é um Aluno
    if not hasattr(request.user, 'aluno'):
        messages.error(request, 'Apenas alunos podem deixar avaliações.')
        return redirect('home')  # Redireciona se não for aluno

    profissional = get_object_or_404(Profissional, pk=profissional_id)
    autor_aluno = request.user.aluno

    # Redireciona de volta para a página de perfil (para onde o formulário foi enviado)
    redirect_url = redirect('public_profile', usuario_id=profissional.usuario.id)

    # Verifica se o aluno já avaliou este profissional
    if Avaliacao.objects.filter(autor=autor_aluno,
                                profissional_avaliado=profissional).exists():
        messages.error(request, 'Você já avaliou este profissional.')
        return redirect_url

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.autor = autor_aluno
            avaliacao.profissional_avaliado = profissional
            avaliacao.save()
            messages.success(request, 'Sua avaliação foi enviada com sucesso!')
            return redirect_url
        else:
            # Se o formulário for inválido, é difícil mostrar o erro,
            # então apenas redirecionamos com uma mensagem genérica.
            messages.error(request, 'Erro ao enviar sua avaliação. Verifique os dados.')
            return redirect_url

    # Se alguém tentar acessar esta URL via GET, apenas redireciona
    return redirect_url


@login_required
def solicitar_conexao_view(request, usuario_id):
    """
    Cria uma nova SolicitacaoConexao (um pedido de WhatsApp).
    Esta view é chamada via POST (HTMX).
    """
    if request.method == 'POST':
        solicitado = get_object_or_404(Usuario, pk=usuario_id)
        solicitante = request.user

        # Regras de Negócio
        if solicitado == solicitante:
            messages.error(request, 'Você não pode solicitar seu próprio WhatsApp.')
        elif not hasattr(solicitado, 'aluno'):
            messages.error(request, 'Você só pode solicitar conexões de Alunos.')
        elif SolicitacaoConexao.objects.filter(solicitante=solicitante,
                                               solicitado=solicitado).exists():
            messages.warning(request,
                             'Você já enviou uma solicitação para este usuário.')
        else:
            SolicitacaoConexao.objects.create(solicitante=solicitante,
                                              solicitado=solicitado, status='pendente')
            messages.success(request, 'Solicitação de conexão enviada!')

    # Redireciona de volta para o perfil que o usuário estava vendo
    return redirect('public_profile', usuario_id=usuario_id)


@login_required
def listar_notificacoes_view(request):
    """
    Mostra a página do "sininho" e marca as novas
    notificações como lidas (Conexões e Curtidas),
    mas exibe o histórico permanente de todas elas.
    """
    usuario = request.user

    # === PARTE A: CONEXÕES (WhatsApp) ===

    # 1. Pedidos que EU RECEBI e preciso responder
    pedidos_pendentes = SolicitacaoConexao.objects.filter(
        solicitado=usuario,
        status='pendente'
    ).select_related('solicitante')

    # 2. Histórico de Pedidos que EU FIZ e foram aceitos
    pedidos_aceitos_para_mim = SolicitacaoConexao.objects.filter(
        solicitante=usuario,
        status='aceita'
    ).select_related('solicitado').order_by('-updated_at')

    # 2.1. Descobre quais são NOVOS e marca como lidos
    ids_novos_aceitos = list(
        pedidos_aceitos_para_mim.filter(lida_pelo_solicitante=False).values_list('id',
                                                                                 flat=True)
    )
    if ids_novos_aceitos:
        SolicitacaoConexao.objects.filter(pk__in=ids_novos_aceitos).update(
            lida_pelo_solicitante=True)

    # 3. Histórico de conexões (outros status)
    historico_conexoes = SolicitacaoConexao.objects.filter(
        Q(solicitado=usuario) & ~Q(status='pendente') |
        Q(solicitante=usuario) & ~Q(status='pendente')
    ).select_related('solicitante', 'solicitado').order_by('-updated_at')

    # === PARTE B: INTERAÇÕES DE PRESENÇA (Lógica Corrigida) ===

    # 4. Histórico de Curtidas que RECEBI
    curtidas_recebidas_historico = InteracaoPresenca.objects.filter(
        inscricao_alvo__id_aluno__usuario=usuario
    ).select_related('autor', 'inscricao_alvo__id_evento').order_by('-updated_at')

    # 4.1. Descobre quais são NOVAS e marca como lidas
    ids_novas_curtidas = list(
        curtidas_recebidas_historico.filter(lida_pelo_alvo=False).values_list('id',
                                                                              flat=True)
    )
    if ids_novas_curtidas:
        InteracaoPresenca.objects.filter(pk__in=ids_novas_curtidas).update(
            lida_pelo_alvo=True)

    # 5. Histórico de "Likes de Volta" que RECEBI
    likes_back_historico = InteracaoPresenca.objects.filter(
        autor=usuario,
        status_retorno='aceito'
    ).select_related('inscricao_alvo__id_aluno__usuario').order_by('-updated_at')

    # 5.1. Descobre quais são NOVOS e marca como lidos
    ids_novos_likes_back = list(
        likes_back_historico.filter(lida_pelo_autor=False).values_list('id', flat=True)
    )
    if ids_novos_likes_back:
        InteracaoPresenca.objects.filter(pk__in=ids_novos_likes_back).update(
            lida_pelo_autor=True)

    context = {
        # Contextos de Conexão
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_aceitos_para_mim': pedidos_aceitos_para_mim,
        'historico': historico_conexoes,  # Renomeado para clareza
        'novos_pedidos_aceitos_ids': ids_novos_aceitos,  # Renomeado para clareza

        # Novos Contextos de Curtida (Histórico + IDs novos)
        'curtidas_recebidas': curtidas_recebidas_historico,
        'novas_curtidas_ids': ids_novas_curtidas,

        'likes_back_recebidos': likes_back_historico,
        'novos_likes_back_ids': ids_novos_likes_back,
    }
    return render(request, 'account/notificacoes.html', context)

@login_required
def responder_solicitacao_view(request, solicitacao_id, acao):
    """
    Aceita ou Recusa uma solicitação pendente.
    Esta view é chamada via POST (HTMX).
    """
    # Garante que o usuário logado é o DONO do pedido
    solicitacao = get_object_or_404(
        SolicitacaoConexao,
        pk=solicitacao_id,
        solicitado=request.user
    )

    if solicitacao.status == 'pendente' and request.method == 'POST':
        if acao == 'aceitar':
            solicitacao.status = 'aceita'
            messages.success(request,
                             f'Você aceitou a conexão de {solicitacao.solicitante.first_name}.')
        elif acao == 'recusar':
            solicitacao.status = 'recusada'
            messages.success(request,
                             f'Você recusou a conexão de {solicitacao.solicitante.first_name}.')
        solicitacao.save()

    return redirect('listar_notificacoes')


@login_required
def processar_like_back_view(request, interacao_id):
    """
    Chamada quando o usuário clica em "Curtir de Volta" na tela de notificações.
    Aceita o 'match' de presença.
    """
    if request.method == 'POST':
        # Busca a interação onde o usuário logado é o ALVO (quem recebeu o like original)
        interacao = get_object_or_404(
            InteracaoPresenca,
            pk=interacao_id,
            inscricao_alvo__id_aluno__usuario=request.user
        )
        # Atualiza o status para aceito
        interacao.status_retorno = 'aceito'
        # Define que o autor original (quem deu o 1º like) ainda NÃO leu essa novidade
        # Isso fará o sininho dele tocar
        interacao.lida_pelo_autor = False
        interacao.save()
        messages.success(request,
                         f"Você curtiu {interacao.autor.first_name} de volta! ⚡")
    return redirect('listar_notificacoes')


@login_required
def process_premium_payment_view(request):
    """
    Processa o pagamento Premium (mockado).
    Atualiza o tipo de conta do aluno para Premium.
    """
    if request.method != 'POST':
        return redirect('mock_premium_checkout')

    # Verifica se o usuário é um aluno
    if not hasattr(request.user, 'aluno'):
        messages.error(request, 'Apenas alunos podem se tornar Premium.')
        return redirect('home')

    aluno = request.user.aluno

    # Verifica se já é Premium
    if aluno.tipo_conta and aluno.tipo_conta.nome.lower() == 'premium':
        messages.info(request, 'Você já é um membro Premium!')
        return redirect('profile')

    try:
        # Busca ou cria o tipo de conta Premium
        tipo_premium, created = TipoConta.objects.get_or_create(
            nome='Premium'
        )

        # Atualiza o aluno para Premium
        aluno.tipo_conta = tipo_premium
        aluno.save()

        # Mensagem de sucesso
        messages.success(
            request,
            '🎉 Parabéns! Você agora é um membro Premium! Aproveite todos os benefícios.'
        )

        # Redireciona para o perfil
        return redirect('profile')

    except Exception as e:
        messages.error(
            request,
            f'Ocorreu um erro ao processar seu upgrade. Tente novamente. ({str(e)})'
        )
        return redirect('mock_premium_checkout')

@login_required
def escolher_plano_view(request):
    """
    Mostra planos disponíveis.
    Alunos: opcional | Profissionais: obrigatório
    """
    # Determina tipo de usuário
    if hasattr(request.user, 'aluno'):
        tipo_usuario = 'aluno'
        titulo = "Torne-se Premium"
        subtitulo = "Desbloqueie recursos exclusivos"
        obrigatorio = False
    elif hasattr(request.user, 'profissional'):
        tipo_usuario = 'profissional'
        titulo = "Escolha seu Plano Profissional"
        subtitulo = "Ative sua conta profissional"
        obrigatorio = True
    else:
        messages.error(request, 'Complete seu perfil primeiro.')
        return redirect('account_set_profile_type')

    # Se já tem assinatura
    if request.user.tem_assinatura_ativa():
        messages.info(request, 'Você já tem assinatura ativa!')
        return redirect('profile')

    # Busca planos
    planos = TipoPlano.objects.filter(
        tipo_usuario=tipo_usuario,
        ativo=True
    ).order_by('ordem', 'periodicidade')

    if not planos.exists():
        messages.error(request, 'Nenhum plano disponível.')
        return redirect('profile')

    context = {
        'planos': planos,
        'tipo_usuario': tipo_usuario,
        'titulo': titulo,
        'subtitulo': subtitulo,
        'obrigatorio': obrigatorio,
    }

    return render(request, 'users/escolher_plano.html', context)


@login_required
def checkout_assinatura_view(request, plano_id):
    """
    Mostra a tela de checkout para um plano específico.
    Similar ao checkout de eventos, mas para assinatura do sistema.
    """
    plano = get_object_or_404(TipoPlano, pk=plano_id, ativo=True)

    # Verifica se o plano é compatível com o tipo de usuário
    if hasattr(request.user, 'aluno') and plano.tipo_usuario != 'aluno':
        messages.error(request, 'Este plano não é compatível com seu tipo de conta.')
        return redirect('escolher_plano')

    if hasattr(request.user, 'profissional') and plano.tipo_usuario != 'profissional':
        messages.error(request, 'Este plano não é compatível com seu tipo de conta.')
        return redirect('escolher_plano')

    # Verifica se já tem assinatura ativa
    if request.user.tem_assinatura_ativa():
        messages.info(request, 'Você já tem uma assinatura ativa!')
        return redirect('escolher_plano')

    # Calcula os valores para exibição
    valor_final = plano.valor_com_desconto()
    economia = plano.economia_mensal()

    context = {
        'plano': plano,
        'valor_final': valor_final,
        'economia': economia,
    }

    return render(request, 'users/checkout_assinatura.html', context)


@login_required
def processar_assinatura_view(request, plano_id):
    """
    Processa o pagamento da assinatura após confirmação do usuário.
    Cria a assinatura e ativa os benefícios correspondentes.
    Só aceita POST.
    """
    if request.method != 'POST':
        return redirect('checkout_assinatura', plano_id=plano_id)

    plano = get_object_or_404(TipoPlano, pk=plano_id, ativo=True)

    # Validações de segurança
    if hasattr(request.user, 'aluno') and plano.tipo_usuario != 'aluno':
        messages.error(request, 'Este plano não é compatível com seu tipo de conta.')
        return redirect('escolher_plano')

    if hasattr(request.user, 'profissional') and plano.tipo_usuario != 'profissional':
        messages.error(request, 'Este plano não é compatível com seu tipo de conta.')
        return redirect('escolher_plano')

    # Verifica se já tem assinatura ativa (última verificação antes de processar)
    if request.user.tem_assinatura_ativa():
        messages.warning(request, 'Você já tem uma assinatura ativa!')
        return redirect('profile')

    # --- PROCESSA O PAGAMENTO MOCKADO ---

    # Pega as opções do formulário
    renovacao_automatica = request.POST.get('renovacao_automatica') == 'on'

    # Cria a assinatura
    assinatura = AssinaturaPremium.objects.create(
        usuario=request.user,
        tipo_plano=plano,
        status='ativa',
        # Em produção real, seria 'pendente' até confirmação de pagamento
        renovacao_automatica=renovacao_automatica,
        id_transacao_externa=f"mock_assinatura_{request.user.id}_{timezone.now().timestamp()}",
        metodo_pagamento='mock',
        observacoes="Assinatura criada via checkout mockado"
    )

    # Atualiza o tipo de conta do usuário se necessário
    if hasattr(request.user, 'aluno') and plano.tipo_usuario == 'aluno':
        try:
            tipo_premium = TipoConta.objects.get(nome='Premium')
            request.user.aluno.tipo_conta = tipo_premium
            request.user.aluno.save()
        except:
            pass

    # Mensagem de sucesso personalizada por tipo de usuário
    if plano.tipo_usuario == 'aluno':
        mensagem_sucesso = (
            f'Parabéns! Sua assinatura Premium {plano.periodicidade} foi ativada com sucesso! '
            f'Você agora tem acesso a todos os recursos exclusivos. '
            f'Válida até {assinatura.data_expiracao.strftime("%d/%m/%Y")}.'
        )
    else:
        mensagem_sucesso = (
            f'Sua assinatura Profissional {plano.periodicidade} foi ativada! '
            f'Você pode continuar usando todas as funcionalidades da plataforma. '
            f'Válida até {assinatura.data_expiracao.strftime("%d/%m/%Y")}.'
        )

    messages.success(request, mensagem_sucesso)
    return redirect('profile')


@login_required
def cancelar_assinatura_view(request):
    """
    Cancela a renovação automática da assinatura.
    A assinatura continua ativa até o fim do período pago.
    """
    if request.method != 'POST':
        return redirect('profile')

    assinatura = request.user.obter_assinatura_ativa()

    if not assinatura:
        messages.error(request, 'Você não tem uma assinatura ativa para cancelar.')
        return redirect('profile')

    # Cancela a assinatura (marca para não renovar)
    assinatura.cancelar()

    # Mensagem diferenciada por tipo
    if assinatura.tipo_plano.tipo_usuario == 'profissional':
        messages.warning(
            request,
            f'Assinatura cancelada. ATENÇÃO: Você perderá o acesso às funcionalidades '
            f'profissionais após {assinatura.data_expiracao.strftime("%d/%m/%Y")}. '
            f'Renove antes desta data para manter sua conta ativa.'
        )
    else:
        messages.success(
            request,
            f'Renovação automática cancelada. Você continuará tendo acesso Premium até '
            f'{assinatura.data_expiracao.strftime("%d/%m/%Y")}.'
        )

    return redirect('profile')


@login_required
def historico_assinaturas_view(request):
    """
    Mostra o histórico completo de assinaturas do usuário.
    """
    assinaturas = request.user.assinaturas_premium.all().order_by('-created_at')
    assinatura_atual = request.user.obter_assinatura_ativa()

    context = {
        'assinaturas': assinaturas,
        'assinatura_atual': assinatura_atual,
    }

    return render(request, 'users/historico_assinaturas.html', context)

@login_required
def mock_premium_checkout_view(request):
    """
    View antiga mantida para compatibilidade.
    Redireciona para o novo sistema de assinaturas.
    """
    messages.info(request, 'Confira nossos planos Premium!')
    return redirect('escolher_plano')


@login_required
def escolher_plano_obrigatorio_view(request):
    """
    Versão especial da escolha de planos para profissionais novos.
    Não permite pular esta etapa - é obrigatória.
    """
    # Verifica se é profissional
    if not hasattr(request.user, 'profissional'):
        messages.error(request, 'Esta página é exclusiva para profissionais.')
        return redirect('home')

    # Se já tem assinatura ativa, não precisa estar aqui
    if request.user.tem_assinatura_ativa():
        messages.info(request, 'Você já tem uma assinatura ativa!')
        return redirect('profile')

    # Busca os planos disponíveis para profissionais
    planos = TipoPlano.objects.filter(
        tipo_usuario='profissional',
        ativo=True
    ).order_by('ordem', 'periodicidade')

    if not planos.exists():
        messages.error(request,
                       'Nenhum plano disponível no momento. Entre em contato com o suporte.')
        return redirect('profile')

    context = {
        'planos': planos,
        'tipo_usuario': 'profissional',
        'obrigatorio': True,  # Flag para o template saber que não pode pular
        'titulo': 'Escolha seu Plano Profissional',
        'subtitulo': 'Para ativar sua conta profissional, escolha um dos planos abaixo',
    }

    return render(request, 'users/escolher_plano_obrigatorio.html', context)
