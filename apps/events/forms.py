from django import forms
from .models import Evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        # Liste os campos que o usuário deve preencher
        fields = [
            'nome_evento',
            'descricao_do_evento',
            'foto_do_evento',
            'preco',
            'vagas_restantes',
            'data_e_hora',
            'localizacao_cidade',
            'localizacao_bairro_endereco',
            'categoria_de_esporte',
        ]
        # Opcional: Adiciona labels amigáveis
        labels = {
            'nome_evento': 'Nome do Evento',
            'descricao_do_evento': 'Descrição',
            'foto_do_evento': 'Foto de Capa do Evento',
            'vagas_restantes': 'Vagas Disponíveis',
            'data_e_hora': 'Data e Hora (ex: 2025-12-31 18:30)',
            'localizacao_cidade': 'Cidade',
            'localizacao_bairro_endereco': 'Endereço com Bairro',
            'categoria_de_esporte': 'Categoria (ex: Corrida, Yoga, Vôlei)',
        }