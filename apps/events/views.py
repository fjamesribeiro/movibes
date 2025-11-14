from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Evento, Inscricao, CategoriaEvento, Pagamento, InteracaoPresenca
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .forms import EventoCreateForm, FotoEventoForm
from apps.users.models import Aluno
from django.contrib import messages


def home(request):
    # Buscar todos os eventos
    eventos = Evento.objects.all().select_related('categoria', 'id_criador')

    # Filtro de busca por nome
    search = request.GET.get('search', '').strip()
    if search:
        eventos = eventos.filter(
            Q(nome_evento__icontains=search) |
            Q(descricao_do_evento__icontains=search)
        )

    # Filtro de categorias (múltiplas seleções)
    categorias_ids = request.GET.getlist('categorias')
    if categorias_ids:
        eventos = eventos.filter(categoria_id__in=categorias_ids)

    # Filtro de cidade
    cidade = request.GET.get('cidade', '').strip()
    if cidade:
        eventos = eventos.filter(localizacao_cidade__icontains=cidade)

    # Filtro de bairro
    bairro = request.GET.get('bairro', '').strip()
    if bairro:
        eventos = eventos.filter(localizacao_bairro_endereco__icontains=bairro)

    # Filtro de status
    status_filtros = request.GET.getlist('status')
    if status_filtros:
        status_q = Q()
        if 'vagas_disponiveis' in status_filtros:
            status_q |= Q(vagas_restantes__gt=5)
        if 'quase_lotado' in status_filtros:
            status_q |= Q(vagas_restantes__lte=5, vagas_restantes__gt=0)
        if 'confirmado' in status_filtros:
            status_q |= Q(status='confirmado')
        eventos = eventos.filter(status_q)

    # Filtro de data (atalhos rápidos)
    after_filtros = request.GET.getlist('after')
    hoje = datetime.now().date()

    if after_filtros:
        data_q = Q()
        if 'hoje' in after_filtros:
            data_q |= Q(data_e_hora__date=hoje)
        if 'amanha' in after_filtros:
            amanha = hoje + timedelta(days=1)
            data_q |= Q(data_e_hora__date=amanha)
        if 'esta_semana' in after_filtros:
            fim_semana = hoje + timedelta(days=7)
            data_q |= Q(data_e_hora__date__range=[hoje, fim_semana])
        if 'proximo_mes' in after_filtros:
            fim_mes = hoje + timedelta(days=30)
            data_q |= Q(data_e_hora__date__range=[hoje, fim_mes])
        eventos = eventos.filter(data_q)

    # Filtro de período personalizado
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    if data_inicio:
        eventos = eventos.filter(data_e_hora__date__gte=data_inicio)
    if data_fim:
        eventos = eventos.filter(data_e_hora__date__lte=data_fim)

    # Ordenar por data
    eventos = eventos.order_by('data_e_hora')

    # Buscar categorias com contagem de eventos
    categorias = CategoriaEvento.objects.annotate(
        eventos_count=Count('eventos')
    ).order_by('nome')

    # Buscar cidades e bairros únicos para autocomplete
    cidades_disponiveis = Evento.objects.values_list(
        'localizacao_cidade', flat=True
    ).distinct().order_by('localizacao_cidade')

    bairros_disponiveis = Evento.objects.values_list(
        'localizacao_bairro_endereco', flat=True
    ).distinct().order_by('localizacao_bairro_endereco')

    context = {
        'eventos': eventos,
        'categorias': categorias,
        'cidades_disponiveis': [c for c in cidades_disponiveis if c],
        'bairros_disponiveis': [b for b in bairros_disponiveis if b],
    }

    # Se for requisição HTMX, retornar apenas a lista de eventos
    if request.headers.get('HX-Request'):
        return render(request, 'partials/eventos_list.html', context)

    return render(request, 'home.html', context)


@login_required
def subscribe_to_event(request, event_id):
    """
    Inscreve um aluno em um evento (apenas eventos GRATUITOS).
    Chamado via HTMX.
    """
    evento = get_object_or_404(Evento, pk=event_id)
    aluno = get_object_or_404(Aluno, usuario=request.user)
    # --- 6. REGRA DE NEGÓCIO ADICIONADA ---
    # Se o evento for pago, esta view não deve fazer nada.
    if evento.eh_pago:
        messages.error(request,
                       'Este é um evento pago e não pode ser inscrito por aqui.')
        return redirect('evento_detail', evento_id=evento.id)
    # --- FIM DA REGRA ---
    inscricao_existente = Inscricao.objects.filter(id_aluno=aluno,
                                                   id_evento=evento).first()

    if inscricao_existente:
        inscricao_existente.delete()
        is_subscribed = False
        messages.success(request, 'Inscrição cancelada.')
    else:
        Inscricao.objects.create(id_aluno=aluno, id_evento=evento)
        is_subscribed = True
        messages.success(request, 'Inscrição realizada com sucesso!')

    context = {
        'evento': evento,
        'is_subscribed': is_subscribed,
    }
    # Retorna o partial do botão
    return render(request, 'partials/subscribe_button.html', context)


@login_required
def create_event(request):
    """
    Usa o novo EventoCreateForm para criar um evento.
    Passa o 'request.user' para o formulário.
    """
    if request.method == 'POST':
        # 3. Passe 'user=request.user' para o formulário
        form = EventoCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.id_criador = request.user
            # 4. Lógica para salvar o preço correto (do clean do form)
            if not form.cleaned_data.get('eh_pago'):
                evento.preco = None
            else:
                evento.preco = form.cleaned_data.get('preco')

            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('home')  # TODO: Mudar para a página do evento
    else:
        # 5. Passe 'user=request.user' também no GET
        form = EventoCreateForm(user=request.user)

    return render(request, 'events/create_event.html', {'form': form})


@login_required
def modal_premium_view(request):
    """
    Retorna o HTML do modal premium para uso com HTMX.
    """
    return render(request, 'partials/modal_premium.html')


@login_required
def processar_curtida_presenca_view(request, inscricao_id):
    """
    Chamada via HTMX quando o usuário clica em "Curtir" na lista de participantes.
    Cria a interação de presença.
    """
    # Apenas Alunos podem curtir (regra de negócio)
    if not hasattr(request.user, 'aluno'):
        return HttpResponseForbidden("Apenas alunos podem interagir.")

    inscricao_alvo = get_object_or_404(Inscricao, pk=inscricao_id)

    # Impede curtir a si mesmo
    if inscricao_alvo.id_aluno.usuario == request.user:
        return HttpResponse("Você não pode curtir a si mesmo.", status=400)

    # Cria a interação (get_or_create evita duplicatas)
    # O default é status_retorno='pendente' e lida_pelo_alvo=False
    InteracaoPresenca.objects.get_or_create(
        autor=request.user,
        inscricao_alvo=inscricao_alvo
    )

    # Retorna o botão atualizado (estado "Curtida enviada")
    # Vamos criar este pequeno template parcial no próximo passo
    return render(request, 'partials/botao_curtida_estado.html', {
        'inscricao': inscricao_alvo,
        'ja_curtiu': True
    })


@login_required
def gerenciar_galeria_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    # Definimos quem é o criador
    is_creator = (evento.id_criador == request.user)

    # REGRA DE NEGÓCIO 1: Só pode adicionar fotos a eventos passados
    if evento.data_e_hora >= timezone.now():
        messages.error(request,
                       'Você só pode gerenciar a galeria de eventos que já ocorreram.')
        # TODO: Redirecionar para a página pública do evento quando ela existir
        return redirect('home')

    # REGRA DE NEGÓCIOS 2: Apenas o criador pode fazer UPLOAD (POST)
    if request.method == 'POST':
        # Se não for o criador, bloqueia a tentativa de POST
        if not is_creator:
            messages.error(request,
                           'Você não tem permissão para adicionar fotos a este evento.')
            return redirect('account_galeria_evento', evento_id=evento.id)

        form = FotoEventoForm(request.POST, request.FILES)
        if form.is_valid():
            foto = form.save(commit=False)
            foto.evento = evento
            foto.usuario = request.user  # Salva quem enviou
            foto.save()
            messages.success(request, 'Foto adicionada à galeria do evento!')
            return redirect('account_galeria_evento', evento_id=evento.id)
    else:
        # Se for um GET, apenas prepara o formulário
        form = FotoEventoForm()

    # Pega todas as fotos existentes para mostrar na página
    fotos_galeria = evento.galeria.all()

    return render(request, 'events/galeria_evento.html', {
        'form': form,
        'evento': evento,
        'fotos': fotos_galeria,
        'is_creator': is_creator  # Passa a permissão para o template
    })


@login_required
def like_inscricao_view(request, inscricao_id):
    """
    Adiciona ou remove uma 'curtida' de uma inscrição (presença).
    Esta view é chamada via HTMX.
    """
    # Só alunos podem curtir
    if not hasattr(request.user, 'aluno'):
        messages.error(request, 'Apenas alunos podem interagir.')
        return redirect(request.META.get('HTTP_REFERER', 'home')) # Volta para onde estava

    inscricao = get_object_or_404(Inscricao, pk=inscricao_id)

    # Tenta encontrar uma curtida existente
    try:
        curtida_existente = InteracaoPresenca.objects.get(
            usuario=request.user,
            inscricao=inscricao
        )
        # Se encontrou, o usuário está "descurtindo"
        curtida_existente.delete()
        is_liked = False
    except InteracaoPresenca.DoesNotExist:
        # Se não encontrou, o usuário está "curtindo"
        InteracaoPresenca.objects.create(
            usuario=request.user,
            inscricao=inscricao
        )
        is_liked = True

    # Prepara o contexto para o partial do botão
    context = {
        'inscricao': inscricao,
        'is_liked': is_liked # Passa o novo status
    }
    # Retorna SÓ o botão atualizado
    return render(request, 'partials/like_button.html', context)


def evento_detail_view(request, evento_id):
    """
    Mostra a página de detalhes do evento.
    """
    evento = get_object_or_404(Evento, pk=evento_id)
    is_past = evento.data_e_hora < timezone.now()
    fotos_galeria = []
    if is_past:
        fotos_galeria = evento.galeria.all()

    inscricoes = evento.inscricoes.all().select_related('id_aluno__usuario')
    total_participantes = inscricoes.count()

    # Inicializa todas as variáveis como False/vazio
    curtidas_pelo_usuario_ids = []
    is_subscribed = False
    has_paid = False
    is_premium = False
    is_aluno = False
    can_view_participants = False
    participant_preview = None

    if request.user.is_authenticated:
        is_aluno = hasattr(request.user, 'aluno')

        if is_aluno:
            # Verifica se é premium
            try:
                is_premium = request.user.eh_premium()
            except:
                is_premium = False

            # Define permissões para ver participantes
            can_view_participants = (
                is_premium or
                request.user == evento.id_criador
            )

            if not is_premium and is_past:
                participant_preview = inscricoes[:3]

        # Criador sempre pode ver participantes
        if request.user == evento.id_criador:
            can_view_participants = True

        # Busca curtidas do usuário
        curtidas_pelo_usuario_ids = InteracaoPresenca.objects.filter(
            autor=request.user,
            inscricao_alvo__in=inscricoes
        ).values_list('inscricao_alvo_id', flat=True)

        # LÓGICA PRINCIPAL DE INSCRIÇÃO
        if is_aluno:
            try:
                if evento.eh_pago:
                    # EVENTO PAGO: A regra é clara
                    # 1. Primeiro verifica se existe PAGAMENTO aprovado
                    has_paid = Pagamento.objects.filter(
                        usuario=request.user,
                        evento=evento,
                        status='aprovado'
                    ).exists()

                    # 2. Se tem pagamento aprovado, ele está inscrito
                    # Se NÃO tem pagamento, ele NÃO está inscrito (mesmo que exista Inscricao)
                    is_subscribed = has_paid

                else:
                    # EVENTO GRATUITO: Só verifica a inscrição
                    is_subscribed = Inscricao.objects.filter(
                        id_aluno=request.user.aluno,
                        id_evento=evento
                    ).exists()
                    # Em evento gratuito, has_paid sempre é False
                    has_paid = False

            except Aluno.DoesNotExist:
                is_subscribed = False
                has_paid = False

    context = {
        'evento': evento,
        'is_past': is_past,
        'fotos_galeria': fotos_galeria,
        'is_subscribed': is_subscribed,
        'inscricoes': inscricoes,
        'curtidas_pelo_usuario_ids': curtidas_pelo_usuario_ids,
        'has_paid': has_paid,
        'total_participantes': total_participantes,
        'is_premium': is_premium,
        'is_aluno': is_aluno,
        'can_view_participants': can_view_participants,
        'participant_preview': participant_preview,
    }
    return render(request, 'events/evento_detail.html', context)


@login_required
def mock_checkout_view(request, evento_id):
    """
    Exibe a tela de checkout com os detalhes do evento e valor a pagar.
    Esta é apenas a tela de visualização, não processa o pagamento ainda.
    """
    evento = get_object_or_404(Evento, pk=evento_id)

    # Valida que o usuário é um aluno
    try:
        aluno = request.user.aluno
    except:
        messages.error(request, 'Apenas alunos podem comprar ingressos.')
        return redirect('evento_detail', evento_id=evento.id)

    # Verifica se o evento é pago
    if not evento.eh_pago:
        messages.error(request, 'Este evento é gratuito.')
        return redirect('evento_detail', evento_id=evento.id)

    # Verifica se já pagou
    ja_pagou = Pagamento.objects.filter(
        usuario=request.user,
        evento=evento,
        status='aprovado'
    ).exists()

    if ja_pagou:
        messages.info(request, 'Você já comprou o ingresso para este evento!')
        return redirect('evento_detail', evento_id=evento.id)

    # Se passou por todas as validações, mostra a tela de checkout
    context = {
        'evento': evento,
        'aluno': aluno,
    }
    return render(request, 'events/checkout.html', context)


@login_required
def processar_pagamento_view(request, evento_id):
    """
    Processa efetivamente o pagamento após o usuário confirmar na tela de checkout.
    Só aceita requisições POST.
    """
    # Só aceita POST (quando o usuário clica em "Confirmar Pagamento")
    if request.method != 'POST':
        return redirect('mock_checkout', evento_id=evento_id)

    evento = get_object_or_404(Evento, pk=evento_id)

    # Valida que o usuário é um aluno
    try:
        aluno = request.user.aluno
    except:
        messages.error(request, 'Apenas alunos podem comprar ingressos.')
        return redirect('evento_detail', evento_id=evento.id)

    # Verifica se o evento é pago
    if not evento.eh_pago:
        messages.error(request, 'Este evento é gratuito.')
        return redirect('evento_detail', evento_id=evento.id)

    # Verifica se já pagou (última validação antes de processar)
    ja_pagou = Pagamento.objects.filter(
        usuario=request.user,
        evento=evento,
        status='aprovado'
    ).exists()

    if ja_pagou:
        messages.info(request, 'Você já comprou o ingresso para este evento!')
        return redirect('evento_detail', evento_id=evento.id)

    # --- AGORA SIM, PROCESSA O PAGAMENTO ---

    # Cria o registro de Pagamento
    pagamento = Pagamento.objects.create(
        usuario=request.user,
        evento=evento,
        valor_pago=evento.preco,
        status='aprovado',
        id_transacao_externa=f"mock_{request.user.id}_{evento.id}_{timezone.now().timestamp()}"
    )

    # Garante que existe a Inscrição
    inscricao, criada = Inscricao.objects.get_or_create(
        id_aluno=aluno,
        id_evento=evento
    )

    # Atualiza vagas se necessário
    if evento.vagas_restantes and evento.vagas_restantes > 0:
        evento.vagas_restantes -= 1
        evento.save()

    # Mensagem de sucesso
    messages.success(request,
                     f'Pagamento de R$ {evento.preco} confirmado com sucesso! Você está inscrito no evento.')
    return redirect('evento_detail', evento_id=evento.id)
