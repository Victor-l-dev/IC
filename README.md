# Chatbot de Anamnese — Saúde Mental

Chatbot em Rasa com interface em Streamlit para coleta de anamnese.

## Como rodar (Docker)

O projeto roda em 3 containers:

| Serviço | Porta | Função |
|---|---|---|
| `streamlit` | 8501 | Interface web |
| `rasa` | 5005 | Servidor do chatbot (modelo treinado no build) |
| `actions` | 5055 | Custom actions e notificações (Telegram/e-mail) |

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e **aberto**
- PC com processador Intel/AMD (a imagem do Rasa não suporta Mac M1/M2/M3)

### Passo a passo

1. Clone o repositório e entre na pasta:
   ```bash
   git clone <url-do-repositorio>
   cd IC
   ```

2. *(Opcional)* Configure as notificações. Copie `.env.example` para `.env` e preencha os dados do Telegram e do e-mail. Sem o `.env`, o chatbot funciona normalmente, só não envia notificações.

3. Suba os containers:
   ```bash
   docker compose up -d --build
   ```

4. Acesse **http://localhost:8501**

### Observações

- **A primeira execução demora** de 5 a 10 minutos: o Docker baixa as imagens (alguns GB) e treina o modelo. As próximas são rápidas.
- **O Streamlit só sobe depois que o Rasa estiver pronto**, cerca de 30 a 60 segundos depois do comando. Se a página não abrir na hora, aguarde.
- **Use `--build` depois de alterar o código ou os dados de treino**. Sem ele, o Docker reaproveita a imagem antiga.
- **As conversas ficam em memória** e são apagadas quando os containers param.

### Comandos úteis

| Comando | O que faz |
|---|---|
| `docker compose up -d --build` | Builda e sobe tudo |
| `docker compose down` | Para e remove os containers |
| `docker compose logs -f` | Mostra os logs em tempo real |
| `docker compose logs -f rasa` | Logs só de um serviço |
| `docker compose ps` | Status dos containers |

## Como rodar sem Docker

Use o ambiente conda `chatbot` (Python 3.10, rasa 3.6.21) e rode, dentro de `chatbot/`, cada comando em um terminal:

```bash
rasa train
rasa run actions
rasa run --enable-api
streamlit run app.py
```

Nesse modo é usado o `endpoints.yml`. O `endpoints.docker.yml` é só para o Docker.
