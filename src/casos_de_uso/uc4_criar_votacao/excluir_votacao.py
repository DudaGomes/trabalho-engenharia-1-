"""UC4 — Configuração de Votações (RF5): excluir votação configurada.

RN3 — a exclusão é permitida SOMENTE enquanto o status é CONFIGURADA;
votação iniciada não pode mais ser excluída.
"""

from src.casos_de_uso.erros import ErroDeNegocio
from src.config.constantes import StatusVotacao
from src.modelos import votacao


def excluir(conexao, votacao_id):
    registro = votacao.buscar_por_id(conexao, votacao_id)
    if registro is None:
        raise ErroDeNegocio("Votação não encontrada")

    # RN3 — impede a exclusão após a votação ter sido iniciada
    if registro["status"] != StatusVotacao.CONFIGURADA:
        raise ErroDeNegocio("Votação iniciada não pode ser excluída")

    votacao.excluir(conexao, votacao_id)  # opções saem por ON DELETE CASCADE
    conexao.commit()
