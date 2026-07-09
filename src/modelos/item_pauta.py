"""Modelo ItemPauta — acesso a dados da entidade ItemPauta (ERSw 3.5)."""


def inserir(conexao, titulo, descricao, reuniao_id):
    cursor = conexao.execute(
        "INSERT INTO item_pauta (titulo, descricao, reuniao_id) VALUES (?, ?, ?)",
        (titulo, descricao, reuniao_id),
    )
    return cursor.lastrowid


def listar_por_reuniao(conexao, reuniao_id):
    return conexao.execute(
        "SELECT * FROM item_pauta WHERE reuniao_id = ? ORDER BY id",
        (reuniao_id,),
    ).fetchall()
