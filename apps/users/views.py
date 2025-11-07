from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AlunoProfileForm
from .models import Aluno


@login_required
def complete_aluno_profile(request):
    """
    View para forçar o aluno a completar o cadastro
    após o primeiro login.
    """
    try:
        # Pega o perfil de aluno vinculado a este usuário
        aluno_profile = request.user.aluno
    except Aluno.DoesNotExist:
        # Se por algum motivo não tiver um perfil,
        # (o que não deve acontecer por causa do nosso adapter)
        # criamos um.
        aluno_profile = Aluno.objects.create(usuario=request.user)

    if request.method == 'POST':
        # Usuário está enviando o formulário preenchido
        form = AlunoProfileForm(request.POST, instance=aluno_profile)
        if form.is_valid():
            form.save()

            # ATUALIZA O FLAG NO 'USUARIO'
            request.user.cadastro_completo = True
            request.user.save()

            # Redireciona para a homepage
            return redirect('home')
    else:
        # Usuário está vendo a página pela primeira vez (GET)
        form = AlunoProfileForm(instance=aluno_profile)

    return render(request, 'account/complete_profile.html', {'form': form})