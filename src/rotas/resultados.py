"""Rotas do UC6 — mapeamento URL → caso de uso, sem regra de negócio.

GET /votacoes/<id>/resultado → apura (se preciso) e exibe a tela conforme
a visibilidade: Aberta (nominal) ou Fechada (participantes sem escolha).
"""

from flask import Blueprint, flash, redirect, render_template, url_for

from src.casos_de_uso.erros import ErroDeNegocio
from src.casos_de_uso.uc5_executar_votacao import encerrar as uc_encerrar
from src.casos_de_uso.uc6_resultado import visualizar_resultado
from src.config import banco, sessao
from src.config.constantes import Visibilidade
from src.modelos import votacao

bp = Blueprint("resultados", __name__)


@bp.get("/votacoes/<int:votacao_id>/resultado")
@sessao.exige_login
def resultado(votacao_id):
    conexao = banco.obter_conexao()
    try:
        registro = votacao.buscar_por_id(conexao, votacao_id)
        if registro is None:
            flash("Votação não encontrada", "erro")
            return redirect(url_for("autenticacao.painel"))

        # RN8 — se o tempo zerou, o encerramento automático acontece aqui também
        uc_encerrar.encerrar_se_tempo_esgotado(conexao, registro)

        try:
            visao = visualizar_resultado.montar(conexao, votacao_id)
        except ErroDeNegocio as erro:
            flash(erro.mensagem, "erro")
            return redirect(url_for("autenticacao.painel"))

        tela = ("uc6_resultado_aberta.html"
                if visao["votacao"]["visibilidade"] == Visibilidade.ABERTA
                else "uc6_resultado_fechada.html")
        return render_template(tela, **visao)
    finally:
        conexao.close()
