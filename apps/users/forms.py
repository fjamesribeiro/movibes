from django import forms
from .models import Aluno, Profissional, Usuario, VibeAfterOpcao, FotoUsuario, Avaliacao
from ..events.models import CategoriaEvento


class UsuarioProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'url_foto_perfil',
            'first_name',
            'last_name',
            'bio_curta',
            'whatsapp',
        ]
        labels = {
            'url_foto_perfil': 'Foto de Perfil',
            'first_name': 'Primeiro Nome',
            'last_name': 'Sobrenome',
            'bio_curta': 'Bio Curta (max 140 caracteres)',
            'whatsapp': 'WhatsApp (Ex: 85999998888)',
        }
widgets = {
    'url_foto_perfil': forms.FileInput,
}


class AlunoProfileForm(forms.ModelForm):
    preferencias_esporte = forms.ModelMultipleChoiceField(
        queryset=CategoriaEvento.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Quais esportes você curte?"
    )

    vibe_after = forms.ModelMultipleChoiceField(
        queryset=VibeAfterOpcao.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Como é o seu pós-treino?"
    )

    sexo = forms.ChoiceField(
        choices=Aluno.SEXO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'peer'}),
        required=False,
        initial=None
    )

    nivel_pratica = forms.ChoiceField(
        choices=Aluno.NIVEL_PRATICA_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'peer'}),
        required=False,
        label='Nível de Prática',
        initial=None
    )

    periodos_preferidos = forms.ChoiceField(
        choices=Aluno.PERIODOS_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'peer'}),
        required=False,
        label='Período preferido',
        initial=None
    )

    class Meta:
        model = Aluno
        fields = [
            'sexo',
            'preferencias_esporte',
            'vibe_after',
            'nivel_pratica',
            'periodos_preferidos',
            'status_social',
            'estado',
            'cidade',
            'bairro',
            'tipo_conta',
        ]

        widgets = {
            'status_social': forms.RadioSelect(attrs={'class': 'peer'}),
            'tipo_conta': forms.RadioSelect(attrs={'class': 'peer'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'status_social' in self.fields:
            self.fields['status_social'].empty_label = None
            self.fields['status_social'].required = False

        if 'tipo_conta' in self.fields:
            self.fields['tipo_conta'].empty_label = None
            self.fields['tipo_conta'].required = True


class ProfissionalProfileForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = [
            'especialidade',
            'num_conselho_classe',
        ]
        labels = {
            'num_conselho_classe': 'Nº Conselho de classe',
        }

class FotoUsuarioForm(forms.ModelForm):
    """
    Formulário para fazer upload de uma nova foto para a galeria.
    """
    class Meta:
        model = FotoUsuario
        fields = ['imagem', 'legenda'] # O 'usuario' será definido na view
        labels = {
            'imagem': 'Nova Foto',
            'legenda': 'Legenda (opcional)',
        }

class AvaliacaoForm(forms.ModelForm):
    """
    Formulário para um Aluno avaliar um Profissional.
    """
    # Definindo as escolhas de nota de forma amigável
    NOTA_CHOICES = (
        (5, '★★★★★ (5 Estrelas)'),
        (4, '★★★★☆ (4 Estrelas)'),
        (3, '★★★☆☆ (3 Estrelas)'),
        (2, '★★☆☆☆ (2 Estrelas)'),
        (1, '★☆☆☆☆ (1 Estrela)'),
    )

    nota = forms.ChoiceField(
        choices=NOTA_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full p-4 bg-gray-700/50 border border-gray-600 rounded-xl text-white ...'}),
        label="Sua Nota"
    )

    class Meta:
        model = Avaliacao
        # Apenas os campos que o usuário preenche
        fields = ['nota', 'comentario']
        labels = {
            'comentario': 'Seu Comentário (opcional)',
        }
        widgets = {
            'comentario': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Descreva sua experiência com este profissional...',
                    'class': 'w-full p-4 bg-gray-700/50 border border-gray-600 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-all resize-none'
                }
            ),
        }
