from django import forms
from .models import Aluno

class AlunoProfileForm(forms.ModelForm):
    class Meta:
        model = Aluno
        # Especifique os campos do Aluno que você quer no formulário
        fields = [
            'afinidades',
            'horarios_preferidos',
            'nivel_pratica',
            'objetivos',
            'vibe_after'
        ]
        # (Você pode adicionar ou remover campos desta lista)