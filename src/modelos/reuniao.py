"""Modelo Reuniao — acesso a dados da entidade Reuniao (ERSw 3.5)."""


def inserir(conexao, titulo, data, horario, local, status="AGENDADA"):
    cursor = conexao.execute(
        "INSERT INTO reuniao (titulo, data, horario, local, status) "
        "VALUES (?, ?, ?, ?, ?)",
        (titulo, data, horario, local, status),
    )
    return cursor.lastrowid


def buscar_por_id(conexao, reuniao_id):
    return conexao.execute(
        "SELECT * FROM reuniao WHERE id = ?", (reuniao_id,)
    ).fetchone()


def listar(conexao):
    return conexao.execute(
        "SELECT * FROM reuniao ORDER BY data, horario"
    ).fetchall()
