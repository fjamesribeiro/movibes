from django.db import models
from apps.users.models import Usuario, Aluno  # Importa nossos modelos de usuário


class CategoriaEvento(models.Model):
    """ Tabela de cadastro das categorias (ex: Corrida, Yoga, Vôlei). """
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Evento"
        verbose_name_plural = "Categorias de Eventos"

# --- Modelo de Eventos ---
class Evento(models.Model):
    """ Tabela principal de eventos, criados por alunos ou profissionais. """
    nome_evento = models.TextField(null=True, blank=True)
    descricao_do_evento = models.TextField(null=True, blank=True)
    foto_do_evento = models.ImageField(upload_to='event_pics/', null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vagas_restantes = models.IntegerField(null=True, blank=True)
    participantes_confirmados = models.IntegerField(null=True, blank=True)
    link_pagamento = models.TextField(null=True, blank=True)
    data_e_hora = models.DateTimeField(null=True, blank=True)
    localizacao_cidade = models.TextField(null=True, blank=True)
    localizacao_bairro_endereco = models.TextField(null=True, blank=True)

    # DEPOIS:
    categoria = models.ForeignKey(
        CategoriaEvento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos'
    )

    # Chave estrangeira para o Usuário (aluno ou profissional) que criou.
    id_criador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='eventos_criados')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def __str__(self):
        return self.nome_evento or f"Evento {self.id}"


# --- Modelo de Inscrições ---
class Inscricao(models.Model):
    """ Tabela de ligação que registra a inscrição de um aluno em um evento. """
    id_aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='inscricoes')
    id_evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscricoes')

    testemunho = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Garante que um aluno não possa se inscrever 2x no mesmo evento
        constraints = [
            models.UniqueConstraint(fields=['id_aluno', 'id_evento'], name='unique_aluno_evento')
        ]
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"

    def __str__(self):
        return f"{self.id_aluno} @ {self.id_evento}"