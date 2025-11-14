from django import forms
from .models import Evento, FotoEvento, CategoriaEvento
from django.utils import timezone


class EventoCreateForm(forms.ModelForm):
    """
    Formulário para Alunos e Profissionais criarem eventos.
    """
    # DateTimeInput nativo do Django funciona bem
    data_e_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label="Data e Hora do Evento"
    )

    class Meta:
        model = Evento
        fields = [
            'nome_evento',
            'descricao_do_evento',
            'foto_do_evento',
            'eh_pago',
            'preco',
            'vagas_restantes',
            'data_e_hora',
            'localizacao_cidade',
            'localizacao_bairro_endereco',
            'categoria',
        ]
        labels = {
            'nome_evento': 'Nome do Evento',
            'descricao_do_evento': 'Descrição',
            'foto_do_evento': 'Foto de Capa do Evento',
            'eh_pago': 'Este é um evento pago?',
            'preco': 'Valor do Ingresso (R$)',
            'vagas_restantes': 'Vagas Disponíveis',
            'data_e_hora': 'Data e Hora',
            'localizacao_cidade': 'Cidade',
            'localizacao_bairro_endereco': 'Endereço com Bairro',
            'categoria': 'Categoria'
        }
        widgets = {
            'descricao_do_evento': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descreva os detalhes, o que levar, etc.',
                'class': 'form-control'
            }),
            'eh_pago': forms.CheckboxInput(attrs={'id': 'id_eh_pago'}),
            'preco': forms.NumberInput(attrs={
                'placeholder': 'Ex: 25.50',
                'id': 'id_preco',
                'class': 'form-control',
                'step': '0.01'
            }),
            'nome_evento': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_do_evento': forms.FileInput(attrs={'class': 'form-control'}),
            'vagas_restantes': forms.NumberInput(attrs={'class': 'form-control'}),
            'localizacao_cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'localizacao_bairro_endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = CategoriaEvento.objects.all()

    def clean_data_e_hora(self):
        data = self.cleaned_data.get('data_e_hora')
        if data and data < timezone.now():
            raise forms.ValidationError(
                "Você não pode criar um evento em uma data passada.")
        return data

    def clean(self):
        cleaned_data = super().clean()
        eh_pago = cleaned_data.get('eh_pago')
        preco = cleaned_data.get('preco')

        if eh_pago:
            # Se marcou como pago, o preço é obrigatório e deve ser maior que 0
            if not preco or preco <= 0:
                self.add_error('preco',
                               "Para eventos pagos, o valor deve ser maior que R$ 0,00.")
        else:
            # Se não é pago, limpa o preço
            cleaned_data['preco'] = None

        return cleaned_data


class FotoEventoForm(forms.ModelForm):
    class Meta:
        model = FotoEvento
        fields = ['imagem', 'legenda']
        labels = {
            'imagem': 'Adicionar Foto',
            'legenda': 'Legenda (opcional)',
        }
        widgets = {
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'legenda': forms.TextInput(attrs={'class': 'form-control'}),
        }
