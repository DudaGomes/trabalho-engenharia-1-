"""Modelo Usuario — acesso a dados da entidade Usuario (ERSw 3.5).

O usuário NÃO possui peso próprio: o peso de voto deriva dos lotes (RN1).
"""


def inserir(conexao, nome, email, senha_hash, telefone, tipo, ativo=True):
    cursor = conexao.execute(
        "INSERT INTO usuario (nome, email, senha_hash, telefone, tipo, ativo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (nome, email, senha_hash, telefone, tipo, 1 if ativo else 0),
    )
    return cursor.lastrowid


def buscar_por_email(conexao, email):
    return conexao.execute(
        "SELECT * FROM usuario WHERE email = ?", (email,)
    ).fetchone()


def buscar_por_id(conexao, usuario_id):
    return conexao.execute(
        "SELECT * FROM usuario WHERE id = ?", (usuario_id,)
    ).fetchone()


def listar_aptos_com_peso(conexao):
    """RN2 — Aptidão: proprietários ATIVOS com ao menos 1 lote vinculado,
    já com o peso total calculado pela soma dos pesos de seus lotes (RN1).

    Esta consulta é a "fotografia" usada pelo caso de uso Iniciar (UC5)
    para congelar a lista de aptos em participacao_votacao.
    """
    return conexao.execute(
        """
        SELECT u.id, u.nome, SUM(l.peso) AS peso_total
          FROM usuario u
          JOIN lote l ON l.usuario_id = u.id
         WHERE u.tipo = 'PROPRIETARIO' AND u.ativo = 1
         GROUP BY u.id, u.nome
        HAVING COUNT(l.id) >= 1
         ORDER BY u.nome
        """
    ).fetchall()
