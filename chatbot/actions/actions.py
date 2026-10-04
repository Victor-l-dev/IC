import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .notificacoes import notificar_profissional


# Escala fixa de resposta: (rótulo do botão, valor)
ESCALA = [
    ("Muito baixo", 0),
    ("Baixo", 1),
    ("Médio", 2),
    ("Alto", 3),
    ("Muito alto", 4),
]

# Perguntas do questionário. Cada resposta soma (valor da escala x peso)
# nos dois scores. Para ajustar, basta alterar os textos e os pesos aqui.
PERGUNTAS = [
    {
        "tema": "Tristeza ou desânimo",
        "texto": "qual foi o seu nível de tristeza, desânimo ou falta de esperança?",
        "peso_ansiedade": 1,
        "peso_depressao": 3,
    },
    {
        "tema": "Perda de interesse ou prazer",
        "texto": "qual foi o seu nível de perda de interesse ou prazer nas coisas que costumava gostar?",
        "peso_ansiedade": 1,
        "peso_depressao": 3,
    },
    {
        "tema": "Pensamentos negativos sobre si",
        "texto": "qual foi o seu nível de pensamentos negativos sobre si mesmo, como culpa ou sensação de inutilidade?",
        "peso_ansiedade": 1,
        "peso_depressao": 3,
    },
    {
        "tema": "Preocupação excessiva",
        "texto": "qual foi o seu nível de preocupação com as coisas, mesmo sem um motivo claro?",
        "peso_ansiedade": 3,
        "peso_depressao": 1,
    },
    {
        "tema": "Tensão ou dificuldade de relaxar",
        "texto": "qual foi o seu nível de nervosismo, tensão ou dificuldade para relaxar?",
        "peso_ansiedade": 3,
        "peso_depressao": 1,
    },
    {
        "tema": "Sintomas físicos",
        "texto": "qual foi o seu nível de sintomas físicos como coração acelerado, aperto no peito, tremor ou falta de ar?",
        "peso_ansiedade": 3,
        "peso_depressao": 1,
    },
    {
        "tema": "Problemas de sono",
        "texto": "qual foi o seu nível de dificuldade com o sono, seja para dormir, manter o sono ou por dormir demais?",
        "peso_ansiedade": 2,
        "peso_depressao": 2,
    },
    {
        "tema": "Dificuldade de concentração",
        "texto": "qual foi o seu nível de dificuldade para se concentrar ou tomar decisões?",
        "peso_ansiedade": 2,
        "peso_depressao": 2,
    },
]

PERGUNTA_IDEACAO = (
    "Para finalizar: nas últimas duas semanas, você teve pensamentos de se machucar "
    "ou de que seria melhor não estar aqui?"
)

VALOR_MAXIMO = max(valor for _, valor in ESCALA)
SCORE_MAXIMO_ANSIEDADE = VALOR_MAXIMO * sum(p["peso_ansiedade"] for p in PERGUNTAS)
SCORE_MAXIMO_DEPRESSAO = VALOR_MAXIMO * sum(p["peso_depressao"] for p in PERGUNTAS)


def perguntar(dispatcher: CollectingDispatcher, indice: int):
    """Envia a pergunta do índice informado com os botões da escala."""
    pergunta = PERGUNTAS[indice]
    dispatcher.utter_message(
        text=f"Pergunta {indice + 1} de {len(PERGUNTAS)}. Nas últimas duas semanas, {pergunta['texto']}",
        buttons=[
            {"title": rotulo, "payload": f'/responder_escala{{"valor":"{valor}"}}'}
            for rotulo, valor in ESCALA
        ],
    )


def perguntar_ideacao(dispatcher: CollectingDispatcher):
    dispatcher.utter_message(
        text=PERGUNTA_IDEACAO,
        buttons=[
            {"title": "Sim", "payload": "/afirmar_ideacao"},
            {"title": "Não", "payload": "/negar_ideacao"},
        ],
    )


def descrever_paciente(tracker: Tracker) -> str:
    nome = tracker.get_slot("nome") or "não informado"
    idade = tracker.get_slot("idade") or "não informada"
    sexo = tracker.get_slot("sexo") or "não informado"
    return f"Paciente: {nome}\nIdade: {idade}\nSexo: {sexo}"


def montar_relatorio(tracker: Tracker, tem_ideacao: bool) -> str:
    ansiedade = int(tracker.get_slot("score_ansiedade") or 0)
    depressao = int(tracker.get_slot("score_depressao") or 0)
    respostas = tracker.get_slot("respostas") or []
    rotulos = {valor: rotulo for rotulo, valor in ESCALA}

    linhas = [
        descrever_paciente(tracker),
        "",
        f"Score de ansiedade: {ansiedade}/{SCORE_MAXIMO_ANSIEDADE} "
        f"({round(100 * ansiedade / SCORE_MAXIMO_ANSIEDADE)}%)",
        f"Score de depressão: {depressao}/{SCORE_MAXIMO_DEPRESSAO} "
        f"({round(100 * depressao / SCORE_MAXIMO_DEPRESSAO)}%)",
        f"Ideação suicida: {'SIM' if tem_ideacao else 'Não'}",
        "",
        "Respostas:",
    ]
    for pergunta, valor in zip(PERGUNTAS, respostas):
        linhas.append(f"- {pergunta['tema']}: {rotulos[valor]} ({valor})")
    if len(respostas) < len(PERGUNTAS):
        linhas.append(f"(questionário incompleto: {len(respostas)} de {len(PERGUNTAS)} respostas)")

    return "\n".join(linhas)


class ValidateIdentificacaoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_identificacao_form"

    def validate_nome(self, slot_value: Any,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any]) -> Dict[Text, Any]:
        nome = re.sub(
            r"^(meu nome é|me chamo|pode me chamar de|eu sou|sou o|sou a)\s+",
            "",
            str(slot_value).strip(),
            flags=re.IGNORECASE,
        )
        if not nome or len(nome) > 80:
            dispatcher.utter_message(text="Não consegui registrar o nome. Pode informar novamente?")
            return {"nome": None}
        return {"nome": nome}

    def validate_idade(self, slot_value: Any,
                       dispatcher: CollectingDispatcher,
                       tracker: Tracker,
                       domain: Dict[Text, Any]) -> Dict[Text, Any]:
        numero = re.search(r"\d+", str(slot_value))
        if not numero or not 1 <= int(numero.group()) <= 120:
            dispatcher.utter_message(text="Por favor, informe sua idade em números. Exemplo: 28")
            return {"idade": None}
        return {"idade": numero.group()}


class ActionIniciarQuestionario(Action):
    def name(self) -> Text:
        return "action_iniciar_questionario"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nome = tracker.get_slot("nome") or "você"
        dispatcher.utter_message(
            text=(
                f"Obrigado, {nome}. Agora vou fazer {len(PERGUNTAS)} perguntas rápidas. "
                "Escolha a opção que melhor descreve como você tem se sentido."
            )
        )
        perguntar(dispatcher, 0)
        return [
            SlotSet("indice_pergunta", 0),
            SlotSet("score_ansiedade", 0),
            SlotSet("score_depressao", 0),
            SlotSet("respostas", []),
            SlotSet("tem_ideacao_suicida", None),
            SlotSet("anamnese_encerrada", False),
        ]


class ActionRegistrarResposta(Action):
    """Soma a resposta da pergunta atual nos dois scores e faz a próxima pergunta."""
    def name(self) -> Text:
        return "action_registrar_resposta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        indice = tracker.get_slot("indice_pergunta")
        if indice is None or tracker.get_slot("anamnese_encerrada"):
            dispatcher.utter_message(response="utter_default")
            return []

        indice = int(indice)
        if indice >= len(PERGUNTAS):
            perguntar_ideacao(dispatcher)
            return []

        valor = next(tracker.get_latest_entity_values("valor"), None)
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            valor = None

        if valor not in [v for _, v in ESCALA]:
            dispatcher.utter_message(text="Por favor, escolha uma das opções.")
            perguntar(dispatcher, indice)
            return []

        pergunta = PERGUNTAS[indice]
        ansiedade = (tracker.get_slot("score_ansiedade") or 0) + valor * pergunta["peso_ansiedade"]
        depressao = (tracker.get_slot("score_depressao") or 0) + valor * pergunta["peso_depressao"]
        respostas = (tracker.get_slot("respostas") or []) + [valor]

        proximo = indice + 1
        if proximo < len(PERGUNTAS):
            perguntar(dispatcher, proximo)
        else:
            perguntar_ideacao(dispatcher)

        return [
            SlotSet("indice_pergunta", proximo),
            SlotSet("score_ansiedade", ansiedade),
            SlotSet("score_depressao", depressao),
            SlotSet("respostas", respostas),
        ]


class ActionProtocoloRiscoSuicida(Action):
    """
    Acionado quando o paciente afirma ideação suicida.
    Registra o slot e envia o alerta imediato ao profissional
    por Telegram e e-mail.
    """
    def name(self) -> Text:
        return "action_protocolo_risco_suicida"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        notificar_profissional(
            "ALERTA: paciente relatou ideação suicida",
            (
                "O paciente abaixo respondeu SIM à pergunta sobre pensamentos de se "
                "machucar ou de que seria melhor não estar aqui.\n\n"
                f"{descrever_paciente(tracker)}\n\n"
                "O relatório completo da anamnese será enviado em seguida."
            ),
        )
        dispatcher.utter_message(
            text=(
                "Obrigado por compartilhar isso. O que você está sentindo é importante "
                "e será avaliado com prioridade pelo profissional responsável. "
                "Se precisar de apoio agora, ligue para o CVV no 188 (gratuito, 24 horas) "
                "ou procure o pronto-socorro mais próximo."
            )
        )
        return [SlotSet("tem_ideacao_suicida", True)]


class ActionEncerrarAnamnese(Action):
    def name(self) -> Text:
        return "action_encerrar_anamnese"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("anamnese_encerrada"):
            return []

        nome = tracker.get_slot("nome") or "você"
        tem_ideacao = bool(tracker.get_slot("tem_ideacao_suicida"))

        assunto = "Anamnese concluída"
        if tem_ideacao:
            assunto += " - ALERTA de ideação suicida"
        notificar_profissional(assunto, montar_relatorio(tracker, tem_ideacao))

        dispatcher.utter_message(
            text=(
                f"Obrigado pelas respostas, {nome}. A anamnese foi concluída e "
                "será avaliada pelo profissional responsável."
            )
        )
        return [
            SlotSet("tem_ideacao_suicida", tem_ideacao),
            SlotSet("anamnese_encerrada", True),
        ]
