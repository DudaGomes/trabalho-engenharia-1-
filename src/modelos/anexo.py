"""Modelo Anexo — acesso a dados da entidade Anexo (ERSw 3.5).

O upload/download de PDF (RF4/RF8) está fora do recorte; a entidade existe
para manter o esquema fiel à ERSw e dar contexto à pauta do seed.
"""


def inserir(conexao, nome_arquivo, item_pauta_id):
    cursor = conexao.execute(
        "INSERT INTO anexo (nome_arquivo, item_pauta_id) VALUES (?, ?)",
        (nome_arquivo, item_pauta_id),
    )
    return cursor.lastrowid


def listar_por_item(conexao, item_pauta_id):
    return conexao.execute(
        "SELECT * FROM anexo WHERE item_pauta_id = ? ORDER BY id",
        (item_pauta_id,),
    ).fetchall()
