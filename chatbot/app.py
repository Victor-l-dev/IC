import streamlit as st
import requests
import uuid
import html
import random
from datetime import datetime

from streamlit.errors import StreamlitAPIException

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
/* Layout em duas colunas: box de status à esquerda, conversa à direita.
   O conjunto é centralizado na tela; o padding esquerdo reserva a coluna do box. */
:root {
    --largura-box: 400px;
    --vao-colunas: 2.5rem;
    /* Altura da conversa e da coluna lateral, para a página caber na tela.
       Os 25rem são a altura somada do que fica fora da conversa
       (cabeçalho e a linha das opções de resposta). */
    --altura-conversa: max(14rem, calc(100vh - 25rem));
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: calc(1rem + var(--largura-box) + var(--vao-colunas));
    padding-right: 1rem;
    max-width: calc(760px + var(--largura-box) + var(--vao-colunas));
    /* Mantém a conversa acima da camada de partículas */
    position: relative;
    z-index: 1;
    background: transparent !important;
}
/* Campo de digitação alinhado à coluna da conversa */
[data-testid="stBottomBlockContainer"] {
    padding-left: calc(1rem + var(--largura-box) + var(--vao-colunas)) !important;
    padding-right: 1rem !important;
    max-width: calc(760px + var(--largura-box) + var(--vao-colunas)) !important;
}

/* Fundo: partículas azuis discretas subindo devagar, atrás da conversa */
.particulas {
    position: fixed;
    inset: 0;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
}
.particulas span {
    position: absolute;
    bottom: -10px;
    border-radius: 50%;
    background: #2f6bff;
    opacity: 0;
    animation: flutuar linear infinite;
}
@keyframes flutuar {
    0%   { transform: translate(0, 0); opacity: 0; }
    10%  { opacity: var(--opacidade); }
    90%  { opacity: var(--opacidade); }
    100% { transform: translate(var(--desvio), -105vh); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .particulas { display: none; }
}

.anamnese-header {
    position: relative;
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    margin-bottom: 2rem;
    /* O cabeçalho ocupa as duas colunas, com o título centralizado sobre o conjunto */
    margin-left: calc(-1 * (var(--largura-box) + var(--vao-colunas)));
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
    font-size: 2.3rem;
    font-weight: 700;
    color: #e8e6e1;
    letter-spacing: -0.5px;
    line-height: 1.2;
    margin: 0;
}
.anamnese-header p {
    font-size: 1rem;
    color: #6b7280;
    margin-top: 0.4rem;
    font-weight: 300;
}

/* Coluna da esquerda: dois cartões empilhados, com a mesma altura da conversa.
   Fica presa ao cabeçalho e começa na altura do topo da conversa:
   100% = base do cabeçalho; 2rem = distância medida na tela entre a base
   do cabeçalho e o topo da conversa. */
.coluna-lateral {
    position: absolute;
    top: calc(100% + 2rem);
    left: 0;
    width: var(--largura-box);
    height: var(--altura-conversa);
    display: flex;
    flex-direction: column;
    gap: 1rem;
    text-align: left;
}
.painel-status, .painel-ajuda {
    box-sizing: border-box;
    background: #0e1117;
    border: 1px solid #1c2230;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
}
/* Cartão de cima: status, paciente, progresso e aviso */
.painel-status { border-left: 2px solid #2f6bff; }
/* Cartão de baixo: ocupa a altura que sobra até a base da conversa */
.painel-ajuda {
    flex: 1;
    min-height: 0;
    overflow: hidden;
}
.painel-ajuda ul {
    margin: 0.5rem 0 0 0;
    padding: 0;
    list-style: none;
}
.painel-ajuda li {
    position: relative;
    margin: 0 0 0.6rem 0;
    padding-left: 1rem;
    font-size: 0.92rem;
    line-height: 1.5;
    color: #c5c9d3;
}
.painel-ajuda li::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0.6em;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #2f6bff;
}
.painel-rotulo {
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 0.3rem;
}
.painel-valor {
    font-size: 1.02rem;
    font-weight: 500;
    color: #e8e6e1;
    margin-bottom: 1.1rem;
    overflow-wrap: anywhere;
}
.painel-valor:last-child { margin-bottom: 0; }
.painel-linha {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}
.painel-contagem { color: #7ea6ff; letter-spacing: 0.04em; }

/* Barra de progresso do questionário */
.painel-barra {
    height: 6px;
    margin-top: 0.35rem;
    background: #1c2230;
    border-radius: 999px;
    overflow: hidden;
}
.painel-barra-preenchida {
    position: relative;
    height: 100%;
    background: #2f6bff;
    border-radius: 999px;
    overflow: hidden;
    transition: width 0.6s ease;
}
/* Reflexo que percorre a parte preenchida */
.painel-barra-preenchida::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.45), transparent);
    transform: translateX(-100%);
    animation: reflexo 2.4s ease-in-out infinite;
}
@keyframes reflexo {
    to { transform: translateX(100%); }
}
@media (prefers-reduced-motion: reduce) {
    .painel-barra-preenchida::after { animation: none; }
}

.painel-aviso {
    margin-top: 1.1rem;
    padding-top: 0.9rem;
    border-top: 1px solid #1c2230;
    font-size: 0.78rem;
    line-height: 1.5;
    color: #6b7280;
}
.painel-ativo .painel-status-valor { color: #7ea6ff; }
.painel-neutro .painel-status-valor { color: #94a3b8; }
.painel-risco { border-left-color: #f87171; }
.painel-risco .painel-status-valor { color: #f87171; }

/* Botão de reiniciar: abaixo dos cartões, na mesma linha das opções de resposta
   (1rem = espaço que o Streamlit põe entre a conversa e as opções). */
.botao-reiniciar {
    position: absolute;
    top: calc(100% + 1rem);
    left: 50%;
    transform: translateX(-50%);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    min-height: 3.45rem; /* mesma altura dos botões de resposta */
    padding: 0 1.6rem;
    white-space: nowrap;
    background: transparent;
    border: 1px solid #1c2230;
    border-radius: 10px;
    font-size: 0.95rem;
    color: #8b93a5 !important;
    text-decoration: none !important;
    transition: all 0.2s;
}
.botao-reiniciar:hover {
    border-color: #2f6bff;
    color: #c7d7ff !important;
    background: #0e1117;
}

/* Tela estreita: volta a uma coluna, com os cartões abaixo do subtítulo */
@media (max-width: 1260px) {
    .block-container {
        padding-left: 1rem;
        max-width: 760px;
    }
    [data-testid="stBottomBlockContainer"] {
        padding-left: 1rem !important;
        max-width: 760px !important;
    }
    .anamnese-header { margin-left: 0; }
    .coluna-lateral {
        position: static;
        width: auto;
        height: auto;
        margin-top: 1.5rem;
    }
    .botao-reiniciar {
        position: static;
        transform: none;
        align-self: center;
    }
}

/* Coluna da direita: cartão da conversa, com altura fixa e rolagem própria,
   para a página não passar da altura da tela. */
.conversa {
    display: flex;
    flex-direction: column-reverse; /* mantém a rolagem presa na última mensagem */
    box-sizing: border-box;
    height: var(--altura-conversa);
    /* Mesmo vão que há entre os cartões da esquerda e o botão de reiniciar
       (medido na tela: o Streamlit deixava só 3px aqui) */
    margin-bottom: 15px;
    overflow-y: auto;
    padding: 1.1rem 0.9rem 0.2rem 1.1rem;
    background: rgba(10, 12, 17, 0.6);
    border: 1px solid #1c2230;
    border-radius: 12px;
    scrollbar-width: thin;
    scrollbar-color: #1c2230 transparent;
}
/* Com poucas mensagens, elas ficam no topo do cartão */
.conversa > div { margin-bottom: auto; }
.conversa::-webkit-scrollbar { width: 6px; }
.conversa::-webkit-scrollbar-thumb { background: #1c2230; border-radius: 3px; }
.conversa::-webkit-scrollbar-thumb:hover { background: #2f6bff; }

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
    font-size: 1.05rem;
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
    font-size: 1.02rem;
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
    font-size: 0.9rem;
    font-weight: 700;
    flex-shrink: 0;
}
.avatar-bot  { background: #0b1530; border: 1px solid #2f6bff; color: #7ea6ff; }
.avatar-user { background: #0e1117; border: 1px solid #1c2230; color: #94a3b8; }

.ts { font-size: 0.75rem; color: #4b5563; margin-top: 0.2rem; padding: 0 0.5rem; }
.ts-right { text-align: right; }

/* Base dos botões do Streamlit */
.stButton > button {
    background: transparent;
    border: 1px solid #1c2230;
    color: #6b7280;
    border-radius: 8px;
    font-size: 0.9rem;
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
    font-size: 1.08rem;
    font-weight: 600;
    padding: 0.8rem 0.6rem;
    min-height: 3.2rem;
    box-shadow: 0 2px 8px rgba(47, 107, 255, 0.14);
}
.stButton > button[kind="primary"] p,
.stButton > button[data-testid="stBaseButton-primary"] p {
    font-size: 1.08rem;
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

/* Campo de digitação: mesma altura e mesmo arredondamento do botão de reiniciar */
[data-testid="stChatInput"] > div {
    min-height: 3.45rem;
    align-items: center;
    background: #0e1117 !important;
    border: 1px solid #1c2230 !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #2f6bff !important;
    box-shadow: 0 0 0 2px rgba(47, 107, 255, 0.3) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.05rem !important;
}
</style>
""", unsafe_allow_html=True)


# Total de perguntas do questionário, usado na barra de progresso.
# Manter igual ao tamanho da lista PERGUNTAS em actions/actions.py.
TOTAL_PERGUNTAS = 8

for key, default in [
    ("session_id", str(uuid.uuid4())),
    ("messages", []),
    ("nome", ""),
    ("respondidas", 0),
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
        st.session_state.respondidas = int(slots_rasa.get("indice_pergunta") or 0)
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

    blocos = []
    for msg in st.session_state.messages:
        texto_safe = html.escape(msg["text"])
        ts = msg.get("ts", "")

        if msg["role"] == "bot":
            blocos.append(
                '<div class="msg-bot">'
                '<div class="avatar avatar-bot">A</div>'
                '<div class="msg-corpo">'
                f'<div class="bubble bubble-bot">{texto_safe}</div>'
                f'<div class="ts">{ts}</div>'
                '</div></div>'
            )
        else:
            blocos.append(
                '<div class="msg-user">'
                f'<div class="avatar avatar-user">{inicial}</div>'
                '<div class="msg-corpo">'
                f'<div class="bubble bubble-user">{texto_safe}</div>'
                f'<div class="ts ts-right">{ts}</div>'
                '</div></div>'
            )

    # Um único bloco rolável; a div interna mantém as mensagens na ordem normal
    st.markdown(
        f'<div class="conversa"><div>{"".join(blocos)}</div></div>',
        unsafe_allow_html=True,
    )


def html_painel_status() -> str:
    if st.session_state.risco:
        classe, status = "painel-risco", "⚠ Alerta de risco"
    elif st.session_state.encerrada:
        classe, status = "painel-neutro", "✓ Encerrada"
    elif st.session_state.iniciada:
        classe, status = "painel-ativo", "● Em andamento"
    else:
        classe, status = "painel-neutro", "○ Aguardando início"

    nome = html.escape(st.session_state.nome) or "—"
    respondidas = min(st.session_state.respondidas, TOTAL_PERGUNTAS)
    percentual = round(100 * respondidas / TOTAL_PERGUNTAS)
    return (
        '<div class="coluna-lateral">'
        f'<div class="painel-status {classe}">'
        '<div class="painel-rotulo">Status da anamnese</div>'
        f'<div class="painel-valor painel-status-valor">{status}</div>'
        '<div class="painel-rotulo">Paciente</div>'
        f'<div class="painel-valor">{nome}</div>'
        '<div class="painel-rotulo painel-linha">'
        f'<span>Progresso</span><span class="painel-contagem">{respondidas} de {TOTAL_PERGUNTAS}</span>'
        '</div>'
        f'<div class="painel-barra"><div class="painel-barra-preenchida" style="width:{percentual}%"></div></div>'
        '<div class="painel-aviso">Suas respostas são enviadas apenas ao profissional responsável.</div>'
        '</div>'
        '<div class="painel-ajuda">'
        '<div class="painel-rotulo">Como responder</div>'
        '<ul>'
        '<li>Escolha a opção que melhor descreve as últimas duas semanas.</li>'
        '<li>Não existe resposta certa ou errada.</li>'
        '<li>Leva cerca de 2 minutos.</li>'
        '</ul>'
        '</div>'
        # Recarregar a página abre uma sessão nova do Streamlit, com outro session_id
        '<a class="botao-reiniciar" href="?" target="_self">↺ Reiniciar sessão</a>'
        '</div>'
    )


def html_particulas(quantidade: int = 14) -> str:
    """Camada de fundo com partículas. A semente fixa mantém o mesmo HTML a cada
    rerun do Streamlit, então a animação não reinicia quando o paciente responde."""
    sorteio = random.Random(7)
    regras = []
    for i in range(1, quantidade + 1):
        tamanho = sorteio.choice([2, 2, 3, 3, 4])
        duracao = sorteio.randint(22, 48)
        regras.append(
            f".particulas span:nth-child({i}){{"
            f"left:{sorteio.randint(1, 99)}%;"
            f"width:{tamanho}px;height:{tamanho}px;"
            f"--opacidade:{sorteio.uniform(0.08, 0.22):.2f};"
            f"--desvio:{sorteio.randint(-40, 40)}px;"
            f"animation-duration:{duracao}s;"
            # atraso negativo: a tela já abre com as partículas espalhadas
            f"animation-delay:-{sorteio.randint(0, duracao)}s;}}"
        )
    return f'<style>{"".join(regras)}</style><div class="particulas">{"<span></span>" * quantidade}</div>'


if not st.session_state.iniciada:
    respostas = enviar_para_rasa("quero começar")
    processar_respostas_bot(respostas)
    sincronizar_slots()
    st.session_state.iniciada = True

st.markdown(f"""
{html_particulas()}
<div class="anamnese-header">
    <div class="anamnese-titulo">Anamnese Clínica</div>
    <p>Coleta automatizada de histórico em saúde mental</p>
    {html_painel_status()}
</div>
""", unsafe_allow_html=True)

renderizar_mensagens()

ultima = st.session_state.messages[-1] if st.session_state.messages else None
botoes = ultima["botoes"] if ultima and ultima["role"] == "bot" else []

if st.session_state.encerrada:
    st.info("A anamnese foi encerrada. Use o botão “Reiniciar sessão” para começar outra.")
elif botoes:
    # Pergunta com opções fixas: o paciente responde só pelos botões
    colunas = st.columns(len(botoes))
    for i, (coluna, botao) in enumerate(zip(colunas, botoes)):
        with coluna:
            if st.button(botao["title"], key=f"opcao_{len(st.session_state.messages)}_{i}", type="primary", use_container_width=True):
                responder(botao["title"], botao["payload"])
else:
    # Dentro de um container o campo fica logo abaixo da conversa, na mesma linha
    # do botão de reiniciar. Versões antigas do Streamlit só aceitam o campo
    # preso no rodapé da janela.
    try:
        with st.container():
            user_input = st.chat_input("Digite sua resposta...")
    except StreamlitAPIException:
        user_input = st.chat_input("Digite sua resposta...")
    if user_input:
        texto = user_input.strip()
        responder(texto, texto)