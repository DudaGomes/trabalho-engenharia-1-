"""Modelo OpcaoVoto — acesso a dados da entidade OpcaoVoto (ERSw 3.5).

Cada opção pertence a exatamente 1 votação; toda votação tem 2..* opções.
"""


def inserir(conexao, texto, votacao_id):
    cursor = conexao.execute(
        "INSERT INTO opcao_voto (texto, votacao_id) VALUES (?, ?)",
        (texto, votacao_id),
    )
    return cursor.lastrowid


def listar_por_votacao(conexao, votacao_id):
    return conexao.execute(
        "SELECT * FROM opcao_voto WHERE votacao_id = ? ORDER BY id",
        (votacao_id,),
    ).fetchall()


def buscar_por_id(conexao, opcao_id):
    return conexao.execute(
        "SELECT * FROM opcao_voto WHERE id = ?", (opcao_id,)
    ).fetchone()


def excluir_por_votacao(conexao, votacao_id):
    """Usado ao alterar uma votação CONFIGURADA (substitui as opções)."""
    conexao.execute("DELETE FROM opcao_voto WHERE votacao_id = ?", (votacao_id,))
