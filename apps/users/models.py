from django.contrib.auth.models import AbstractUser, BaseUserManager
import io
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta


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
    perfil_escolhido = models.BooleanField(
        default=False,
        help_text="Indica se o usuário já escolheu ser Aluno ou Profissional"
    )
    metodo_registro = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email/Senha'),
            ('google', 'Google OAuth2'),
        ],
        default='email',
        help_text="Método usado no primeiro cadastro"
    )
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

    def tem_assinatura_ativa(self):
        """
        Verifica se o usuário tem qualquer assinatura ativa.
        Funciona tanto para Alunos Premium quanto Profissionais Pro.
        """
        return self.assinaturas_premium.filter(
            status='ativa',
            data_inicio__lte=timezone.now(),
            data_expiracao__gte=timezone.now(),
            cancelada_pelo_usuario=False
        ).exists()


    def obter_assinatura_ativa(self):
        """
        Retorna a assinatura ativa do usuário, se houver.
        """
        return self.assinaturas_premium.filter(
            status='ativa',
            data_inicio__lte=timezone.now(),
            data_expiracao__gte=timezone.now(),
            cancelada_pelo_usuario=False
        ).first()


    def eh_premium(self):
        """
        Verifica se o usuário é um Aluno Premium ativo.
        """
        if not hasattr(self, 'aluno'):
            return False

        assinatura = self.obter_assinatura_ativa()
        if not assinatura:
            return False

        return assinatura.tipo_plano.tipo_usuario == 'aluno'


    def eh_profissional_ativo(self):
        """
        Verifica se o usuário é um Profissional com assinatura Pro ativa.
        IMPORTANTE: Profissionais SÓ podem acessar o sistema se tiverem assinatura ativa.
        """
        if not hasattr(self, 'profissional'):
            return False

        assinatura = self.obter_assinatura_ativa()
        if not assinatura:
            return False

        return assinatura.tipo_plano.tipo_usuario == 'profissional'


    def precisa_assinatura(self):
        """
        Verifica se este usuário PRECISA de assinatura para usar o sistema.
        - Alunos podem ser Free, então retorna False
        - Profissionais DEVEM ter assinatura, então retorna True
        """
        return hasattr(self, 'profissional')


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


class Avaliacao(models.Model):
    """
    Armazena uma avaliação (nota e comentário) que um Aluno
    faz sobre um Profissional.
    """
    # Relacionamentos
    autor = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name="avaliacoes_feitas"
    )
    profissional_avaliado = models.ForeignKey(
        Profissional,
        on_delete=models.CASCADE,
        related_name="avaliacoes"
    )

    # Campos da Avaliação
    nota = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ['-created_at']
        # Garante que um aluno só pode avaliar um profissional uma única vez
        constraints = [
            models.UniqueConstraint(
                fields=['autor', 'profissional_avaliado'],
                name='unique_avaliacao_aluno_profissional'
            )
        ]

    def __str__(self):
        return f"Avaliação de {self.autor.usuario.first_name} para {self.profissional_avaliado.usuario.first_name}: {self.nota} estrelas"


class SolicitacaoConexao(models.Model):
    """
    Rastreia um pedido de um usuário (solicitante) para ver
    o WhatsApp de outro usuário (solicitado).
    Esta tabela também alimenta o "sininho" de notificações.
    """

    # --- Status Choices ---
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aceita', 'Aceita'),
        ('recusada', 'Recusada'),
    ]

    # --- Relacionamentos ---
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conexoes_solicitadas"
    )
    solicitado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conexoes_recebidas"
    )

    # --- Campos ---
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente'
    )

    lida_pelo_solicitante = models.BooleanField(
        default=False,
        help_text="Indica se o solicitante já viu a notificação de 'aceita'."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitação de Conexão"
        verbose_name_plural = "Solicitações de Conexão"
        ordering = ['-updated_at']
        # Garante que um usuário só pode pedir o WhatsApp de outro uma única vez
        constraints = [
            models.UniqueConstraint(
                fields=['solicitante', 'solicitado'],
                name='unique_solicitacao_conexao'
            )
        ]

    def __str__(self):
        return f"Pedido de {self.solicitante.email} para {self.solicitado.email} ({self.status})"


class TipoPlano(models.Model):
    """
    Define os tipos de planos disponíveis no sistema.
    Permite cadastrar e gerenciar os valores de cada plano.

    Exemplos:
    - Aluno Premium Mensal
    - Aluno Premium Anual
    - Profissional Pro Mensal
    - Profissional Pro Anual
    """

    # Choices para tipo de usuário
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno Premium'),
        ('profissional', 'Profissional Pro'),
    ]

    # Choices para periodicidade
    PERIODICIDADE_CHOICES = [
        ('mensal', 'Mensal'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]

    # Identificação do Plano
    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text="Ex: Aluno Premium Mensal, Profissional Pro Anual"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Identificador único para uso no código (ex: aluno-premium-mensal)"
    )

    # Características do Plano
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        help_text="Para qual tipo de usuário este plano se aplica"
    )
    periodicidade = models.CharField(
        max_length=20,
        choices=PERIODICIDADE_CHOICES,
        help_text="Com que frequência o plano é cobrado"
    )

    # Valores
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor cobrado por período"
    )
    desconto_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Desconto aplicado (ex: planos anuais com 20% de desconto)"
    )

    # Configurações
    ativo = models.BooleanField(
        default=True,
        help_text="Se False, este plano não aparecerá nas opções de compra"
    )
    destaque = models.BooleanField(
        default=False,
        help_text="Se True, este plano será destacado como 'Mais Popular' ou 'Recomendado'"
    )

    # Descrição e Benefícios
    descricao = models.TextField(
        blank=True,
        help_text="Descrição curta do plano"
    )
    ordem = models.IntegerField(
        default=0,
        help_text="Ordem de exibição (menor número aparece primeiro)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Plano"
        verbose_name_plural = "Tipos de Planos"
        ordering = ['tipo_usuario', 'ordem', 'periodicidade']

    def __str__(self):
        return self.nome

    def valor_com_desconto(self):
        """
        Calcula o valor final aplicando o desconto, se houver.
        """
        if self.desconto_percentual > 0:
            desconto = self.valor * (self.desconto_percentual / 100)
            return self.valor - desconto
        return self.valor

    def economia_mensal(self):
        """
        Para planos não mensais, calcula quanto o usuário economiza por mês
        comparado com o plano mensal equivalente.
        """
        if self.periodicidade == 'mensal':
            return 0

        try:
            # Tenta encontrar o plano mensal correspondente
            plano_mensal = TipoPlano.objects.get(
                tipo_usuario=self.tipo_usuario,
                periodicidade='mensal',
                ativo=True
            )

            # Calcula quantos meses este plano cobre
            meses = {
                'trimestral': 3,
                'semestral': 6,
                'anual': 12,
            }
            num_meses = meses.get(self.periodicidade, 1)

            # Custo total se pagasse mensalmente
            custo_mensal_total = plano_mensal.valor_com_desconto() * num_meses

            # Economia total
            economia = custo_mensal_total - self.valor_com_desconto()

            return economia
        except TipoPlano.DoesNotExist:
            return 0

    def meses_duracao(self):
        """
        Retorna quantos meses este plano dura.
        """
        meses_map = {
            'mensal': 1,
            'trimestral': 3,
            'semestral': 6,
            'anual': 12,
        }
        return meses_map.get(self.periodicidade, 1)


class AssinaturaPremium(models.Model):
    """
    Gerencia as assinaturas ativas de usuários.

    Funciona tanto para Alunos Premium quanto para Profissionais Pro.
    Cada registro representa um período de assinatura pago.

    Regras de negócio:
    - Alunos podem ter ou não ter assinatura (podem ser Free)
    - Profissionais DEVEM ter assinatura ativa para usar o sistema
    """

    # Choices para status da assinatura
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
        ('pendente', 'Pendente Pagamento'),
    ]

    # Relacionamentos
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assinaturas_premium'
    )

    tipo_plano = models.ForeignKey(
        TipoPlano,
        on_delete=models.PROTECT,
        related_name='assinaturas',
        help_text="Qual plano foi contratado"
    )

    # Status da Assinatura
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )

    # Datas
    data_inicio = models.DateTimeField(
        help_text="Quando a assinatura começou ou começará"
    )
    data_expiracao = models.DateTimeField(
        help_text="Quando a assinatura expira"
    )
    data_cancelamento = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Quando o usuário solicitou o cancelamento"
    )

    # Informações de Pagamento
    valor_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor efetivamente pago por este período"
    )
    id_transacao_externa = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID da transação no gateway de pagamento"
    )
    metodo_pagamento = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: cartao_credito, pix, boleto"
    )

    # Controle de Renovação
    renovacao_automatica = models.BooleanField(
        default=False,
        help_text="Se True, tentará renovar automaticamente ao expirar"
    )
    cancelada_pelo_usuario = models.BooleanField(
        default=False,
        help_text="Se True, o usuário não quer renovar"
    )

    # Observações
    observacoes = models.TextField(
        blank=True,
        help_text="Notas internas sobre esta assinatura"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Assinatura Premium"
        verbose_name_plural = "Assinaturas Premium"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['data_expiracao', 'status']),
        ]

    def __str__(self):
        return f"{self.usuario.email} - {self.tipo_plano.nome} - {self.status}"

    def save(self, *args, **kwargs):
        """
        Ao salvar, se não tiver data_inicio, define como agora.
        Se não tiver data_expiracao, calcula baseado no tipo de plano.
        """
        if not self.data_inicio:
            self.data_inicio = timezone.now()

        if not self.data_expiracao:
            # Calcula a data de expiração baseada no tipo de plano
            meses = self.tipo_plano.meses_duracao()
            self.data_expiracao = self.data_inicio + relativedelta(months=meses)

        # Se o valor_pago não foi definido, usa o valor do plano
        if not self.valor_pago:
            self.valor_pago = self.tipo_plano.valor_com_desconto()

        super().save(*args, **kwargs)

    def esta_ativa(self):
        """
        Verifica se a assinatura está ativa e não expirou.
        """
        agora = timezone.now()
        return (
            self.status == 'ativa' and
            self.data_inicio <= agora <= self.data_expiracao and
            not self.cancelada_pelo_usuario
        )

    def dias_restantes(self):
        """
        Retorna quantos dias faltam para a assinatura expirar.
        """
        if not self.esta_ativa():
            return 0

        delta = self.data_expiracao - timezone.now()
        return max(0, delta.days)

    def pode_renovar(self):
        """
        Verifica se esta assinatura pode ser renovada.
        """
        return (
            self.renovacao_automatica and
            not self.cancelada_pelo_usuario and
            self.status in ['ativa', 'expirada']
        )

    def renovar(self):
        """
        Cria uma nova assinatura que começa quando esta termina.
        Usado para renovações automáticas.
        """
        if not self.pode_renovar():
            return None

        # Cria nova assinatura começando quando esta expira
        nova_assinatura = AssinaturaPremium.objects.create(
            usuario=self.usuario,
            tipo_plano=self.tipo_plano,
            status='pendente',  # Será 'ativa' após confirmação de pagamento
            data_inicio=self.data_expiracao,
            renovacao_automatica=self.renovacao_automatica,
            observacoes=f"Renovação automática da assinatura #{self.id}"
        )

        return nova_assinatura

    def cancelar(self):
        """
        Cancela a assinatura (marca para não renovar).
        A assinatura continua válida até a data de expiração.
        """
        self.cancelada_pelo_usuario = True
        self.renovacao_automatica = False
        self.data_cancelamento = timezone.now()
        self.save()
