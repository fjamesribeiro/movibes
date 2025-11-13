from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
from apps.users.models import ImageResizingMixin

class CategoriaEvento(models.Model):
    """ Tabela de cadastro das categorias (ex: Corrida, Yoga, Vôlei). """
    nome = models.CharField(max_length=100, unique=True)
    icone = models.CharField(max_length=10, null=True, blank=True,
                             help_text="Cole o emoji aqui (ex: 🏃)")

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
    id_criador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

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
    id_aluno = models.ForeignKey('users.Aluno', on_delete=models.CASCADE, related_name='inscricoes')

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


class FotoEvento(ImageResizingMixin, models.Model):
    """
    Armazena uma foto da galeria de um Evento,
    enviada por um usuário.
    Reutiliza o ImageResizingMixin para otimização.
    """
    # Relacionamentos
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="galeria"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fotos_enviadas_evento"
    )

    # Campos da Foto
    imagem = models.ImageField(upload_to='event_gallery/')
    legenda = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto de Evento"
        verbose_name_plural = "Fotos de Eventos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Foto de {self.evento.titulo} por {self.usuario.first_name}"

    def save(self, *args, **kwargs):
        # Chama a função de redimensionamento do Mixin
        if self.imagem:
            self.imagem = self.resize_image(self.imagem)
        super().save(*args, **kwargs)


class InteracaoPresenca(models.Model):
    """
    Rastreia uma "curtida" (like) que um usuário (autor) dá
    na presença (Inscricao) de outro usuário.
    Também rastreia o "like de volta" (status_retorno).
    """

    # --- Status Choices ---
    STATUS_RETORNO_CHOICES = [
        ('pendente', 'Pendente'),  # O "like de volta" ainda não foi dado
        ('aceito', 'Aceito'),  # O "like de volta" foi dado
    ]

    # --- Relacionamentos ---
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="curtidas_dadas"
    )
    inscricao_alvo = models.ForeignKey(
        Inscricao,
        on_delete=models.CASCADE,
        related_name="curtidas_recebidas"
    )

    # --- Campos de Estado ---
    status_retorno = models.CharField(
        max_length=10,
        choices=STATUS_RETORNO_CHOICES,
        default='pendente'
    )
    lida_pelo_alvo = models.BooleanField(
        default=False,
        help_text="Notificação lida pelo dono da inscrição (quem recebeu o 1º like)"
    )
    lida_pelo_autor = models.BooleanField(
        default=False,
        help_text="Notificação lida pelo autor (quem recebeu o 'like de volta')"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Interação de Presença"
        verbose_name_plural = "Interações de Presença"
        ordering = ['-updated_at']
        # Garante que um usuário só pode curtir uma inscrição uma única vez
        constraints = [
            UniqueConstraint(
                fields=['autor', 'inscricao_alvo'],
                name='unique_curtida_presenca'
            )
        ]

    def __str__(self):
        return f"Interação de {self.autor.email} para {self.inscricao_alvo.id_aluno.usuario.email}"
