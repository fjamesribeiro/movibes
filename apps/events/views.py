from django.shortcuts import render, get_object_or_404 # Garanta que 'get_object_or_404' está importado
from .models import Evento, Inscricao, Aluno # Garanta que 'Inscricao' e 'Aluno' estão importados
from django.contrib.auth.decorators import login_required # Nova importação
from django.http import HttpResponse, HttpResponseForbidden # Nova importação

# Esta é a view que será nossa homepage
def homepage(request):
    todos_os_eventos = Evento.objects.all().order_by('data_e_hora')  # Pega todos
    eventos_inscritos_ids = []  # Lista vazia por padrão
    # 1. Verifica se o usuário está logado e é um Aluno
    if request.user.is_authenticated:
        try:
            aluno = request.user.aluno
            # 2. Pega os IDs de todos os eventos que este aluno já se inscreveu
            eventos_inscritos_ids = Inscricao.objects.filter(
                id_aluno=aluno
            ).values_list('id_evento_id', flat=True)  # Retorna uma lista de IDs [1, 5, 12]

        except Aluno.DoesNotExist:
            # Usuário está logado, mas não é um aluno (ex: é Profissional ou Admin)
            pass  # A lista de IDs continua vazia

    contexto = {
        'eventos': todos_os_eventos,
        'eventos_inscritos_ids': eventos_inscritos_ids  # 3. Envia a lista para o template
    }

    return render(request, 'home.html', contexto)


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