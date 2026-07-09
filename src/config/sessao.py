"""Configuração da sessão do Flask e proteção de rotas por perfil.

UC1 — o PAC cria a sessão de acesso vinculada ao usuário autenticado e
direciona cada perfil às suas funcionalidades. Os decorators abaixo são
aplicados nas ROTAS (camada de apresentação) antes de qualquer caso de uso.
"""

from functools import wraps

from flask import redirect, session, url_for

from src.config.constantes import TipoUsuario


def configurar(app):
    # Chave fixa de desenvolvimento — suficiente para o escopo acadêmico
    app.secret_key = "pac-chave-de-desenvolvimento-nao-usar-em-producao"
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,   # cookie inacessível a JavaScript
        SESSION_COOKIE_SAMESITE="Lax",
    )


def usuario_da_sessao():
    """Retorna (id, nome, tipo) do usuário logado ou None."""
    if "usuario_id" not in session:
        return None
    return {
        "id": session["usuario_id"],
        "nome": session["usuario_nome"],
        "tipo": session["usuario_tipo"],
    }


def iniciar_sessao(usuario):
    """UC1 — cria a sessão de acesso vinculada ao Usuário autenticado."""
    session.clear()
    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    session["usuario_tipo"] = usuario["tipo"]


def encerrar_sessao():
    session.clear()


def exige_login(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if usuario_da_sessao() is None:
            return redirect(url_for("autenticacao.tela_login"))
        return funcao(*args, **kwargs)
    return protegida


def exige_admin(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        usuario = usuario_da_sessao()
        if usuario is None:
            return redirect(url_for("autenticacao.tela_login"))
        if usuario["tipo"] != TipoUsuario.ADMINISTRADOR:
            return redirect(url_for("autenticacao.painel"))
        return funcao(*args, **kwargs)
    return protegida


def exige_proprietario(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        usuario = usuario_da_sessao()
        if usuario is None:
            return redirect(url_for("autenticacao.tela_login"))
        if usuario["tipo"] != TipoUsuario.PROPRIETARIO:
            return redirect(url_for("autenticacao.painel"))
        return funcao(*args, **kwargs)
    return protegida
