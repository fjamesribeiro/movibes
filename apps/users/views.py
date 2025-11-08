from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AlunoProfileForm, ProfissionalProfileForm, UsuarioProfileForm
from .models import Aluno, Profissional, Perfil


@login_required
def select_profile_type(request):
    """
    Mostra a página para o usuário escolher entre Aluno ou Profissional.
    Esta é a página para onde os novos usuários serão redirecionados.
    """
    # Se o usuário já completou o cadastro, não o deixe ver esta página.
    if request.user.cadastro_completo:
        return redirect('home')

    # Apenas renderiza o template de escolha
    return render(request, 'account/select_profile_type.html')

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