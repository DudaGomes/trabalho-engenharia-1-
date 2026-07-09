"""UC6 — Apuração e Resultado da Votação (RF7): apurar.

RN6 — Quórum e resultado:
  • quórum = pesoParticipante / pesoTotalApto;
  • abaixo do mínimo → SEM_QUORUM, sem vencedora;
  • com quórum, vence a opção CONCORRENTE de maior peso;
  • igualdade no maior peso → EMPATE, vencedora vazia;
  • caso contrário → CONCLUIDO com a vencedora.
A abstenção conta para participação e quórum, mas NÃO concorre.
"""

from datetime import datetime

from src.casos_de_uso.erros import ErroDeNegocio
from src.config.constantes import (StatusResultado, StatusVotacao,
                                   TEXTO_ABSTENCAO, TipoResposta)
from src.modelos import (participacao_votacao, resultado_votacao, votacao,
                         voto)


def _e_concorrente(registro_votacao, opcao):
    """RN6 — em Sim/Não/Abstenção, a Abstenção participa do quórum mas não
    concorre à vitória; nos demais tipos todas as opções concorrem."""
    if registro_votacao["tipo_resposta"] != TipoResposta.SIM_NAO_ABSTENCAO:
        return True
    return opcao["texto"] != TEXTO_ABSTENCAO


def apurar(conexao, votacao_id):
    """Apura uma votação Encerrada e persiste o ResultadoVotacao.
    Idempotente: se já foi apurada, retorna o resultado existente."""
    registro = votacao.buscar_por_id(conexao, votacao_id)
    if registro is None:
        raise ErroDeNegocio("Votação não encontrada")
    if registro["status"] != StatusVotacao.ENCERRADA:
        raise ErroDeNegocio("Somente votação Encerrada pode ser apurada")

    existente = resultado_votacao.buscar_por_votacao(conexao, votacao_id)
    if existente is not None:
        return existente

    # RN2/RN6 — pesos a partir da lista congelada no Iniciar
    totais = participacao_votacao.totais(conexao, votacao_id)
    peso_total_apto = totais["peso_total_apto"]
    peso_participante = totais["peso_participante"]
    percentual = (100.0 * peso_participante / peso_total_apto
                  if peso_total_apto > 0 else 0.0)

    apuracao = voto.apuracao_por_opcao(conexao, votacao_id)

    # RN6 — quórum mínimo (0% quando não configurado)
    if percentual + 1e-9 < registro["quorum_minimo"]:
        status, vencedora_id = StatusResultado.SEM_QUORUM, None
    else:
        concorrentes = [o for o in apuracao if _e_concorrente(registro, o)]
        maior_peso = max(o["peso_total"] for o in concorrentes)
        lideres = [o for o in concorrentes if o["peso_total"] == maior_peso]
        if len(lideres) > 1:
            # RN6 — igualdade no maior peso: EMPATE, vencedora vazia
            status, vencedora_id = StatusResultado.EMPATE, None
        else:
            status, vencedora_id = StatusResultado.CONCLUIDO, lideres[0]["id"]

    resultado_votacao.inserir(
        conexao, status, peso_total_apto, peso_participante,
        round(percentual, 2), datetime.now().isoformat(timespec="seconds"),
        votacao_id, vencedora_id)
    conexao.commit()
    return resultado_votacao.buscar_por_votacao(conexao, votacao_id)
