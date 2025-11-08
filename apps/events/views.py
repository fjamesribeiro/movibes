from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Evento, Inscricao, Aluno, CategoriaEvento
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .forms import EventoForm


def homepage(request):
    # Buscar todas as categorias com contagem de eventos
    categorias = CategoriaEvento.objects.annotate(
        eventos_count=Count('eventos')
    ).order_by('nome')

    # Filtrar eventos
    eventos = Evento.objects.select_related(
        'id_criador',
        'categoria'
    ).all().order_by('data_e_hora')

    # Filtro por categoria
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        eventos = eventos.filter(categoria_id=categoria_id)

    # Busca por nome
    search = request.GET.get('search')
    if search:
        eventos = eventos.filter(
            Q(nome_evento__icontains=search) |
            Q(descricao_do_evento__icontains=search)
        )

    # Ordenação
    order = request.GET.get('order', 'data_e_hora')
    if order:
        eventos = eventos.order_by(order)

    # Eventos inscritos do usuário
    eventos_inscritos_ids = []
    if request.user.is_authenticated:
        try:
            aluno = request.user.aluno
            eventos_inscritos_ids = list(
                aluno.inscricoes.values_list('id_evento_id', flat=True)
            )
        except Aluno.DoesNotExist:
            pass

    context = {
        'eventos': eventos,
        'categorias': categorias,
        'eventos_inscritos_ids': eventos_inscritos_ids,
    }

    # Se for requisição HTMX, retornar apenas a lista
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