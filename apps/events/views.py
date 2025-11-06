from django.shortcuts import render
from .models import Evento  # Importa seu modelo de Evento


# Esta é a view que será nossa homepage
def homepage(request):
    # 1. Busca todos os objetos "Evento" no banco de dados
    todos_os_eventos = Evento.objects.all()

    # 2. Define o contexto (dados) que vamos enviar para o HTML
    contexto = {
        'eventos': todos_os_eventos
    }

    # 3. Renderiza o template "home.html" com esses dados
    return render(request, 'home.html', contexto)