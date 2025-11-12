from django.contrib.auth.models import AbstractUser, BaseUserManager
import io
from django.conf import settings
from django.db import models
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image


class ImageResizingMixin:
    """
    Mixin de modelo para redimensionar imagens antes de salvar.
    Requer a biblioteca 'Pillow'.
    """
    MAX_IMAGE_WIDTH = 1024  # Largura máxima em pixels
    MAX_IMAGE_HEIGHT = 1024  # Altura máxima em pixels
    IMAGE_QUALITY = 85  # Qualidade do JPEG (0-100)

    def resize_image(self, image_field):
        """ Redimensiona e otimiza a imagem. """
        try:
            # Abre a imagem em memória
            img = Image.open(image_field)

            # Converte para RGB se for RGBA (remove transparência)
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Checa o tamanho
            if img.width > self.MAX_IMAGE_WIDTH or img.height > self.MAX_IMAGE_HEIGHT:
                img.thumbnail((self.MAX_IMAGE_WIDTH, self.MAX_IMAGE_HEIGHT),
                              Image.LANCZOS)

            # Salva a imagem otimizada em um buffer de memória
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=self.IMAGE_QUALITY)

            # Cria um novo ContentFile do Django com a imagem otimizada
            new_image = ContentFile(thumb_io.getvalue(), name=image_field.name)
            return new_image

        except Exception as e:
            # Se a imagem for inválida (ex: SVG), apenas retorne a original
            print(f"Erro ao redimensionar imagem: {e}")
            return image_field


class VibeAfterOpcao(models.Model):
    """ Tabela de cadastro das opções de pós-treino. """
    nome = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Opção de Vibe After"
        verbose_name_plural = "Opções de Vibe After"

    def __str__(self):
        return self.nome


# --- Modelo de Perfil (RBAC) ---
class Perfil(models.Model):
    """ Tabela de cadastro dos perfis (roles) do sistema para RBAC. """
    nome = models.TextField(unique=True, null=False, blank=False)  # 'admin', 'aluno', 'profissional'

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return self.nome


# --- Modelo de Usuário Customizado ---
class UsuarioManager(BaseUserManager):
    """
    Manager customizado para o nosso modelo de Usuário que usa e-mail como identificador único.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e salva um usuário com o e-mail e senha fornecidos.
        """
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria e salva um superusuário com o e-mail e senha fornecidos.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')

        # first_name e last_name virão de 'REQUIRED_FIELDS' e estarão em extra_fields
        return self.create_user(email, password, **extra_fields)


# --- Modelo de Usuário Customizado ---
class Usuario(AbstractUser):
    """ Tabela central que herda do User padrão do Django e adiciona nossos campos. """
    # Removemos o username, usaremos email como login
    username = None
    email = models.EmailField(unique=True)  # Email de login, deve ser único

    # Nossos campos customizados
    url_foto_perfil = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio_curta = models.TextField(null=True, blank=True)
    whatsapp = models.CharField(
        max_length=20,
        null=True, blank=True,
        verbose_name="WhatsApp"
    )
    cadastro_completo = models.BooleanField(default=False)

    # Campo que define qual é o "username" (para o django-admin)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Campos pedidos no 'createsuperuser'

    # Diga ao Django para usar o nosso manager
    objects = UsuarioManager()

    # Perfis (RBAC)
    perfis = models.ManyToManyField(
        Perfil,
        through='UsuarioPerfil',  # Define a tabela de ligação
        related_name='usuarios'
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.email


class FotoUsuario(ImageResizingMixin, models.Model):
    """ Armazena fotos da galeria de um usuário (ex: Aluno). """
    # Relacionamentos
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="galeria"
    )

    # Campos da Foto
    imagem = models.ImageField(upload_to='user_gallery/')
    legenda = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto do Usuário"
        verbose_name_plural = "Fotos dos Usuários"
        ordering = ['-created_at']

    def __str__(self):
        return f"Foto de {self.usuario.first_name} ({self.id})"

    def save(self, *args, **kwargs):
        # Chama a função de redimensionamento do Mixin
        if self.imagem:
            self.imagem = self.resize_image(self.imagem)
        super().save(*args, **kwargs)

    # O campo para a imagem
    imagem = models.ImageField(
        upload_to='galerias_usuarios/%Y/%m/%d/',
        help_text="Foto da galeria do usuário"
    )

    legenda = models.CharField(max_length=255, blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto da Galeria"
        verbose_name_plural = "Fotos da Galeria"
        ordering = ['-data_upload']  # Mais nova primeiro

    def save(self, *args, **kwargs):
        # Se for uma imagem nova, redimensiona
        if self.pk is None and self.imagem:
            # Abrir a imagem em memória
            img = Image.open(self.imagem)

            # Definir tamanho máximo (ex: 1920px de largura)
            max_width = 1920
            if img.width > max_width:
                # Calcular a nova altura mantendo a proporção
                new_height = int((max_width / img.width) * img.height)
                img = img.resize((max_width, new_height),
                                 Image.LANCZOS)  # Usa um algoritmo de alta qualidade

            # Salvar a imagem otimizada de volta no campo
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG',
                     quality=85)  # Salva como JPEG com 85% de qualidade

            # Reescreve o 'self.imagem' com a versão otimizada
            self.imagem.file = ContentFile(img_io.getvalue(), name=self.imagem.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Foto de {self.usuario.username} - {self.data_upload.strftime('%d/%m/%Y')}"

# --- Tabela de Ligação Usuário-Perfil (RBAC) ---
class UsuarioPerfil(models.Model):
    """ Tabela de ligação (N-N) que associa usuários a perfis. """
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id_usuario', 'id_perfil'], name='unique_usuario_perfil')
        ]
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"


class TipoConta(models.Model):
    """ Tabela de cadastro dos tipos de conta (ex: Free, Premium). """
    nome = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tipo de Conta"
        verbose_name_plural = "Tipos de Conta"

    def __str__(self):
        return self.nome


class StatusSocial(models.Model):
    """ Tabela de cadastro dos status sociais (ex: Aberto a amizades). """
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Status Social"
        verbose_name_plural = "Status Sociais"

    def __str__(self):
        return self.nome

# --- Modelo de Aluno ---
class Aluno(models.Model):
    """ Armazena dados específicos de usuários que são alunos. """
    # --- DEFINIÇÃO DAS ESCOLHAS (CHOICES) ---
    NIVEL_PRATICA_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
    ]

    PERIODOS_CHOICES = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite'),
    ]

    VIBE_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
        ('as_vezes', 'Às vezes'),
    ]

    SEXO_CHOICES = [
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('nao_informar', 'Prefiro não responder'),
    ]

    # Ligação 1-para-1 com o Usuário. A PK do Aluno será a FK do Usuário.
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    # --- NOVOS CAMPOS DE RELAÇÃO (FK/M2M) ---
    tipo_conta = models.ForeignKey(
        TipoConta,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Tipo de Conta"
    )

    preferencias_esporte = models.ManyToManyField(
        'events.CategoriaEvento',
        blank=True,
        verbose_name="Preferências de Esporte"
    )

    status_social = models.ForeignKey(
        StatusSocial,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Status Social"
    )

    # --- CAMPOS MODIFICADOS (AGORA COM CHOICES) ---
    periodos_preferidos = models.CharField(
        max_length=20,
        choices=PERIODOS_CHOICES,
        null=True, blank=True,
        verbose_name="Períodos Preferidos"
    )

    nivel_pratica = models.CharField(
        max_length=20,
        choices=NIVEL_PRATICA_CHOICES,
        null=True, blank=True,
        verbose_name="Nível de Prática"
    )

    vibe_after = models.ManyToManyField(
        VibeAfterOpcao,
        blank=True,
        verbose_name="Como é o seu pós-treino?"
    )

    sexo = models.CharField(
        max_length=20,
        choices=SEXO_CHOICES,
        null=True, blank=True,
        verbose_name="Sexo"
    )

    estado = models.CharField(max_length=100, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def __str__(self):
        return self.usuario.email


# --- Modelo de Profissional ---
class Profissional(models.Model):
    """ Armazena dados específicos de usuários que são profissionais. """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    especialidade = models.TextField(null=True, blank=True)
    num_conselho_classe = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"

    def __str__(self):
        return self.usuario.email
