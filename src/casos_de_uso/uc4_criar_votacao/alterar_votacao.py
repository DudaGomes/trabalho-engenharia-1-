"""UC4 — Configuração de Votações (RF5): alterar votação configurada.

RN3 — a alteração é permitida SOMENTE enquanto o status é CONFIGURADA;
votação iniciada não pode mais ser alterada.
"""

from src.casos_de_uso.erros import ErroDeNegocio
from src.casos_de_uso.uc4_criar_votacao.validacoes import validar_configuracao
from src.config.constantes import StatusVotacao
from src.modelos import opcao_voto, votacao


def alterar(conexao, votacao_id, pergunta, tipo_resposta, visibilidade,
            duracao, quorum_texto, opcoes_texto, item_pauta_id=None):
    registro = votacao.buscar_por_id(conexao, votacao_id)
    if registro is None:
        raise ErroDeNegocio("Votação não encontrada")

    # RN3 — impede a alteração após a votação ter sido iniciada
    if registro["status"] != StatusVotacao.CONFIGURADA:
        raise ErroDeNegocio("Votação iniciada não pode ser alterada")

    dados = validar_configuracao(
        pergunta, tipo_resposta, visibilidade, duracao, quorum_texto, opcoes_texto)

    votacao.atualizar(
        conexao, votacao_id, dados["pergunta"], dados["tipo_resposta"],
        dados["visibilidade"], dados["duracao"], dados["quorum_minimo"],
        item_pauta_id or None)
    # substitui o conjunto de opções pelo novo
    opcao_voto.excluir_por_votacao(conexao, votacao_id)
    for texto in dados["opcoes"]:
        opcao_voto.inserir(conexao, texto, votacao_id)

    conexao.commit()
