"""Ponto de entrada do PAC — cria o app Flask, sessão, rotas e telas.

Uso:  python3 src/servidor.py   (ou python3 -m src.servidor, da raiz)
"""

import sys
from pathlib import Path

# permite executar o arquivo diretamente de qualquer diretório
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, redirect, url_for

from src.config import sessao
from src.config.constantes import StatusVotacao, TipoResposta, Visibilidade
from src.rotas.autenticacao import bp as bp_autenticacao
from src.rotas.resultados import bp as bp_resultados
from src.rotas.votacoes import bp as bp_votacoes

RAIZ = Path(__file__).resolve().parent


def criar_app():
    app = Flask(
        "pac",
        template_folder=str(RAIZ / "telas"),
        static_folder=str(RAIZ / "publico"),
        static_url_path="/publico",
    )
    sessao.configurar(app)

    app.register_blueprint(bp_autenticacao)
    app.register_blueprint(bp_votacoes)
    app.register_blueprint(bp_resultados)

    # rótulos e sessão disponíveis em todas as telas
    @app.context_processor
    def contexto_global():
        return {
            "usuario_logado": sessao.usuario_da_sessao(),
            "ROTULOS_TIPO": TipoResposta.ROTULOS,
            "ROTULOS_VISIBILIDADE": Visibilidade.ROTULOS,
            "StatusVotacao": StatusVotacao,
        }

    @app.template_filter("peso_br")
    def peso_br(valor):
        """2.4 → '2,40' (formato decimal brasileiro usado nos protótipos)."""
        return f"{float(valor):.2f}".replace(".", ",")

    @app.template_filter("data_br")
    def data_br(data_iso):
        """2026-07-12 → 12/07/2026 (formato dd/mm/aaaa da ERSw)."""
        try:
            ano, mes, dia = str(data_iso).split("-")
            return f"{dia}/{mes}/{ano}"
        except ValueError:
            return data_iso

    @app.get("/")
    def inicio():
        if sessao.usuario_da_sessao():
            return redirect(url_for("autenticacao.painel"))
        return redirect(url_for("autenticacao.tela_login"))

    return app


if __name__ == "__main__":
    criar_app().run(debug=True, port=5001)
