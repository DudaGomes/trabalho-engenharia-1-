"""UC5 — Execução de Votação (RF6): comando Iniciar.

É AQUI que a lista de aptos e seus pesos são congelados (RN1/RN2) e que a
votação é liberada (RN3) com o cronômetro disparado (RN8) — tudo na mesma
transação.
"""

from datetime import datetime

from src.casos_de_uso.erros import ErroDeNegocio
from src.config.constantes import StatusVotacao
from src.modelos import participacao_votacao, usuario, votacao


def iniciar(conexao, votacao_id):
    registro = votacao.buscar_por_id(conexao, votacao_id)
    if registro is None:
        raise ErroDeNegocio("Votação não encontrada")

    # RN3 — somente uma votação Configurada pode ser iniciada
    if registro["status"] != StatusVotacao.CONFIGURADA:
        raise ErroDeNegocio("Somente votação Configurada pode ser iniciada")

    # UC5 — não pode haver duas votações ATIVAS na mesma reunião
    if votacao.buscar_ativa_na_reuniao(conexao, registro["reuniao_id"]):
        raise ErroDeNegocio(
            "Já existe uma votação Ativa nesta reunião — "
            "encerre a votação atual antes de iniciar outra")

    # RN2 — apto = proprietário ATIVO com >= 1 lote NESTE instante;
    # RN1 — o peso de cada apto = soma dos pesos de seus lotes NESTE instante.
    # A fotografia fica congelada em participacao_votacao para toda a votação.
    aptos = usuario.listar_aptos_com_peso(conexao)
    for apto in aptos:
        participacao_votacao.fixar_apto(
            conexao, votacao_id, apto["id"], apto["peso_total"])

    # RN3/RN8 — status ATIVA e cronômetro contando a partir de agora
    votacao.ativar(
        conexao, votacao_id, datetime.now().isoformat(timespec="seconds"))

    conexao.commit()
    return len(aptos)
