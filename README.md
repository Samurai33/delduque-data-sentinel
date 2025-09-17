<div align="center">

![datasentinel_logo](datasentinel_logo.png)

<div align="center">
# Data Sentinel

[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red?logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Delduque Data Sentinel** é um painel interativo para análise e visualização de dados sensíveis, com integração segura ao Google Drive, desenvolvido para facilitar a tomada de decisões com foco em segurança, performance e experiência do usuário.

---

## 🚀 Features

- 🔒 Download seguro de dados sensíveis via Google Drive API
- 📊 Visualização interativa com Streamlit e Plotly
- ⚡ Performance otimizada com cache e pandas
- 🛡️ Dados protegidos por .env e credenciais externas
- 🐳 Pronto para deploy em Docker e Cloud

---

## 📦 Stack

- **Python 3.13+**
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Docker](https://www.docker.com/)

---

## ⚡ Instalação Rápida

```bash
git clone https://github.com/Samurai33/delduque-data-sentinel.git
cd delduque-data-sentinel
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
# Configure .env e credentials.json conforme instruções abaixo
streamlit run delduquedatasentinel/app.py
```

---

## 🔑 Segurança & Configuração

- **NUNCA** compartilhe `credentials.json` ou dados sensíveis publicamente.
- Adicione seu `GOOGLE_DRIVE_FILE_ID` no arquivo `.env`.
- Baixe o `credentials.json` da sua conta de serviço Google Cloud e coloque na raiz do projeto.
- Compartilhe o arquivo do Google Drive com o e-mail da conta de serviço.

---

## ☁️ Deploy com Docker

```bash
docker build -t delduque-data-sentinel .
docker run -d -p 8501:8501 --env-file .env -v $(pwd)/credentials.json:/app/credentials.json delduque-data-sentinel
```

---

## 🛠️ Contribuindo

Contribuições são bem-vindas! Siga o padrão de branch `feature/`, faça PRs claros e utilize issues para sugestões ou bugs.

1. Fork o projeto
2. Crie sua branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'feat: minha nova feature'`
4. Push: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Contato

- Autor: Samurai33
- GitHub: [Samurai33](https://github.com/Samurai33)
- Email: [samurai@n3xus.dev](mailto:samurai@n3xus.dev)

---

> Inspirado nos melhores projetos open source de 2025: [Streamlit](https://github.com/streamlit/streamlit), [Pandas](https://github.com/pandas-dev/pandas), [Plotly](https://github.com/plotly/plotly.py), [Cookiecutter Data Science](https://github.com/drivendata/cookiecutter-data-science), [FastAPI](https://github.com/tiangolo/fastapi), [Superset](https://github.com/apache/superset), [Prefect](https://github.com/PrefectHQ/prefect), [Great Expectations](https://github.com/great-expectations/great_expectations), [Airbyte](https://github.com/airbytehq/airbyte), [Dagster](https://github.com/dagster-io/dagster).
