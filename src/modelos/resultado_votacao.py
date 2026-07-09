"""Modelo ResultadoVotacao — acesso a dados da entidade (ERSw 3.5).

Consolida status (CONCLUIDO | EMPATE | SEM_QUORUM), pesos, percentual de
participação, data da apuração e a opção vencedora opcional (RN6).
"""


def inserir(conexao, status, peso_total_apto, peso_participante,
            percentual_participacao, data_apuracao, votacao_id,
            opcao_vencedora_id=None):
    cursor = conexao.execute(
        """
        INSERT INTO resultado_votacao
               (status, peso_total_apto, peso_participante,
                percentual_participacao, data_apuracao, votacao_id,
                opcao_vencedora_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (status, peso_total_apto, peso_participante,
         percentual_participacao, data_apuracao, votacao_id,
         opcao_vencedora_id),
    )
    return cursor.lastrowid


def buscar_por_votacao(conexao, votacao_id):
    return conexao.execute(
        "SELECT * FROM resultado_votacao WHERE votacao_id = ?",
        (votacao_id,),
    ).fetchone()
