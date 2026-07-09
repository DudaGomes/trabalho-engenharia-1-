"""Modelo Votacao — acesso a dados da entidade Votacao (ERSw 3.5)."""


def inserir(conexao, pergunta, tipo_resposta, visibilidade, duracao,
            quorum_minimo, reuniao_id, item_pauta_id=None):
    cursor = conexao.execute(
        """
        INSERT INTO votacao (pergunta, tipo_resposta, visibilidade, duracao,
                             quorum_minimo, status, reuniao_id, item_pauta_id)
        VALUES (?, ?, ?, ?, ?, 'CONFIGURADA', ?, ?)
        """,
        (pergunta, tipo_resposta, visibilidade, duracao,
         quorum_minimo, reuniao_id, item_pauta_id),
    )
    return cursor.lastrowid


def atualizar(conexao, votacao_id, pergunta, tipo_resposta, visibilidade,
              duracao, quorum_minimo, item_pauta_id=None):
    conexao.execute(
        """
        UPDATE votacao
           SET pergunta = ?, tipo_resposta = ?, visibilidade = ?,
               duracao = ?, quorum_minimo = ?, item_pauta_id = ?
         WHERE id = ?
        """,
        (pergunta, tipo_resposta, visibilidade, duracao,
         quorum_minimo, item_pauta_id, votacao_id),
    )


def excluir(conexao, votacao_id):
    # ON DELETE CASCADE remove as opções junto
    conexao.execute("DELETE FROM votacao WHERE id = ?", (votacao_id,))


def buscar_por_id(conexao, votacao_id):
    return conexao.execute(
        "SELECT * FROM votacao WHERE id = ?", (votacao_id,)
    ).fetchone()


def listar_por_reuniao(conexao, reuniao_id):
    return conexao.execute(
        "SELECT * FROM votacao WHERE reuniao_id = ? ORDER BY id",
        (reuniao_id,),
    ).fetchall()


def buscar_ativa_na_reuniao(conexao, reuniao_id):
    """UC5 — não pode haver duas votações ATIVAS na mesma reunião."""
    return conexao.execute(
        "SELECT * FROM votacao WHERE reuniao_id = ? AND status = 'ATIVA'",
        (reuniao_id,),
    ).fetchone()


def ativar(conexao, votacao_id, data_inicio):
    """RN3 — somente o comando Iniciar muda o status para ATIVA."""
    conexao.execute(
        "UPDATE votacao SET status = 'ATIVA', data_inicio = ? WHERE id = ?",
        (data_inicio, votacao_id),
    )


def encerrar(conexao, votacao_id, data_encerramento):
    """RN8 — Encerrar (manual ou por tempo) muda o status para ENCERRADA."""
    conexao.execute(
        "UPDATE votacao SET status = 'ENCERRADA', data_encerramento = ? WHERE id = ?",
        (data_encerramento, votacao_id),
    )
