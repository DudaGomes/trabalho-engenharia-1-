"""Modelo Voto — acesso a dados da entidade Voto (ERSw 3.5).

O Voto sempre aponta para 1 Votacao e 1 OpcaoVoto. A referência a Usuario é
OPCIONAL e preenchida somente em votação ABERTA (RN5) — em FECHADA o campo
fica NULL e o trigger trg_sigilo_votacao_fechada rejeita qualquer tentativa
de gravá-lo preenchido.
"""


def inserir(conexao, data_hora, peso_computado, votacao_id, opcao_voto_id,
            usuario_id=None):
    cursor = conexao.execute(
        """
        INSERT INTO voto (data_hora, peso_computado, votacao_id,
                          opcao_voto_id, usuario_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (data_hora, peso_computado, votacao_id, opcao_voto_id, usuario_id),
    )
    return cursor.lastrowid


def apuracao_por_opcao(conexao, votacao_id):
    """RN6/RN7 — apuração ponderada: quantidade e soma de pesoComputado por
    opção, para todas as opções da votação (inclusive as sem votos)."""
    return conexao.execute(
        """
        SELECT o.id, o.texto,
               COUNT(v.id)                    AS quantidade_votos,
               COALESCE(SUM(v.peso_computado), 0) AS peso_total
          FROM opcao_voto o
          LEFT JOIN voto v ON v.opcao_voto_id = o.id
         WHERE o.votacao_id = ?
         GROUP BY o.id, o.texto
         ORDER BY o.id
        """,
        (votacao_id,),
    ).fetchall()


def relacao_nominal(conexao, votacao_id):
    """RN5 — SOMENTE para votação ABERTA: relação nominal com proprietário,
    voto e peso (o join por usuario_id só existe quando a votação é aberta)."""
    return conexao.execute(
        """
        SELECT u.id AS usuario_id, u.nome, o.texto AS voto,
               v.peso_computado, v.data_hora
          FROM voto v
          JOIN usuario u    ON u.id = v.usuario_id
          JOIN opcao_voto o ON o.id = v.opcao_voto_id
         WHERE v.votacao_id = ?
         ORDER BY u.nome
        """,
        (votacao_id,),
    ).fetchall()
