from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Evento, Inscricao, CategoriaEvento
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .forms import EventoForm
from apps.users.models import Aluno


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

@login_required  # 1. Garante que apenas usuários logados acessem
def subscribe_to_event(request, event_id):
    # 2. Só aceita requisições POST (que vêm do HTMX)
    if request.method != 'POST':
        return HttpResponseForbidden()

    # 3. Pega o usuário e o evento
    user = request.user
    evento = get_object_or_404(Evento, pk=event_id)

    # 4. LÓGICA DE NEGÓCIO: Verifica se o usuário é um Aluno
    try:
        # Tenta acessar o perfil de aluno do usuário logado
        aluno = user.aluno
    except Aluno.DoesNotExist:
        # Se não tiver, retorna um erro 403 (Proibido)
        return HttpResponse("Apenas alunos podem se inscrever.", status=403)

    # 5. CÚPULA DO HTMX: Cria a inscrição e retorna o novo HTML
    # Usamos get_or_create para evitar duplicatas se o usuário clicar rápido
    Inscricao.objects.get_or_create(id_aluno=aluno, id_evento=evento)

    # 6. RESPOSTA HTMX: Retorna o HTML do novo botão
    # Este é o fragmento que o HTMX vai "trocar" na tela
    return HttpResponse(
        '<button class="bg-green-500 text-white font-semibold px-4 py-2 rounded-md text-sm" disabled>✓ Inscrito</button>'
    )


@login_required  # Só usuários logados podem criar eventos
def create_event(request):
    """
    Mostra o formulário para criar um novo evento.
    """
    if request.method == 'POST':
        # Usuário está enviando o formulário
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            # Não salve no banco ainda, precisamos adicionar o criador
            evento = form.save(commit=False)
            # 3. Define o 'id_criador' como o usuário logado
            evento.id_criador = request.user
            # 4. Define um status padrão
            evento.status = 'ativo'
            # 5. Agora sim, salva no banco
            evento.save()
            # 6. Redireciona para a homepage para ver o evento criado
            return redirect('home')
    else:
        # Usuário está vendo a página (GET)
        form = EventoForm()

    # Vamos criar este template no próximo passo
    return render(request, 'events/create_event.html', {'form': form})
