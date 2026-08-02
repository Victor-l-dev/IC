from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction


# Mapeamento as etapas, para empedir erros do usuario
ETAPAS = {
    "action_perguntar_nome": {
        "intent": "informar_nome",
        "proxima": "action_perguntar_idade",
    },
    "action_perguntar_idade": {
        "intent": "informar_idade",
        "proxima": "action_perguntar_sexo",
    },
    "action_perguntar_sexo": {
        "intent": "informar_sexo",
        "proxima": "action_perguntar_queixa_principal",
    },
    "action_perguntar_queixa_principal": {
        "intent": "relatar_queixa_principal",
        "proxima": "action_perguntar_humor",
    },
    "action_perguntar_humor": {
        "intent": "relatar_humor_deprimido",
        "proxima": "action_perguntar_anedonia",
    },
    "action_perguntar_anedonia": {
        "intent": "relatar_anedonia",
        "proxima": "action_perguntar_pensamentos",
    },
    "action_perguntar_pensamentos": {
        "intent": "relatar_pensamentos_negativos",
        "proxima": "action_perguntar_ansiedade",
    },
    "action_perguntar_ansiedade": {
        "intent": "relatar_ansiedade_generalizada",
        "proxima": "action_perguntar_panico",
    },
    "action_perguntar_panico": {
        "intent": "relatar_crise_de_panico",
        "proxima": "action_perguntar_fobia_social",
    },
    "action_perguntar_fobia_social": {
        "intent": "relatar_fobia_social",
        "proxima": "action_perguntar_sintomas_fisicos",
    },
    "action_perguntar_sintomas_fisicos": {
        "intent": "relatar_sintomas_fisicos_ansiedade",
        "proxima": "action_perguntar_sono",
    },
    "action_perguntar_sono": {
        "intent": "relatar_problema_sono",
        "proxima": "action_perguntar_apetite",
    },
    "action_perguntar_apetite": {
        "intent": "relatar_alteracao_apetite",
        "proxima": "action_perguntar_cognicao",
    },
    "action_perguntar_cognicao": {
        "intent": "relatar_dificuldade_cognitiva",
        "proxima": "action_perguntar_impacto_trabalho",
    },
    "action_perguntar_impacto_trabalho": {
        "intent": "relatar_impacto_trabalho_estudo",
        "proxima": "action_perguntar_impacto_social",
    },
    "action_perguntar_impacto_social": {
        "intent": "relatar_impacto_social",
        "proxima": "action_perguntar_impacto_autocuidado",
    },
    "action_perguntar_impacto_autocuidado": {
        "intent": "relatar_impacto_autocuidado",
        "proxima": "action_perguntar_duracao",
    },
    "action_perguntar_duracao": {
        "intent": "informar_duracao_sintomas",
        "proxima": "action_perguntar_intensidade",
    },
    "action_perguntar_intensidade": {
        "intent": "informar_intensidade_sintomas",
        "proxima": "action_perguntar_frequencia",
    },
    "action_perguntar_frequencia": {
        "intent": "informar_frequencia_sintomas",
        "proxima": "action_perguntar_fator_desencadeante",
    },
    "action_perguntar_fator_desencadeante": {
        "intent": "informar_fator_desencadeante",
        "proxima": "action_perguntar_tratamento_anterior",
    },
    "action_perguntar_tratamento_anterior": {
        "intent": "informar_tratamento_anterior",
        "proxima": "action_perguntar_medicacao",
    },
    "action_perguntar_medicacao": {
        "intent": "informar_medicacao_atual",
        "proxima": "action_perguntar_historico_familiar",
    },
    "action_perguntar_historico_familiar": {
        "intent": "informar_historico_familiar",
        "proxima": "action_perguntar_ideacao",
    },
    "action_perguntar_ideacao": {
        "intent": ["expressar_ideacao_suicida", "negar_ideacao_suicida"],
        "proxima": "action_encerrar_anamnese",
    },
}


def validar_etapa(tracker: Tracker, dispatcher: CollectingDispatcher):
    """
    Verifica se o intent recebido é o esperado para a etapa atual da conversa.
    Se não for, repete a última pergunta em vez de avançar.
    Retorna None se a validação passou.
    Retorna [] caso a resposta não corresponda ao esperado.
    """

    etapa = tracker.get_slot("etapa_atual")
    intent = tracker.latest_message.get("intent", {}).get("name")

    if etapa not in ETAPAS:
        return None

    esperado = ETAPAS[etapa]["intent"]

    if isinstance(esperado, str):
        esperado = [esperado]

    if intent not in esperado:
        ultima = tracker.get_slot("ultima_pergunta") or ""

        dispatcher.utter_message(
            text=f"Antes de continuar, preciso que responda a pergunta anterior:\n\n{ultima}"
        )

        return []

    return None


def salvar_ultima_pergunta(texto: str):
    return SlotSet("ultima_pergunta", texto)

class ActionPerguntarNome(Action):
    def name(self) -> Text:
        return "action_perguntar_nome"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Qual é o seu nome?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarIdade(Action):
    def name(self) -> Text:
        return "action_perguntar_idade"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        nome = tracker.get_slot("nome") or "você"
        texto = f"Quantos anos você tem, {nome}?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarSexo(Action):
    def name(self) -> Text:
        return "action_perguntar_sexo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Como você se identifica? Masculino, feminino ou prefere não dizer?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarQueixaPrincipal(Action):
    def name(self) -> Text:
        return "action_perguntar_queixa_principal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Qual é o principal problema ou sintoma que te trouxe aqui hoje?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionFalarSobreOProblema(Action):
    def name(self) -> Text:
        return "action_falar_sobre_o_problema"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        problema = tracker.get_slot("problema") or "esse problema"
        texto = f"Pode me contar mais sobre {problema}? Há quanto tempo você está lidando com isso?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]

class ActionPerguntarHumor(Action):
    def name(self) -> Text:
        return "action_perguntar_humor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Como você descreveria seu humor nas últimas semanas? Tem se sentido triste, vazio ou sem ânimo?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarAnedonia(Action):
    def name(self) -> Text:
        return "action_perguntar_anedonia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você ainda sente prazer nas coisas que costumava gostar, como hobbies, amigos ou atividades do dia a dia?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarPensamentos(Action):
    def name(self) -> Text:
        return "action_perguntar_pensamentos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você tem tido pensamentos negativos sobre si mesmo, como se sentir inútil, um peso ou sem valor?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]

class ActionPerguntarAnsiedade(Action):
    def name(self) -> Text:
        return "action_perguntar_ansiedade"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você se preocupa muito com as coisas, mesmo sem um motivo claro? Sente dificuldade de relaxar?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarPanico(Action):
    def name(self) -> Text:
        return "action_perguntar_panico"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Já teve episódios de crise intensa, com coração acelerado, falta de ar ou sensação de que algo ruim ia acontecer?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarFobiaSocial(Action):
    def name(self) -> Text:
        return "action_perguntar_fobia_social"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Situações sociais te causam ansiedade ou você tende a evitá-las?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarSintomasFisicos(Action):
    def name(self) -> Text:
        return "action_perguntar_sintomas_fisicos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você sente sintomas físicos quando está ansioso, como tremor, aperto no peito, tontura ou falta de ar?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarSono(Action):
    def name(self) -> Text:
        return "action_perguntar_sono"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Como está seu sono? Tem dificuldade para dormir, acorda muito durante a noite ou dorme mais do que o normal?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarApetite(Action):
    def name(self) -> Text:
        return "action_perguntar_apetite"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Seu apetite mudou? Está comendo menos, mais, ou não sente fome?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]

class ActionPerguntarCognicao(Action):
    def name(self) -> Text:
        return "action_perguntar_cognicao"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Tem tido dificuldade para se concentrar, tomar decisões ou sua memória está falhando?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarImpactoTrabalho(Action):
    def name(self) -> Text:
        return "action_perguntar_impacto_trabalho"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Esses problemas estão afetando seu trabalho ou estudos? Como?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarImpactoSocial(Action):
    def name(self) -> Text:
        return "action_perguntar_impacto_social"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você tem se afastado de amigos ou familiares por causa de como está se sentindo?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarImpactoAutocuidado(Action):
    def name(self) -> Text:
        return "action_perguntar_impacto_autocuidado"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você tem conseguido se cuidar normalmente, como higiene, alimentação e tarefas básicas do dia a dia?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]

class ActionPerguntarDuracao(Action):
    def name(self) -> Text:
        return "action_perguntar_duracao"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Há quanto tempo você está se sentindo assim?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarIntensidade(Action):
    def name(self) -> Text:
        return "action_perguntar_intensidade"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Como você avaliaria a intensidade do que sente? Numa escala de 1 a 10, qual seria?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarFrequencia(Action):
    def name(self) -> Text:
        return "action_perguntar_frequencia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Com que frequência esses sintomas aparecem? Todo dia, algumas vezes por semana ou de forma esporádica?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarFatorDesencadeante(Action):
    def name(self) -> Text:
        return "action_perguntar_fator_desencadeante"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você consegue identificar algum evento ou situação que desencadeou esses sintomas?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarTratamentoAnterior(Action):
    def name(self) -> Text:
        return "action_perguntar_tratamento_anterior"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você já fez algum tratamento psicológico ou psiquiátrico anteriormente?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarMedicacao(Action):
    def name(self) -> Text:
        return "action_perguntar_medicacao"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você está tomando alguma medicação atualmente, seja prescrita ou não?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionPerguntarHistoricoFamiliar(Action):
    def name(self) -> Text:
        return "action_perguntar_historico_familiar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Há histórico de transtornos mentais na sua família, como depressão, ansiedade ou outros?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]

class ActionPerguntarIdeacao(Action):
    def name(self) -> Text:
        return "action_perguntar_ideacao"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        resultado = validar_etapa(tracker, dispatcher)
        if resultado is not None:
            return resultado

        texto = "Você já teve ou tem pensamentos de se machucar ou de que seria melhor não estar aqui?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", self.name())]


class ActionProcessarRespostaGenerica(Action):
    def name(self) -> Text:
        return "action_processar_resposta_generica"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        etapa_atual = tracker.get_slot("etapa_atual")

        proximo_passo = {
            "action_perguntar_tratamento_anterior": (
                "Você está tomando alguma medicação atualmente, seja prescrita ou não?",
                "action_perguntar_medicacao",
            ),
            "action_perguntar_medicacao": (
                "Há histórico de transtornos mentais na sua família, como depressão, ansiedade ou outros?",
                "action_perguntar_historico_familiar",
            ),
            "action_perguntar_historico_familiar": (
                "Você já teve ou tem pensamentos de se machucar ou de que seria melhor não estar aqui?",
                "action_perguntar_ideacao",
            ),
        }

        if etapa_atual in proximo_passo:
            texto, proxima_etapa = proximo_passo[etapa_atual]
            dispatcher.utter_message(text=texto)
            return [salvar_ultima_pergunta(texto), SlotSet("etapa_atual", proxima_etapa)]

        dispatcher.utter_message(response="utter_default")
        return []


class ActionProtocoloRiscoSuicida(Action):
    """
    Acionado quando ideação suicida é detectada.
    Registra o slot, emite alerta e encerra o fluxo normal
    para que o profissional assuma o atendimento.
    """
    def name(self) -> Text:
        return "action_protocolo_risco_suicida"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text=(
                "Obrigado por compartilhar isso. Esse é um ponto muito importante "
                "e será avaliado com prioridade pelo profissional responsável. "
                "Vou registrar agora."
            )
        )
        dispatcher.utter_message(
            text="A informação foi registrada. O profissional responsável será notificado."
        )
        return [
            SlotSet("tem_ideacao_suicida", True),
            SlotSet("anamnese_encerrada", True),
        ]

class ActionRepetirUltimaPergunta(Action):
    def name(self) -> Text:
        return "action_repetir_ultima_pergunta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ultima = tracker.get_slot("ultima_pergunta")
        if ultima:
            dispatcher.utter_message(text=f"Claro, vou repetir: {ultima}")
        else:
            dispatcher.utter_message(text="Desculpe, não tenho a pergunta anterior registrada. Vamos continuar?")
        return []


class ActionAceitarIndefinidoEContinuar(Action):
    def name(self) -> Text:
        return "action_aceitar_indefinido_e_continuar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Tudo bem, sem problema. Vamos continuar.")
        return []

class ActionEncerrarAnamnese(Action):
    def name(self) -> Text:
        return "action_encerrar_anamnese"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nome = tracker.get_slot("nome") or "você"
        encerrada_antecipadamente = not tracker.get_slot("anamnese_encerrada")

        if encerrada_antecipadamente:
            dispatcher.utter_message(
                text=(
                    "A sessão foi encerrada antes de concluirmos todas as perguntas. "
                    "O que foi coletado até aqui foi salvo."
                )
            )
        else:
            dispatcher.utter_message(
                text=(
                    f"Obrigado pelas respostas, {nome}. "
                    "As informações foram registradas e estarão disponíveis "
                    "para o profissional responsável."
                )
            )

        return [SlotSet("anamnese_encerrada", True)]