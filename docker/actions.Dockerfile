# Servidor de custom actions (rasa-sdk).
FROM rasa/rasa-sdk:3.6.2

WORKDIR /app

# requests é usado em actions/notificacoes.py (Telegram)
USER root
RUN pip install --no-cache-dir requests==2.34.2
USER 1001

COPY --chown=1001:0 actions/ ./actions/

EXPOSE 5055

CMD ["start", "--actions", "actions", "--port", "5055"]
