from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


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
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarIdade(Action):
    def name(self) -> Text:
        return "action_perguntar_idade"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nome = tracker.get_slot("nome") or "você"
        texto = f"Quantos anos você tem, {nome}?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarSexo(Action):
    def name(self) -> Text:
        return "action_perguntar_sexo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Como você se identifica? Masculino, feminino ou prefere não dizer?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarQueixaPrincipal(Action):
    def name(self) -> Text:
        return "action_perguntar_queixa_principal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Qual é o principal problema ou sintoma que te trouxe aqui hoje?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionFalarSobreOProblema(Action):
    def name(self) -> Text:
        return "action_falar_sobre_o_problema"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        problema = tracker.get_slot("problema") or "esse problema"
        texto = f"Pode me contar mais sobre {problema}? Há quanto tempo você está lidando com isso?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]

class ActionPerguntarHumor(Action):
    def name(self) -> Text:
        return "action_perguntar_humor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Como você descreveria seu humor nas últimas semanas? Tem se sentido triste, vazio ou sem ânimo?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarAnedonia(Action):
    def name(self) -> Text:
        return "action_perguntar_anedonia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você ainda sente prazer nas coisas que costumava gostar, como hobbies, amigos ou atividades do dia a dia?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarPensamentos(Action):
    def name(self) -> Text:
        return "action_perguntar_pensamentos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você tem tido pensamentos negativos sobre si mesmo, como se sentir inútil, um peso ou sem valor?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]

class ActionPerguntarAnsiedade(Action):
    def name(self) -> Text:
        return "action_perguntar_ansiedade"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você se preocupa muito com as coisas, mesmo sem um motivo claro? Sente dificuldade de relaxar?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarPanico(Action):
    def name(self) -> Text:
        return "action_perguntar_panico"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Já teve episódios de crise intensa, com coração acelerado, falta de ar ou sensação de que algo ruim ia acontecer?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarFobiaSocial(Action):
    def name(self) -> Text:
        return "action_perguntar_fobia_social"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Situações sociais te causam ansiedade ou você tende a evitá-las?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarSintomasFisicos(Action):
    def name(self) -> Text:
        return "action_perguntar_sintomas_fisicos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você sente sintomas físicos quando está ansioso, como tremor, aperto no peito, tontura ou falta de ar?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


# ─────────────────────────────────────────────────────────────────────────────
# SONO
# ─────────────────────────────────────────────────────────────────────────────

class ActionPerguntarSono(Action):
    def name(self) -> Text:
        return "action_perguntar_sono"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Como está seu sono? Tem dificuldade para dormir, acorda muito durante a noite ou dorme mais do que o normal?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


# ─────────────────────────────────────────────────────────────────────────────
# APETITE
# ─────────────────────────────────────────────────────────────────────────────

class ActionPerguntarApetite(Action):
    def name(self) -> Text:
        return "action_perguntar_apetite"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Seu apetite mudou? Está comendo menos, mais, ou não sente fome?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


# ─────────────────────────────────────────────────────────────────────────────
# COGNIÇÃO
# ─────────────────────────────────────────────────────────────────────────────

class ActionPerguntarCognicao(Action):
    def name(self) -> Text:
        return "action_perguntar_cognicao"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Tem tido dificuldade para se concentrar, tomar decisões ou sua memória está falhando?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


# ─────────────────────────────────────────────────────────────────────────────
# IMPACTO FUNCIONAL
# ─────────────────────────────────────────────────────────────────────────────

class ActionPerguntarImpactoTrabalho(Action):
    def name(self) -> Text:
        return "action_perguntar_impacto_trabalho"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Esses problemas estão afetando seu trabalho ou estudos? Como?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarImpactoSocial(Action):
    def name(self) -> Text:
        return "action_perguntar_impacto_social"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você tem se afastado de amigos ou familiares por causa de como está se sentindo?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarImpactoAutocuidado(Action):
    def name(self) -> Text:
        return "action_perguntar_impacto_autocuidado"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você tem conseguido se cuidar normalmente, como higiene, alimentação e tarefas básicas do dia a dia?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


# ─────────────────────────────────────────────────────────────────────────────
# HISTÓRICO DOS SINTOMAS
# ─────────────────────────────────────────────────────────────────────────────

class ActionPerguntarDuracao(Action):
    def name(self) -> Text:
        return "action_perguntar_duracao"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Há quanto tempo você está se sentindo assim?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarIntensidade(Action):
    def name(self) -> Text:
        return "action_perguntar_intensidade"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Como você avaliaria a intensidade do que sente? Numa escala de 1 a 10, qual seria?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarFrequencia(Action):
    def name(self) -> Text:
        return "action_perguntar_frequencia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Com que frequência esses sintomas aparecem? Todo dia, algumas vezes por semana ou de forma esporádica?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarFatorDesencadeante(Action):
    def name(self) -> Text:
        return "action_perguntar_fator_desencadeante"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você consegue identificar algum evento ou situação que desencadeou esses sintomas?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


# ─────────────────────────────────────────────────────────────────────────────
# TRATAMENTO E HISTÓRICO
# ─────────────────────────────────────────────────────────────────────────────

class ActionPerguntarTratamentoAnterior(Action):
    def name(self) -> Text:
        return "action_perguntar_tratamento_anterior"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você já fez algum tratamento psicológico ou psiquiátrico anteriormente?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarMedicacao(Action):
    def name(self) -> Text:
        return "action_perguntar_medicacao"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você está tomando alguma medicação atualmente, seja prescrita ou não?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


class ActionPerguntarHistoricoFamiliar(Action):
    def name(self) -> Text:
        return "action_perguntar_historico_familiar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Há histórico de transtornos mentais na sua família, como depressão, ansiedade ou outros?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


# ─────────────────────────────────────────────────────────────────────────────
# TRIAGEM DE RISCO
# ─────────────────────────────────────────────────────────────────────────────

class ActionPerguntarIdeacao(Action):
    def name(self) -> Text:
        return "action_perguntar_ideacao"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        texto = "Você já teve ou tem pensamentos de se machucar ou de que seria melhor não estar aqui?"
        dispatcher.utter_message(text=texto)
        return [salvar_ultima_pergunta(texto)]


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


# ─────────────────────────────────────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# ENCERRAMENTO
# ─────────────────────────────────────────────────────────────────────────────

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