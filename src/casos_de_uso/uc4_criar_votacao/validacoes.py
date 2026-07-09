"""UC4 — validações de configuração de votação (RN7 e RN8).

Compartilhadas por criar_votacao e alterar_votacao, para que a mesma regra
nunca exista em dois lugares.
"""

import re

from src.casos_de_uso.erros import ErroDeNegocio
from src.config.constantes import (
    OPCOES_SIM_NAO_ABSTENCAO, TipoResposta, Visibilidade)

FORMATO_DURACAO = re.compile(r"^(\d{1,2}):([0-5]\d)$")


def validar_duracao(duracao):
    """RN8 — Duração obrigatória: formato mm:ss validado e valor > 00:00."""
    duracao = (duracao or "").strip()
    correspondencia = FORMATO_DURACAO.match(duracao)
    if not correspondencia:
        raise ErroDeNegocio("Duração inválida — informe no formato mm:ss")
    minutos, segundos = int(correspondencia.group(1)), int(correspondencia.group(2))
    if minutos * 60 + segundos <= 0:
        raise ErroDeNegocio("Duração deve ser maior que 00:00")
    return f"{minutos:02d}:{segundos:02d}"


def duracao_em_segundos(duracao):
    """mm:ss → segundos (usada pelo UC5 para o cronômetro)."""
    minutos, segundos = duracao.split(":")
    return int(minutos) * 60 + int(segundos)


def validar_quorum(quorum_texto):
    """Quórum mínimo é OPCIONAL: em branco vale 0% (protótipo do UC4)."""
    texto = (quorum_texto or "").strip().replace("%", "").replace(",", ".")
    if texto == "":
        return 0.0
    try:
        quorum = float(texto)
    except ValueError:
        raise ErroDeNegocio("Quórum mínimo inválido — informe um percentual")
    if not 0 <= quorum <= 100:
        raise ErroDeNegocio("Quórum mínimo deve estar entre 0% e 100%")
    return quorum


def validar_opcoes(tipo_resposta, opcoes_texto):
    """RN7 — Tipos de resposta:
    Sim/Não/Abstenção usa opções FIXAS; Múltipla Escolha e Eleição de Nomes
    exigem pelo menos 2 opções/nomes DISTINTOS cadastrados."""
    if tipo_resposta not in TipoResposta.TODOS:
        raise ErroDeNegocio("Tipo de resposta inválido")

    if tipo_resposta == TipoResposta.SIM_NAO_ABSTENCAO:
        return list(OPCOES_SIM_NAO_ABSTENCAO)

    opcoes = [linha.strip() for linha in (opcoes_texto or "").splitlines()
              if linha.strip()]
    distintas = {opcao.casefold() for opcao in opcoes}
    if tipo_resposta == TipoResposta.MULTIPLA_ESCOLHA:
        minimo = "pelo menos duas opções distintas"
        repetido = "Há opções repetidas — cada opção deve ser distinta"
    else:
        minimo = "pelo menos dois nomes distintos"
        repetido = "Há nomes repetidos — cada nome deve ser distinto"
    if len(opcoes) < 2 or len(distintas) < 2:
        raise ErroDeNegocio(f"Informe {minimo} para este tipo de votação")
    if len(distintas) != len(opcoes):
        raise ErroDeNegocio(repetido)
    return opcoes


def validar_configuracao(pergunta, tipo_resposta, visibilidade,
                         duracao, quorum_texto, opcoes_texto):
    """Valida o conjunto e devolve os valores normalizados."""
    if not (pergunta or "").strip():
        raise ErroDeNegocio("Informe a pergunta da votação")
    if visibilidade not in Visibilidade.TODAS:
        raise ErroDeNegocio("Visibilidade inválida")
    return {
        "pergunta": pergunta.strip(),
        "tipo_resposta": tipo_resposta,
        "visibilidade": visibilidade,
        "duracao": validar_duracao(duracao),
        "quorum_minimo": validar_quorum(quorum_texto),
        "opcoes": validar_opcoes(tipo_resposta, opcoes_texto),
    }
