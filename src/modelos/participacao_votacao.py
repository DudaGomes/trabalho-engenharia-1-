"""Modelo ParticipacaoVotacao — acesso a dados da entidade (ERSw 3.5).

Fixa os aptos e seus pesos no Iniciar (RN1/RN2) e registra QUEM participou
(data_hora_participacao) sem NUNCA referenciar OpcaoVoto (RN5).
A UNIQUE (votacao_id, usuario_id) reforça o voto único (RN4) no banco.
"""


def fixar_apto(conexao, votacao_id, usuario_id, peso_fixado):
    """RN2 — materializa um proprietário apto com seu peso congelado (RN1)."""
    cursor = conexao.execute(
        """
        INSERT INTO participacao_votacao (peso_fixado, votacao_id, usuario_id)
        VALUES (?, ?, ?)
        """,
        (peso_fixado, votacao_id, usuario_id),
    )
    return cursor.lastrowid


def buscar(conexao, votacao_id, usuario_id):
    return conexao.execute(
        "SELECT * FROM participacao_votacao WHERE votacao_id = ? AND usuario_id = ?",
        (votacao_id, usuario_id),
    ).fetchone()


def registrar_participacao(conexao, votacao_id, usuario_id, data_hora):
    """RN4 — marca a participação de forma atômica: o UPDATE só afeta a linha
    se data_hora_participacao ainda for NULL. Retorna False quando o
    proprietário já havia votado (0 linhas afetadas)."""
    cursor = conexao.execute(
        """
        UPDATE participacao_votacao
           SET data_hora_participacao = ?
         WHERE votacao_id = ? AND usuario_id = ?
           AND data_hora_participacao IS NULL
        """,
        (data_hora, votacao_id, usuario_id),
    )
    return cursor.rowcount == 1


def listar_por_votacao(conexao, votacao_id):
    return conexao.execute(
        """
        SELECT p.*, u.nome
          FROM participacao_votacao p
          JOIN usuario u ON u.id = p.usuario_id
         WHERE p.votacao_id = ?
         ORDER BY u.nome
        """,
        (votacao_id,),
    ).fetchall()


def totais(conexao, votacao_id):
    """RN6 — pesos para o quórum: peso total apto (todos os congelados) e
    peso participante (apenas quem já votou)."""
    return conexao.execute(
        """
        SELECT COALESCE(SUM(peso_fixado), 0) AS peso_total_apto,
               COALESCE(SUM(CASE WHEN data_hora_participacao IS NOT NULL
                                 THEN peso_fixado ELSE 0 END), 0) AS peso_participante,
               COUNT(*) AS total_aptos,
               SUM(CASE WHEN data_hora_participacao IS NOT NULL THEN 1 ELSE 0 END)
                   AS total_votaram
          FROM participacao_votacao
         WHERE votacao_id = ?
        """,
        (votacao_id,),
    ).fetchone()
