from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import AlunoProfileForm, ProfissionalProfileForm, UsuarioProfileForm, \
    FotoUsuarioForm
from .models import Aluno, Profissional, Perfil, Usuario
from django.contrib import messages


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
    # 1. Busca o usuário pelo ID da URL. Se não encontrar, dá erro 404.
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    # 2. Inicializa variáveis
    profile_type = None
    fotos_galeria = None

    # 3. Descobre se é Aluno ou Profissional e busca dados
    if hasattr(usuario, 'aluno'):
        profile_type = 'aluno'
        # Busca todas as fotos da galeria deste aluno
        fotos_galeria = usuario.galeria.all()  #
    elif hasattr(usuario, 'profissional'):
        profile_type = 'profissional'
        # Profissionais (por enquanto) não têm galeria

    context = {
        'perfil_usuario': usuario,  # O usuário que estamos vendo (ex: Jônatas)
        'profile_type': profile_type,  # 'aluno' ou 'profissional'
        'fotos_galeria': fotos_galeria,  # A lista de fotos da galeria
    }

    # 4. Renderiza um NOVO template
    return render(request, 'account/public_profile.html', context)
