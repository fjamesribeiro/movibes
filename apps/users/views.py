from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import AlunoProfileForm, ProfissionalProfileForm, UsuarioProfileForm, \
    FotoUsuarioForm, AvaliacaoForm
from .models import Aluno, Profissional, Perfil, Usuario, Avaliacao
from django.contrib import messages
from django.db import models

@login_required
def complete_aluno_profile(request):
    """
    View para forçar o aluno a completar o cadastro
    após o primeiro login.
    """
    try:
        aluno_profile = request.user.aluno
    except Aluno.DoesNotExist:
        aluno_profile = Aluno.objects.create(usuario=request.user)

    if request.method == 'POST':
        # Usuário está enviando o formulário preenchido
        user_form = UsuarioProfileForm(request.POST, request.FILES, instance=request.user)
        profile_form = AlunoProfileForm(request.POST, instance=aluno_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            request.user.cadastro_completo = True
            request.user.save()
            messages.success(request, 'Seu perfil foi salvo! Bem-vindo(a) ao Movibes.')
            return redirect('home')
    else:
        user_form = UsuarioProfileForm(instance=request.user)
        profile_form = AlunoProfileForm(instance=aluno_profile)

    return render(request, 'account/complete_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def complete_profissional_profile(request):
    try:
        profile = request.user.profissional
    except Profissional.DoesNotExist:
        profile = Profissional.objects.create(usuario=request.user)

    if request.method == 'POST':
        user_form = UsuarioProfileForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfissionalProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            request.user.cadastro_completo = True
            request.user.save()
            messages.success(request, 'Seu perfil foi salvo! Bem-vindo(a) ao Movibes.')
            return redirect('home')
    else:
        user_form = UsuarioProfileForm(instance=request.user)
        profile_form = ProfissionalProfileForm(instance=profile)

    return render(request, 'account/complete_profile_profissional.html', {
        'user_form': user_form,
        'profile_form': profile_form  # Renomeado de 'form' para 'profile_form'
    })

@login_required
def set_profile_type(request, profile_type):
    """
    Esta view é chamada pelos botões da página de escolha.
    Ela define o perfil do usuário e redireciona.
    """
    user = request.user

    # Impede que o usuário mude de perfil se já completou o cadastro
    if user.cadastro_completo:
        return redirect('home')

    if profile_type == 'aluno':
        # Pega ou cria o Perfil "aluno"
        perfil, _ = Perfil.objects.get_or_create(nome='aluno')
        # Cria a entrada 1-para-1 do Aluno
        Aluno.objects.get_or_create(usuario=user)
        # Adiciona o perfil ao usuário (N-N)
        user.perfis.add(perfil)
        # Redireciona para completar o cadastro de ALUNO
        return redirect('account_complete_profile')

    elif profile_type == 'profissional':
        # Pega ou cria o Perfil "profissional"
        perfil, _ = Perfil.objects.get_or_create(nome='profissional')
        # Cria a entrada 1-para-1 do Profissional
        Profissional.objects.get_or_create(usuario=user)
        # Adiciona o perfil ao usuário (N-N)
        user.perfis.add(perfil)
        # Redireciona para completar o cadastro de PROFISSIONAL
        return redirect('account_complete_profile_profissional')

    # Se o tipo não for válido, manda de volta para a escolha
    return redirect('account_select_profile_type')


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
