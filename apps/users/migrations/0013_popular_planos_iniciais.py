# apps/planos/migrations/0002_popular_planos_iniciais.py

from django.db import migrations

# Os dados que você forneceu
planos_iniciais = [
    # Planos para Alunos Premium
    {
        'nome': 'Aluno Premium Mensal',
        'slug': 'aluno-premium-mensal',
        'tipo_usuario': 'aluno',
        'periodicidade': 'mensal',
        'valor': 29.90,
        'desconto_percentual': 0,
        'ativo': True,
        'destaque': False,
        'descricao': 'Acesso a todos os recursos Premium por 1 mês',
        'ordem': 1
    },
    {
        'nome': 'Aluno Premium Anual',
        'slug': 'aluno-premium-anual',
        'tipo_usuario': 'aluno',
        'periodicidade': 'anual',
        'valor': 299.90,
        'desconto_percentual': 0,
        'ativo': True,
        'destaque': True,
        'descricao': 'Acesso Premium por 12 meses com desconto',
        'ordem': 2
    },

    # Planos para Profissionais Pro
    {
        'nome': 'Profissional Pro Mensal',
        'slug': 'profissional-pro-mensal',
        'tipo_usuario': 'profissional',
        'periodicidade': 'mensal',
        'valor': 79.90,
        'desconto_percentual': 0,
        'ativo': True,
        'destaque': False,
        'descricao': 'Mantenha sua conta profissional ativa por 1 mês',
        'ordem': 1
    },
    {
        'nome': 'Profissional Pro Anual',
        'slug': 'profissional-pro-anual',
        'tipo_usuario': 'profissional',
        'periodicidade': 'anual',
        'valor': 799.90,
        'desconto_percentual': 0,
        'ativo': True,
        'destaque': True,
        'descricao': 'Assinatura anual com desconto especial',
        'ordem': 2
    },
]


def popular_planos(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0012_solicitacaoconexao_lida_pelo_solicitante'),
    ]

    operations = [
        migrations.RunPython(popular_planos),
    ]
