"""
Envio de alertas e relatórios para o profissional responsável.

Configuração por variáveis de ambiente (definir antes de `rasa run actions`):

    TELEGRAM_BOT_TOKEN   token do bot criado no @BotFather
    TELEGRAM_CHAT_ID     chat do profissional que recebe as mensagens
    SMTP_HOST            servidor SMTP (ex.: smtp.gmail.com)
    SMTP_PORT            porta SMTP com STARTTLS (padrão 587)
    SMTP_USER            usuário/remetente
    SMTP_PASSWORD        senha ou senha de app
    EMAIL_PROFISSIONAL   e-mail do profissional que recebe as mensagens

Um canal sem configuração é ignorado e registrado no log.
"""

import logging
import os
import smtplib
from email.message import EmailMessage
from typing import Dict

import requests

logger = logging.getLogger(__name__)

TIMEOUT = 10


def enviar_telegram(texto: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.warning("Telegram não configurado; mensagem não enviada.")
        return False

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": texto},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        # Não logar a exceção inteira: a URL contém o token do bot
        logger.error("Falha ao enviar Telegram: %s", type(e).__name__)
        return False


def enviar_email(assunto: str, texto: str) -> bool:
    host = os.getenv("SMTP_HOST")
    usuario = os.getenv("SMTP_USER")
    senha = os.getenv("SMTP_PASSWORD")
    destinatario = os.getenv("EMAIL_PROFISSIONAL")
    if not all([host, usuario, senha, destinatario]):
        logger.warning("E-mail não configurado; mensagem não enviada.")
        return False

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = usuario
    msg["To"] = destinatario
    msg.set_content(texto)

    try:
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=TIMEOUT) as smtp:
            smtp.starttls()
            smtp.login(usuario, senha)
            smtp.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as e:
        logger.error("Falha ao enviar e-mail: %s", e)
        return False


def notificar_profissional(assunto: str, texto: str) -> Dict[str, bool]:
    """Envia a mensagem por Telegram e e-mail. Retorna o que foi entregue em cada canal."""
    resultado = {
        "telegram": enviar_telegram(f"{assunto}\n\n{texto}"),
        "email": enviar_email(assunto, texto),
    }
    if not any(resultado.values()):
        logger.error("Nenhum canal entregou a mensagem ao profissional: %s", assunto)
    return resultado
