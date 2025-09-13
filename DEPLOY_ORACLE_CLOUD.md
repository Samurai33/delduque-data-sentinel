# Instruções para deploy na Oracle Cloud (Ubuntu)

1. **Clone seu repositório privado do GitHub**

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <nome_da_pasta>
```

2. **Instale o Docker**

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Faça logout/login para ativar o grupo docker
```

3. **Build e run do container**

```bash
docker build -t data-sentinel .
docker run -d -p 8501:8501 --name data-sentinel data-sentinel
```

4. **Acesse pelo navegador**

Abra: `http://<IP_DA_SUA_VM>:8501`

---

**Dica:**
- Para atualizar, basta dar `git pull`, rebuildar e reiniciar o container.
- Para logs: `docker logs -f data-sentinel`
- Para parar: `docker stop data-sentinel`
- Para remover: `docker rm data-sentinel`
