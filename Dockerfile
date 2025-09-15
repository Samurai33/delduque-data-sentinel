# Dockerfile para Delduque Data Sentinel
# Use uma imagem oficial do Python como base
FROM python:3.13-slim

# Defina o diretório de trabalho
WORKDIR /app

# Instale compiladores e dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copie os arquivos de requirements e instale as dependências
COPY delduquedatasentinel/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código do app
COPY delduquedatasentinel/ ./delduquedatasentinel/
COPY asciiart ./asciiart

# Exponha a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "delduquedatasentinel/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
