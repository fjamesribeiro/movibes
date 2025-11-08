from django import forms
from .models import Aluno, Profissional, Usuario

class UsuarioProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        # 2. Liste os campos que você quer editar
        fields = [
            'url_foto_perfil',
            'first_name',
            'last_name',
            'bio_curta',
            'link_social'
        ]
        labels = {
            'url_foto_perfil': 'Foto de Perfil',
            'first_name': 'Primeiro Nome',
            'last_name': 'Sobrenome',
            'bio_curta': 'Bio Curta (max 140 caracteres)',
            'link_social': 'Link Social (LinkedIn, Instagram, etc.)'
        }

class AlunoProfileForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = [
            'afinidades',
            'horarios_preferidos',
            'nivel_pratica',
            'objetivos',
            'vibe_after'
        ]

class ProfissionalProfileForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = [
            'especialidade'
        ]