"""UC5 — Execução de Votação (RF6): Confirmar Voto.

Concentra as verificações do fluxo principal e de TODOS os fluxos de erro
da ERSw: votação encerrada, proprietário não apto e proprietário já votou.
"""

import sqlite3
from datetime import datetime

from src.casos_de_uso.erros import ErroDeNegocio
from src.casos_de_uso.uc5_executar_votacao import encerrar
from src.config.constantes import (MSG_JA_VOTOU, MSG_NAO_APTO,
                                   MSG_VOTACAO_ENCERRADA, StatusVotacao,
                                   Visibilidade)
from src.modelos import opcao_voto, participacao_votacao, votacao, voto


def votar(conexao, votacao_id, usuario_id, opcao_voto_id):
    registro = votacao.buscar_por_id(conexao, votacao_id)
    if registro is None:
        raise ErroDeNegocio("Votação não encontrada")

    # RN8 — rejeita voto que chegue após o fim do tempo, mesmo com a tela
    # aberta: o encerramento automático roda ANTES de qualquer validação.
    if encerrar.encerrar_se_tempo_esgotado(conexao, registro):
        raise ErroDeNegocio(MSG_VOTACAO_ENCERRADA)
    if registro["status"] == StatusVotacao.ENCERRADA:
        raise ErroDeNegocio(MSG_VOTACAO_ENCERRADA)

    # RN3 — apenas votações ATIVAS recebem votos
    if registro["status"] != StatusVotacao.ATIVA:
        raise ErroDeNegocio("Votação ainda não foi liberada")

    # RN2 — apto é somente quem está na lista congelada no Iniciar
    participacao = participacao_votacao.buscar(conexao, votacao_id, usuario_id)
    if participacao is None:
        raise ErroDeNegocio(MSG_NAO_APTO)

    # RN4 — no máximo um voto por proprietário por votação
    if participacao["data_hora_participacao"] is not None:
        raise ErroDeNegocio(MSG_JA_VOTOU)

    opcao = opcao_voto.buscar_por_id(conexao, opcao_voto_id)
    if opcao is None or opcao["votacao_id"] != votacao_id:
        raise ErroDeNegocio("Opção de voto inválida")

    agora = datetime.now().isoformat(timespec="seconds")

    # RN4 — marcação atômica da participação: se outra requisição do mesmo
    # proprietário chegou primeiro, o UPDATE afeta 0 linhas e o voto é negado.
    if not participacao_votacao.registrar_participacao(
            conexao, votacao_id, usuario_id, agora):
        conexao.rollback()
        raise ErroDeNegocio(MSG_JA_VOTOU)

    # RN1 — o peso computado é o peso FIXADO no Iniciar, não o atual.
    # RN5 — em votação ABERTA o voto referencia o usuário; em FECHADA fica
    # NULL (e o trigger do banco garante isso mesmo contra erros de código).
    usuario_no_voto = (usuario_id
                       if registro["visibilidade"] == Visibilidade.ABERTA
                       else None)
    try:
        voto.inserir(conexao, agora, participacao["peso_fixado"],
                     votacao_id, opcao_voto_id, usuario_no_voto)
    except sqlite3.IntegrityError:
        conexao.rollback()
        raise ErroDeNegocio(MSG_JA_VOTOU)

    conexao.commit()
    return participacao["peso_fixado"]
