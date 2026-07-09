"""Rotas do UC1 — mapeamento URL → caso de uso, sem regra de negócio.

GET  /login  → Tela Inicial — Login
POST /login  → caso de uso entrar; sucesso cria sessão e direciona ao painel
POST /sair   → encerra a sessão
GET  /painel → painel do perfil (reunião, pauta e votações)
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.casos_de_uso.erros import ErroDeNegocio
from src.casos_de_uso.uc1_autenticacao import entrar as uc_entrar
from src.config import banco, sessao
from src.modelos import anexo, item_pauta, lote, reuniao, votacao

bp = Blueprint("autenticacao", __name__)


@bp.get("/login")
def tela_login():
    if sessao.usuario_da_sessao():
        return redirect(url_for("autenticacao.painel"))
    return render_template("login.html")


@bp.post("/login")
def autenticar():
    conexao = banco.obter_conexao()
    try:
        usuario = uc_entrar.entrar(
            conexao, request.form.get("email"), request.form.get("senha"))
    except ErroDeNegocio as erro:
        flash(erro.mensagem, "erro")
        return render_template("login.html", email=request.form.get("email", "")), 401
    finally:
        conexao.close()

    sessao.iniciar_sessao(usuario)
    return redirect(url_for("autenticacao.painel"))


@bp.post("/sair")
def sair():
    sessao.encerrar_sessao()
    return redirect(url_for("autenticacao.tela_login"))


@bp.get("/painel")
@sessao.exige_login
def painel():
    """Painel pós-login: a reunião do seed, sua pauta e suas votações."""
    usuario = sessao.usuario_da_sessao()
    conexao = banco.obter_conexao()
    try:
        reunioes = reuniao.listar(conexao)
        reuniao_atual = reunioes[0] if reunioes else None
        itens = []
        votacoes = []
        peso_do_usuario = None
        if reuniao_atual:
            itens = [
                {
                    "item": item,
                    "anexos": anexo.listar_por_item(conexao, item["id"]),
                }
                for item in item_pauta.listar_por_reuniao(conexao, reuniao_atual["id"])
            ]
            votacoes = votacao.listar_por_reuniao(conexao, reuniao_atual["id"])
        if usuario["tipo"] == "PROPRIETARIO":
            lotes = lote.listar_por_usuario(conexao, usuario["id"])
            peso_do_usuario = {
                "lotes": "; ".join(l["identificacao"] for l in lotes) or "nenhum lote",
                "peso": sum(l["peso"] for l in lotes),
            }
    finally:
        conexao.close()

    return render_template(
        "painel.html",
        reuniao=reuniao_atual, itens=itens, votacoes=votacoes,
        peso_do_usuario=peso_do_usuario)
