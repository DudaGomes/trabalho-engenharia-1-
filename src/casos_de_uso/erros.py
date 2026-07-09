"""Erro de negócio: violação de regra da ERSw detectada por um caso de uso.

As rotas capturam este erro e exibem a mensagem ao usuário — as mensagens
oficiais vivem em config/constantes.py, com o texto exato da ERSw.
"""


class ErroDeNegocio(Exception):
    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem
