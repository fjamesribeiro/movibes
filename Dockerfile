FROM python:3.11-slim-bookworm

# Instalar dependências do sistema necessárias para
# Pillow (libjpeg) e psycopg2 (libpq-dev)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libjpeg-dev zlib1g-dev libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do projeto para o container
COPY . .

# Copiar e dar permissão ao script de inicialização
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Expor a porta 8000
EXPOSE 8000

# Definir o script de inicialização como o comando de entrada
ENTRYPOINT ["/app/startup.sh"]