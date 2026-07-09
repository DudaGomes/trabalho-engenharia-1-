"""Modelo Lote — acesso a dados da entidade Lote (ERSw 3.5).

RN1 — o Lote é a fonte oficial do peso de voto: cada lote pertence a
exatamente 1 proprietário e carrega identificação, fração ideal e peso.
"""


def inserir(conexao, identificacao, fracao_ideal, peso, usuario_id):
    cursor = conexao.execute(
        "INSERT INTO lote (identificacao, fracao_ideal, peso, usuario_id) "
        "VALUES (?, ?, ?, ?)",
        (identificacao, fracao_ideal, peso, usuario_id),
    )
    return cursor.lastrowid


def listar_por_usuario(conexao, usuario_id):
    return conexao.execute(
        "SELECT * FROM lote WHERE usuario_id = ? ORDER BY identificacao",
        (usuario_id,),
    ).fetchall()


def identificacoes_por_usuario(conexao, usuario_id):
    """Ex.: 'Apt 202; Apt 203' — formato usado nas telas de resultado da ERSw."""
    linhas = listar_por_usuario(conexao, usuario_id)
    return "; ".join(linha["identificacao"] for linha in linhas) or "—"
