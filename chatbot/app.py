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
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0f1117;
    color: #e8e6e1;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 760px; }

.anamnese-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid #1e2130;
    margin-bottom: 2rem;
}
.anamnese-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #e8e6e1;
    letter-spacing: -0.5px;
    margin: 0;
}
.anamnese-header p {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 0.4rem;
    font-weight: 300;
}

.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.status-ativo     { background: #0d2b1f; color: #34d399; border: 1px solid #065f46; }
.status-risco     { background: #2b0d0d; color: #f87171; border: 1px solid #991b1b; }
.status-encerrado { background: #1a1e2e; color: #94a3b8; border: 1px solid #334155; }

.msg-bot, .msg-user {
    display: flex;
    align-items: flex-end;
    gap: 0.6rem;
    margin-bottom: 1rem;
    animation: fadeUp 0.3s ease;
}
.msg-user { flex-direction: row-reverse; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

.bubble {
    max-width: 78%;
    padding: 0.85rem 1.1rem;
    border-radius: 16px;
    font-size: 0.9rem;
    line-height: 1.6;
}
.bubble-bot {
    background: #1a1e2e;
    color: #e8e6e1;
    border-bottom-left-radius: 4px;
    border: 1px solid #252a3d;
}
.bubble-user {
    background: #1a3a2e;
    color: #d1fae5;
    border-bottom-right-radius: 4px;
    border: 1px solid #166534;
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
    font-size: 0.85rem;
    flex-shrink: 0;
}
.avatar-bot  { background: #1e2a4a; border: 1px solid #2d3d6b; }
.avatar-user { background: #0d2b1f; border: 1px solid #166534; }

.ts { font-size: 0.65rem; color: #4b5563; margin-top: 0.2rem; padding: 0 0.5rem; }
.ts-right { text-align: right; }

.slots-panel {
    background: #131720;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-top: 1.5rem;
}
.slots-panel h4 {
    font-family: 'DM Serif Display', serif;
    font-size: 0.95rem;
    color: #94a3b8;
    margin: 0 0 0.8rem 0;
    letter-spacing: 0.02em;
}
.slot-row {
    display: flex;
    justify-content: space-between;
    padding: 0.35rem 0;
    border-bottom: 1px solid #1a1e2e;
    font-size: 0.8rem;
}
.slot-row:last-child { border-bottom: none; }
.slot-key { color: #6b7280; }
.slot-val { color: #e8e6e1; font-weight: 500; }

.stButton > button {
    background: transparent;
    border: 1px solid #1e2130;
    color: #6b7280;
    border-radius: 8px;
    font-size: 0.78rem;
    padding: 0.4rem 1rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: #374151;
    color: #9ca3af;
    background: #1a1e2e;
}

section[data-testid="stChatInput"] textarea {
    background: #131720 !important;
    border: 1px solid #1e2130 !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
section[data-testid="stChatInput"] textarea:focus {
    border-color: #2d3d6b !important;
    box-shadow: 0 0 0 2px rgba(45, 61, 107, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)


# Só os dados de identificação aparecem para o paciente.
# Scores e respostas ficam restritos ao profissional.
SLOTS_LABELS = {
    "nome": "Nome",
    "idade": "Idade",
    "sexo": "Sexo",
}

KEYS_SESSION = ["session_id", "messages", "slots", "risco", "encerrada", "iniciada"]

for key, default in [
    ("session_id", str(uuid.uuid4())),
    ("messages", []),
    ("slots", {}),
    ("risco", False),
    ("encerrada", False),
    ("iniciada", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def sincronizar_slots():
    """Busca os slots reais da conversa direto do Rasa e atualiza st.session_state.slots."""
    try:
        resp = requests.get(
            RASA_TRACKER_URL.format(sender=st.session_state.session_id),
            timeout=10,
        )
        resp.raise_for_status()
        slots_rasa = resp.json().get("slots", {})

        for chave in SLOTS_LABELS:
            if slots_rasa.get(chave) is not None:
                st.session_state.slots[chave] = slots_rasa[chave]

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
    for msg in st.session_state.messages:
        texto_safe = html.escape(msg["text"])
        ts = msg.get("ts", "")

        if msg["role"] == "bot":
            st.markdown(f"""
            <div class="msg-bot">
                <div class="avatar avatar-bot">🧠</div>
                <div>
                    <div class="bubble bubble-bot">{texto_safe}</div>
                    <div class="ts">{ts}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-user">
                <div class="avatar avatar-user">👤</div>
                <div>
                    <div class="bubble bubble-user">{texto_safe}</div>
                    <div class="ts ts-right">{ts}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


st.markdown("""
<div class="anamnese-header">
    <h1>Anamnese Clínica</h1>
    <p>Coleta automatizada de histórico em saúde mental</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.risco:
    st.markdown('<div class="status-badge status-risco">⚠ Alerta de risco identificado</div>', unsafe_allow_html=True)
elif st.session_state.encerrada:
    st.markdown('<div class="status-badge status-encerrado">✓ Anamnese encerrada</div>', unsafe_allow_html=True)
elif st.session_state.iniciada:
    st.markdown('<div class="status-badge status-ativo">● Em andamento</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-badge status-encerrado">○ Aguardando início</div>', unsafe_allow_html=True)

if not st.session_state.iniciada:
    respostas = enviar_para_rasa("quero começar")
    processar_respostas_bot(respostas)
    sincronizar_slots()
    st.session_state.iniciada = True

renderizar_mensagens()

ultima = st.session_state.messages[-1] if st.session_state.messages else None
botoes = ultima["botoes"] if ultima and ultima["role"] == "bot" else []

if st.session_state.encerrada:
    st.info("A anamnese foi encerrada. Use o botão abaixo para iniciar uma nova sessão.")
elif botoes:
    # Pergunta com opções fixas: o paciente responde só pelos botões
    colunas = st.columns(len(botoes))
    for i, (coluna, botao) in enumerate(zip(colunas, botoes)):
        with coluna:
            if st.button(botao["title"], key=f"opcao_{len(st.session_state.messages)}_{i}", use_container_width=True):
                responder(botao["title"], botao["payload"])
else:
    user_input = st.chat_input("Digite sua resposta...")
    if user_input:
        texto = user_input.strip()
        responder(texto, texto)

slots_visiveis = {k: v for k, v in st.session_state.slots.items() if v is not None}
if slots_visiveis:
    st.markdown('<div class="slots-panel"><h4>Dados coletados até agora</h4>', unsafe_allow_html=True)
    for key, val in slots_visiveis.items():
        label = SLOTS_LABELS.get(key, key)
        val_str = ("Sim" if val else "Não") if isinstance(val, bool) else html.escape(str(val))
        st.markdown(f"""
        <div class="slot-row">
            <span class="slot-key">{label}</span>
            <span class="slot-val">{val_str}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
_, col_b, _ = st.columns([3, 2, 3])
with col_b:
    if st.button("↺ Nova sessão", use_container_width=True):
        for key in KEYS_SESSION:
            st.session_state.pop(key, None)
        st.rerun()