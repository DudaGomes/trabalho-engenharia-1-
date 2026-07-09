"""UC4 — Configuração de Votações (RF5): criar votação.

RN3 — Liberação: Salvar mantém o status CONFIGURADA e NÃO libera a votação;
somente o comando Iniciar (UC5) a torna ATIVA.
"""

from src.casos_de_uso.uc4_criar_votacao.validacoes import validar_configuracao
from src.modelos import opcao_voto, votacao


def criar(conexao, reuniao_id, pergunta, tipo_resposta, visibilidade,
          duracao, quorum_texto, opcoes_texto, item_pauta_id=None):
    """Valida (RN7/RN8) e salva a votação com status CONFIGURADA (RN3),
    junto de suas 2..* opções, na mesma transação."""
    dados = validar_configuracao(
        pergunta, tipo_resposta, visibilidade, duracao, quorum_texto, opcoes_texto)

    votacao_id = votacao.inserir(
        conexao, dados["pergunta"], dados["tipo_resposta"],
        dados["visibilidade"], dados["duracao"], dados["quorum_minimo"],
        reuniao_id, item_pauta_id or None)
    for texto in dados["opcoes"]:
        opcao_voto.inserir(conexao, texto, votacao_id)

    conexao.commit()
    return votacao_id
