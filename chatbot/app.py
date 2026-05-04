import streamlit as st
import requests
import uuid
import time
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

st.set_page_config(
    page_title="Anamnese — Saúde Mental",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILO
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

/* Reset e base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0f1117;
    color: #e8e6e1;
}

/* Esconde elementos padrão do Streamlit */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 760px; }

/* Header */
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

/* Badge de status */
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
.status-ativo { background: #0d2b1f; color: #34d399; border: 1px solid #065f46; }
.status-risco { background: #2b0d0d; color: #f87171; border: 1px solid #991b1b; }
.status-encerrado { background: #1a1e2e; color: #94a3b8; border: 1px solid #334155; }

/* Área de chat */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1.5rem 0;
    min-height: 420px;
    max-height: 520px;
    overflow-y: auto;
}

/* Balões de mensagem */
.msg-bot, .msg-user {
    display: flex;
    align-items: flex-end;
    gap: 0.6rem;
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

/* Alerta de risco */
.bubble-risco {
    background: #2b0d0d;
    color: #fca5a5;
    border: 1px solid #991b1b;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* Avatar */
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
.avatar-bot { background: #1e2a4a; border: 1px solid #2d3d6b; }
.avatar-user { background: #0d2b1f; border: 1px solid #166534; }

/* Timestamp */
.ts {
    font-size: 0.65rem;
    color: #4b5563;
    margin-top: 0.2rem;
    padding: 0 0.5rem;
}
.ts-right { text-align: right; }

/* Input area */
.input-area {
    margin-top: 1.5rem;
    border-top: 1px solid #1e2130;
    padding-top: 1.2rem;
}

/* Slots coletados */
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

/* Typing indicator */
.typing {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: 0.6rem 0.8rem;
}
.typing span {
    width: 7px; height: 7px;
    background: #4b5563;
    border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-6px); }
}

/* Botão de reiniciar */
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

/* Input text */
.stTextInput > div > div > input {
    background: #131720 !important;
    border: 1px solid #1e2130 !important;
    color: #e8e6e1 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2d3d6b !important;
    box-shadow: 0 0 0 2px rgba(45, 61, 107, 0.3) !important;
}
.stTextInput > label { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "slots" not in st.session_state:
    st.session_state.slots = {}

if "risco" not in st.session_state:
    st.session_state.risco = False

if "encerrada" not in st.session_state:
    st.session_state.encerrada = False

if "iniciada" not in st.session_state:
    st.session_state.iniciada = False


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES
# ─────────────────────────────────────────────────────────────────────────────

PALAVRAS_RISCO = [
    "machucar", "morrer", "suicídio", "suicidio", "não quero viver",
    "nao quero viver", "desaparecer", "seria melhor morrer",
    "não estar aqui", "nao estar aqui", "pensamentos de suicídio",
    "gostaria de morrer", "acabar com tudo", "protocolo_risco"
]

SLOTS_LABELS = {
    "nome": "Nome",
    "idade": "Idade",
    "sexo": "Sexo",
    "queixa_principal": "Queixa principal",
    "duracao_sintomas": "Duração dos sintomas",
    "intensidade_sintomas": "Intensidade",
    "medicacao_atual": "Medicação atual",
    "tem_ideacao_suicida": "Ideação suicida",
    "tem_tratamento_anterior": "Tratamento anterior",
}


def enviar_para_rasa(mensagem: str) -> list[str]:
    """Envia mensagem ao Rasa e retorna lista de respostas."""
    try:
        payload = {
            "sender": st.session_state.session_id,
            "message": mensagem,
        }
        resp = requests.post(RASA_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [item.get("text", "") for item in data if item.get("text")]
    except requests.exceptions.ConnectionError:
        return ["Não foi possível conectar ao servidor Rasa. Verifique se ele está rodando em localhost:5005."]
    except Exception as e:
        return [f"Erro inesperado: {str(e)}"]


def detectar_risco(texto: str) -> bool:
    texto_lower = texto.lower()
    return any(p in texto_lower for p in PALAVRAS_RISCO)


def extrair_slots_da_resposta(respostas: list[str]):
    """Atualiza slots inferidos a partir das respostas do bot."""
    for r in respostas:
        if "protocolo_risco" in r.lower() or detectar_risco(r):
            st.session_state.risco = True
            st.session_state.slots["tem_ideacao_suicida"] = True
        if "encerradas" in r.lower() or "foram registradas" in r.lower():
            st.session_state.encerrada = True


def ts_agora() -> str:
    return datetime.now().strftime("%H:%M")


def renderizar_mensagens():
    for msg in st.session_state.messages:
        role = msg["role"]
        texto = msg["text"]
        ts = msg.get("ts", "")
        is_risco = msg.get("risco", False)

        if role == "bot":
            if is_risco:
                st.markdown(f"""
                <div class="msg-bot">
                    <div class="avatar avatar-bot">🧠</div>
                    <div>
                        <div class="bubble bubble-risco">{texto}</div>
                        <div class="ts">{ts}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-bot">
                    <div class="avatar avatar-bot">🧠</div>
                    <div>
                        <div class="bubble bubble-bot">{texto}</div>
                        <div class="ts">{ts}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-user">
                <div class="avatar avatar-user">👤</div>
                <div>
                    <div class="bubble bubble-user">{texto}</div>
                    <div class="ts ts-right">{ts}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def adicionar_mensagem(role: str, texto: str, risco: bool = False):
    st.session_state.messages.append({
        "role": role,
        "text": texto,
        "ts": ts_agora(),
        "risco": risco,
    })


def iniciar_conversa():
    respostas = enviar_para_rasa("quero começar")
    for r in respostas:
        adicionar_mensagem("bot", r)
    st.session_state.iniciada = True


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="anamnese-header">
    <h1>Anamnese Clínica</h1>
    <p>Coleta automatizada de histórico em saúde mental</p>
</div>
""", unsafe_allow_html=True)

# Status badge
if st.session_state.risco:
    st.markdown('<div class="status-badge status-risco">⚠ Alerta de risco identificado</div>', unsafe_allow_html=True)
elif st.session_state.encerrada:
    st.markdown('<div class="status-badge status-encerrado">✓ Anamnese encerrada</div>', unsafe_allow_html=True)
elif st.session_state.iniciada:
    st.markdown('<div class="status-badge status-ativo">● Em andamento</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-badge status-encerrado">○ Aguardando início</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INICIAR AUTOMATICAMENTE
# ─────────────────────────────────────────────────────────────────────────────

if not st.session_state.iniciada:
    iniciar_conversa()
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ÁREA DE CHAT
# ─────────────────────────────────────────────────────────────────────────────

renderizar_mensagens()


# ─────────────────────────────────────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="input-area">', unsafe_allow_html=True)

if not st.session_state.encerrada:
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                label="",
                placeholder="Digite sua resposta...",
                key="input_field",
            )
        with col2:
            submitted = st.form_submit_button("Enviar", use_container_width=True)

        if submitted and user_input.strip():
            texto = user_input.strip()

            # Adiciona mensagem do usuário
            adicionar_mensagem("user", texto)

            # Detecta risco na mensagem do usuário
            if detectar_risco(texto):
                st.session_state.risco = True
                st.session_state.slots["tem_ideacao_suicida"] = True

            # Envia ao Rasa
            respostas = enviar_para_rasa(texto)
            extrair_slots_da_resposta(respostas)

            for r in respostas:
                is_risco = detectar_risco(r)
                adicionar_mensagem("bot", r, risco=is_risco)

            st.rerun()
else:
    st.info("A anamnese foi encerrada. Use o botão abaixo para iniciar uma nova sessão.")

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAINEL DE SLOTS COLETADOS
# ─────────────────────────────────────────────────────────────────────────────

slots_visiveis = {k: v for k, v in st.session_state.slots.items() if v is not None}

if slots_visiveis:
    st.markdown('<div class="slots-panel">', unsafe_allow_html=True)
    st.markdown('<h4>Dados coletados até agora</h4>', unsafe_allow_html=True)
    for key, val in slots_visiveis.items():
        label = SLOTS_LABELS.get(key, key)
        if isinstance(val, bool):
            val_str = "Sim" if val else "Não"
        else:
            val_str = str(val)
        st.markdown(f"""
        <div class="slot-row">
            <span class="slot-key">{label}</span>
            <span class="slot-val">{val_str}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RODAPÉ — NOVA SESSÃO
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
col_a, col_b, col_c = st.columns([3, 2, 3])
with col_b:
    if st.button("↺ Nova sessão", use_container_width=True):
        for key in ["session_id", "messages", "slots", "risco", "encerrada", "iniciada"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
