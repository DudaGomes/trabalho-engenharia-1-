"""UC1 — Autenticação de Usuários (RF9, RNF4).

Verifica e-mail e senha contra um cadastro ATIVO e identifica o perfil.
"""

from werkzeug.security import check_password_hash

from src.casos_de_uso.erros import ErroDeNegocio
from src.config.constantes import MSG_LOGIN_INVALIDO
from src.modelos import usuario as modelo_usuario


def entrar(conexao, email, senha):
    """UC1 fluxo principal — retorna o usuário autenticado (linha de usuario).

    Fluxo alternativo Credenciais Inválidas: qualquer falha (e-mail
    inexistente, usuário inativo ou senha errada) gera a MESMA mensagem,
    "E-mail ou senha incorretos", sem revelar qual campo errou (RNF4).
    """
    email = (email or "").strip().lower()
    senha = senha or ""

    registro = modelo_usuario.buscar_por_email(conexao, email)
    if (registro is None
            or not registro["ativo"]
            or not check_password_hash(registro["senha_hash"], senha)):
        raise ErroDeNegocio(MSG_LOGIN_INVALIDO)

    return registro
