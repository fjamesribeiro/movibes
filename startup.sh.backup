#!/bin/bash
echo "🚀 Iniciando container Movibes..."

# 1. Coletar todos os arquivos estáticos (da pasta 'static', 'theme', etc)
# e copiá-los para a pasta STATIC_ROOT ('/staticfiles')
echo "🚀 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input --clear

# 2. Aplicar as migrações do banco de dados
echo "🚀 Aplicando migrações..."
python manage.py migrate --no-input

# 3. Iniciar o servidor Gunicorn
echo "🚀 Iniciando Gunicorn..."
gunicorn movibes_project.wsgi:application --bind 0.0.0.0:8000