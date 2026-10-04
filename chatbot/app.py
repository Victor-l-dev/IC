import streamlit as st
import requests
import uuid
import html
from datetime import datetime

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"
RASA_TRACKER_URL = "http://localhost:5005/conversations/{sender}/tracker"

st.set_page_config(
    page_title="Anamnese — Saúde Mental",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #050608;
    color: #e8e6e1;
}
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"] {
    background-color: #050608 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 760px; }

.anamnese-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid #1c2230;
    margin-bottom: 2rem;
}
.anamnese-header::after {
    content: "";
    display: block;
    width: 56px;
    height: 2px;
    margin: 1.2rem auto 0 auto;
    background: #2f6bff;
    border-radius: 2px;
}
.anamnese-titulo {
    font-family: 'Space Grotesk', 'DM Sans', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #e8e6e1;
    letter-spacing: -0.5px;
    line-height: 1.2;
    margin: 0;
}
.anamnese-header p {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 0.4rem;
    font-weight: 300;
}

/* Box fixo no canto esquerdo: status da anamnese e nome do paciente.
   Largura de até 440px, limitada ao espaço livre ao lado da conversa. */
.painel-status {
    position: fixed;
    top: 1.25rem;
    left: 1.25rem;
    z-index: 999999;
    width: min(440px, calc((100vw - 760px) / 2 - 2.5rem));
    background: #0e1117;
    border: 1px solid #1c2230;
    border-left: 2px solid #2f6bff;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
}
.painel-rotulo {
    font-size: 0.62rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 0.3rem;
}
.painel-valor {
    font-size: 0.88rem;
    font-weight: 500;
    color: #e8e6e1;
    margin-bottom: 1.1rem;
    overflow-wrap: anywhere;
}
.painel-valor:last-child { margin-bottom: 0; }
.painel-ativo .painel-status-valor { color: #7ea6ff; }
.painel-neutro .painel-status-valor { color: #94a3b8; }
.painel-risco { border-left-color: #f87171; }
.painel-risco .painel-status-valor { color: #f87171; }

/* Sem espaço ao lado da conversa: o box sobe para acima dela */
@media (max-width: 1280px) {
    .painel-status {
        position: static;
        width: auto;
        margin-bottom: 1.5rem;
    }
}

/* Respiro entre a pergunta do chatbot e os botões de resposta */
.espaco-opcoes { height: 1rem; }

.msg-bot, .msg-user {
    display: flex;
    align-items: flex-end;
    gap: 0.6rem;
    margin-bottom: 1rem;
    animation: fadeUp 0.3s ease;
}
.msg-user { flex-direction: row-reverse; }

.msg-corpo {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    max-width: 78%;
}
.msg-user .msg-corpo { align-items: flex-end; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

.bubble {
    padding: 0.85rem 1.1rem;
    border-radius: 16px;
    font-size: 0.9rem;
    line-height: 1.6;
}
.bubble-bot {
    background: #0e1117;
    color: #e8e6e1;
    border-bottom-left-radius: 4px;
    border: 1px solid #1c2230;
}
.bubble-user {
    background: #0f2257;
    color: #e6edff;
    border-bottom-right-radius: 4px;
    border: 1px solid #2f6bff;
}
.bubble-risco {
    background: #2b0d0d;
    color: #fca5a5;
    border: 1px solid #991b1b;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    line-height: 1.6;
    max-width: 78%;
}

.avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Space Grotesk', 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
}
.avatar-bot  { background: #0b1530; border: 1px solid #2f6bff; color: #7ea6ff; }
.avatar-user { background: #0e1117; border: 1px solid #1c2230; color: #94a3b8; }

.ts { font-size: 0.65rem; color: #4b5563; margin-top: 0.2rem; padding: 0 0.5rem; }
.ts-right { text-align: right; }

/* Botão secundário (Nova sessão): discreto */
.stButton > button {
    background: transparent;
    border: 1px solid #1c2230;
    color: #6b7280;
    border-radius: 8px;
    font-size: 0.78rem;
    padding: 0.4rem 1rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: #2f6bff;
    color: #c7d7ff;
    background: #0e1117;
}

/* Botões de resposta: destaque principal da tela */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: #2f6bff !important;
    border: 1px solid #2f6bff !important;
    color: #ffffff !important;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    padding: 0.8rem 0.6rem;
    min-height: 3.2rem;
    box-shadow: 0 2px 8px rgba(47, 107, 255, 0.14);
}
.stButton > button[kind="primary"] p,
.stButton > button[data-testid="stBaseButton-primary"] p {
    font-size: 0.95rem;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: #4f84ff !important;
    border-color: #4f84ff !important;
    color: #ffffff !important;
    box-shadow: 0 3px 12px rgba(47, 107, 255, 0.22);
    transform: translateY(-1px);
}
.stButton > button[kind="primary"]:focus-visible,
.stButton > button[data-testid="stBaseButton-primary"]:focus-visible {
    outline: 2px solid #c7d7ff;
    outline-offset: 2px;
}

section[data-testid="stChatInput"] textarea {
    background: #0e1117 !important;
    border: 1px solid #1c2230 !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
section[data-testid="stChatInput"] textarea:focus {
    border-color: #2f6bff !important;
    box-shadow: 0 0 0 2px rgba(47, 107, 255, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)


KEYS_SESSION = ["session_id", "messages", "nome", "risco", "encerrada", "iniciada"]

for key, default in [
    ("session_id", str(uuid.uuid4())),
    ("messages", []),
    ("nome", ""),
    ("risco", False),
    ("encerrada", False),
    ("iniciada", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def sincronizar_slots():
    """Busca no Rasa o estado da conversa (nome, risco e encerramento) para atualizar a tela."""
    try:
        resp = requests.get(
            RASA_TRACKER_URL.format(sender=st.session_state.session_id),
            timeout=10,
        )
        resp.raise_for_status()
        slots_rasa = resp.json().get("slots", {})

        st.session_state.nome = slots_rasa.get("nome") or ""
        st.session_state.risco = bool(slots_rasa.get("tem_ideacao_suicida"))
        st.session_state.encerrada = bool(slots_rasa.get("anamnese_encerrada"))
    except Exception:
        # Se o tracker não responder, mantém o que já tinha em session_state (não quebra a UI)
        pass


def enviar_para_rasa(mensagem: str) -> list[dict]:
    try:
        resp = requests.post(
            RASA_URL,
            json={"sender": st.session_state.session_id, "message": mensagem},
            timeout=30,
        )
        resp.raise_for_status()
        return [
            {"text": item["text"], "buttons": item.get("buttons") or []}
            for item in resp.json() if item.get("text")
        ]
    except requests.exceptions.ConnectionError:
        return [{"text": "Não foi possível conectar ao servidor Rasa. Verifique se ele está rodando em localhost:5005.", "buttons": []}]
    except Exception as e:
        return [{"text": f"Erro inesperado: {e}", "buttons": []}]


def processar_respostas_bot(respostas: list[dict]):
    for r in respostas:
        adicionar_mensagem("bot", r["text"], botoes=r["buttons"])


def adicionar_mensagem(role: str, texto: str, botoes: list | None = None):
    st.session_state.messages.append({
        "role": role,
        "text": texto,
        "ts": datetime.now().strftime("%H:%M"),
        "botoes": botoes or [],
    })


def responder(texto_exibido: str, mensagem: str):
    """Registra a resposta do paciente, envia ao Rasa e atualiza a tela."""
    adicionar_mensagem("user", texto_exibido)
    processar_respostas_bot(enviar_para_rasa(mensagem))
    sincronizar_slots()
    st.rerun()


def renderizar_mensagens():
    # Avatar do paciente: inicial do nome, quando já informado
    inicial = html.escape(st.session_state.nome[:1].upper()) or "•"

    for msg in st.session_state.messages:
        texto_safe = html.escape(msg["text"])
        ts = msg.get("ts", "")

        if msg["role"] == "bot":
            st.markdown(f"""
            <div class="msg-bot">
                <div class="avatar avatar-bot">A</div>
                <div class="msg-corpo">
                    <div class="bubble bubble-bot">{texto_safe}</div>
                    <div class="ts">{ts}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-user">
                <div class="avatar avatar-user">{inicial}</div>
                <div class="msg-corpo">
                    <div class="bubble bubble-user">{texto_safe}</div>
                    <div class="ts ts-right">{ts}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def renderizar_painel_status():
    if st.session_state.risco:
        classe, status = "painel-risco", "⚠ Alerta de risco"
    elif st.session_state.encerrada:
        classe, status = "painel-neutro", "✓ Encerrada"
    elif st.session_state.iniciada:
        classe, status = "painel-ativo", "● Em andamento"
    else:
        classe, status = "painel-neutro", "○ Aguardando início"

    nome = html.escape(st.session_state.nome) or "—"
    st.markdown(f"""
    <div class="painel-status {classe}">
        <div class="painel-rotulo">Status da anamnese</div>
        <div class="painel-valor painel-status-valor">{status}</div>
        <div class="painel-rotulo">Paciente</div>
        <div class="painel-valor">{nome}</div>
    </div>
    """, unsafe_allow_html=True)


if not st.session_state.iniciada:
    respostas = enviar_para_rasa("quero começar")
    processar_respostas_bot(respostas)
    sincronizar_slots()
    st.session_state.iniciada = True

st.markdown("""
<div class="anamnese-header">
    <div class="anamnese-titulo">Anamnese Clínica</div>
    <p>Coleta automatizada de histórico em saúde mental</p>
</div>
""", unsafe_allow_html=True)

renderizar_painel_status()

renderizar_mensagens()

ultima = st.session_state.messages[-1] if st.session_state.messages else None
botoes = ultima["botoes"] if ultima and ultima["role"] == "bot" else []

if st.session_state.encerrada:
    st.info("A anamnese foi encerrada. Use o botão abaixo para iniciar uma nova sessão.")
elif botoes:
    # Pergunta com opções fixas: o paciente responde só pelos botões
    st.markdown('<div class="espaco-opcoes"></div>', unsafe_allow_html=True)
    colunas = st.columns(len(botoes))
    for i, (coluna, botao) in enumerate(zip(colunas, botoes)):
        with coluna:
            if st.button(botao["title"], key=f"opcao_{len(st.session_state.messages)}_{i}", type="primary", use_container_width=True):
                responder(botao["title"], botao["payload"])
else:
    user_input = st.chat_input("Digite sua resposta...")
    if user_input:
        texto = user_input.strip()
        responder(texto, texto)

st.markdown("<br>", unsafe_allow_html=True)
_, col_b, _ = st.columns([3, 2, 3])
with col_b:
    if st.button("↺ Nova sessão", use_container_width=True):
        for key in KEYS_SESSION:
            st.session_state.pop(key, None)
        st.rerun()