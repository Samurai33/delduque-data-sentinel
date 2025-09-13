# Dockerfile para Data Sentinel - Delduque
# Use uma imagem oficial do Python como base
FROM python:3.13-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos de requirements e instale as dependências
COPY nathan_dashboard/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código do app
COPY nathan_dashboard/ ./nathan_dashboard/
COPY asciiart ./asciiart

# Exponha a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "nathan_dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
