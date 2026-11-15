# Servidor Rasa (NLU + diálogo). O modelo é treinado durante o build.
FROM rasa/rasa:3.6.21-full

WORKDIR /app

COPY --chown=1001:0 config.yml domain.yml credentials.yml endpoints.docker.yml ./
COPY --chown=1001:0 data/ ./data/

RUN rasa train --fixed-model-name modelo

EXPOSE 5005

CMD ["run", "--enable-api", "--endpoints", "endpoints.docker.yml", "--port", "5005"]
