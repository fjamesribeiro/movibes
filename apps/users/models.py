from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.db import models


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
    link_social = models.TextField(null=True, blank=True)
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


# --- Modelo de Aluno ---
class Aluno(models.Model):
    """ Armazena dados específicos de usuários que são alunos. """
    # Ligação 1-para-1 com o Usuário. A PK do Aluno será a FK do Usuário.
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    afinidades = ArrayField(models.TextField(), null=True, blank=True)
    horarios_preferidos = models.TextField(null=True, blank=True)
    nivel_pratica = models.TextField(null=True, blank=True)
    objetivos = models.TextField(null=True, blank=True)
    vibe_after = models.TextField(null=True, blank=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"

    def __str__(self):
        return self.usuario.email