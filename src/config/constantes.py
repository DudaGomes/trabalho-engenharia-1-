"""Enumerações da ERSw (seção 3.5) e mensagens oficiais dos casos de uso.

Todos os valores literais do sistema vivem aqui, para que telas, rotas e
casos de uso nunca "inventem" textos ou estados fora da especificação.
"""


# ── Enumerações da ERSw ──────────────────────────────────────────────────────

class TipoUsuario:
    ADMINISTRADOR = "ADMINISTRADOR"
    PROPRIETARIO = "PROPRIETARIO"


class TipoResposta:
    SIM_NAO_ABSTENCAO = "SIM_NAO_ABSTENCAO"
    MULTIPLA_ESCOLHA = "MULTIPLA_ESCOLHA"
    ELEICAO_NOMES = "ELEICAO_NOMES"

    TODOS = (SIM_NAO_ABSTENCAO, MULTIPLA_ESCOLHA, ELEICAO_NOMES)

    ROTULOS = {
        SIM_NAO_ABSTENCAO: "Sim/Não/Abstenção",
        MULTIPLA_ESCOLHA: "Múltipla Escolha",
        ELEICAO_NOMES: "Eleição de Nomes",
    }


class Visibilidade:
    ABERTA = "ABERTA"
    FECHADA = "FECHADA"

    TODAS = (ABERTA, FECHADA)

    ROTULOS = {
        ABERTA: "Aberta (nominal)",
        FECHADA: "Fechada (sigilo da escolha individual)",
    }


class StatusVotacao:
    CONFIGURADA = "CONFIGURADA"
    ATIVA = "ATIVA"
    ENCERRADA = "ENCERRADA"


class StatusResultado:
    CONCLUIDO = "CONCLUIDO"
    EMPATE = "EMPATE"
    SEM_QUORUM = "SEM_QUORUM"


class StatusReuniao:
    RASCUNHO = "RASCUNHO"
    AGENDADA = "AGENDADA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    ENCERRADA = "ENCERRADA"


# RN7 — opções fixas do tipo Sim/Não/Abstenção
OPCOES_SIM_NAO_ABSTENCAO = ("Sim", "Não", "Abstenção")

# RN6 — a abstenção participa do quórum, mas não concorre à vitória
TEXTO_ABSTENCAO = "Abstenção"


# ── Mensagens oficiais (textos exatos da ERSw) ───────────────────────────────

MSG_LOGIN_INVALIDO = "E-mail ou senha incorretos"
MSG_JA_VOTOU = "Seu voto já foi registrado"
MSG_NAO_APTO = "Você não está apto a votar nesta votação"
MSG_VOTACAO_ENCERRADA = "Votação encerrada"


# ── Política de senha (RNF4) ─────────────────────────────────────────────────

TAMANHO_MINIMO_SENHA = 8

# Lista embutida de senhas comuns rejeitadas (RNF4)
SENHAS_COMUNS = {
    "12345678", "123456789", "1234567890", "password", "password1",
    "senha123", "12341234", "qwerty123", "abc12345", "11111111",
    "iloveyou", "sunshine", "football", "princess", "admin123",
    "welcome1", "monkey123", "dragon123", "letmein1", "trustno1",
}


def validar_senha(senha):
    """RNF4 — Segurança de acesso: senha com no mínimo 8 caracteres,
    recusando senhas presentes na lista de senhas comuns.

    Retorna None quando válida ou uma mensagem de erro quando inválida.
    """
    if senha is None or len(senha) < TAMANHO_MINIMO_SENHA:
        return f"A senha deve ter no mínimo {TAMANHO_MINIMO_SENHA} caracteres"
    if senha.lower() in SENHAS_COMUNS:
        return "Senha muito comum — escolha outra senha"
    return None
