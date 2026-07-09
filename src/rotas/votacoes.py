"""Rotas de votação — mapeamento URL → casos de uso UC4 e UC5.

Nenhuma regra de negócio aqui: as rotas coletam o formulário, chamam o caso
de uso e traduzem ErroDeNegocio em mensagem na tela.
"""

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from src.casos_de_uso.erros import ErroDeNegocio
from src.casos_de_uso.uc4_criar_votacao import (alterar_votacao,
                                                criar_votacao,
                                                excluir_votacao)
from src.casos_de_uso.uc5_executar_votacao import encerrar as uc_encerrar
from src.casos_de_uso.uc5_executar_votacao import iniciar as uc_iniciar
from src.casos_de_uso.uc5_executar_votacao import votar as uc_votar
from src.config import banco, sessao
from src.modelos import (item_pauta, lote, opcao_voto, participacao_votacao,
                         reuniao, votacao)

bp = Blueprint("votacoes", __name__)


def _dados_do_formulario():
    return {
        "pergunta": request.form.get("pergunta", ""),
        "tipo_resposta": request.form.get("tipo_resposta", ""),
        "visibilidade": request.form.get("visibilidade", ""),
        "duracao": request.form.get("duracao", ""),
        "quorum_texto": request.form.get("quorum_minimo", ""),
        "opcoes_texto": request.form.get("opcoes", ""),
        "item_pauta_id": request.form.get("item_pauta_id") or None,
    }


def _renderizar_configuracao(conexao, reuniao_id, formulario=None,
                             votacao_em_edicao=None):
    """Tela de Configuração de Votação + lista 'Votações Configuradas'.
    O comando Iniciar fica na LISTA, fora do formulário (RN3)."""
    reuniao_atual = reuniao.buscar_por_id(conexao, reuniao_id)
    itens = item_pauta.listar_por_reuniao(conexao, reuniao_id)
    votacoes = votacao.listar_por_reuniao(conexao, reuniao_id)
    return render_template(
        "uc4_configurar_votacao.html",
        reuniao=reuniao_atual, itens=itens, votacoes=votacoes,
        formulario=formulario or {}, votacao_em_edicao=votacao_em_edicao)


@bp.get("/reunioes/<int:reuniao_id>/votacoes/nova")
@sessao.exige_admin
def tela_nova(reuniao_id):
    conexao = banco.obter_conexao()
    try:
        return _renderizar_configuracao(conexao, reuniao_id)
    finally:
        conexao.close()


@bp.post("/reunioes/<int:reuniao_id>/votacoes")
@sessao.exige_admin
def criar(reuniao_id):
    formulario = _dados_do_formulario()
    conexao = banco.obter_conexao()
    try:
        criar_votacao.criar(
            conexao, reuniao_id,
            formulario["pergunta"], formulario["tipo_resposta"],
            formulario["visibilidade"], formulario["duracao"],
            formulario["quorum_texto"], formulario["opcoes_texto"],
            formulario["item_pauta_id"])
        flash("Votação salva com status Configurada — use Iniciar para liberá-la",
              "sucesso")
        return redirect(url_for("votacoes.tela_nova", reuniao_id=reuniao_id))
    except ErroDeNegocio as erro:
        # fluxo alternativo Campos Inválidos: mantém os dados já preenchidos
        flash(erro.mensagem, "erro")
        return _renderizar_configuracao(conexao, reuniao_id, formulario), 400
    finally:
        conexao.close()


@bp.get("/votacoes/<int:votacao_id>/editar")
@sessao.exige_admin
def tela_editar(votacao_id):
    conexao = banco.obter_conexao()
    try:
        registro = votacao.buscar_por_id(conexao, votacao_id)
        if registro is None:
            flash("Votação não encontrada", "erro")
            return redirect(url_for("autenticacao.painel"))
        if registro["status"] != "CONFIGURADA":
            flash("Votação iniciada não pode ser alterada", "erro")
            return redirect(url_for("votacoes.tela_nova",
                                    reuniao_id=registro["reuniao_id"]))
        opcoes = opcao_voto.listar_por_votacao(conexao, votacao_id)
        formulario = {
            "pergunta": registro["pergunta"],
            "tipo_resposta": registro["tipo_resposta"],
            "visibilidade": registro["visibilidade"],
            "duracao": registro["duracao"],
            "quorum_texto": (f"{registro['quorum_minimo']:g}"
                             if registro["quorum_minimo"] else ""),
            "opcoes_texto": "\n".join(o["texto"] for o in opcoes),
            "item_pauta_id": registro["item_pauta_id"],
        }
        return _renderizar_configuracao(
            conexao, registro["reuniao_id"], formulario,
            votacao_em_edicao=registro)
    finally:
        conexao.close()


@bp.post("/votacoes/<int:votacao_id>/atualizar")
@sessao.exige_admin
def atualizar(votacao_id):
    formulario = _dados_do_formulario()
    conexao = banco.obter_conexao()
    try:
        registro = votacao.buscar_por_id(conexao, votacao_id)
        if registro is None:
            flash("Votação não encontrada", "erro")
            return redirect(url_for("autenticacao.painel"))
        alterar_votacao.alterar(
            conexao, votacao_id,
            formulario["pergunta"], formulario["tipo_resposta"],
            formulario["visibilidade"], formulario["duracao"],
            formulario["quorum_texto"], formulario["opcoes_texto"],
            formulario["item_pauta_id"])
        flash("Votação alterada — permanece Configurada até o Iniciar", "sucesso")
        return redirect(url_for("votacoes.tela_nova",
                                reuniao_id=registro["reuniao_id"]))
    except ErroDeNegocio as erro:
        flash(erro.mensagem, "erro")
        return _renderizar_configuracao(
            conexao, registro["reuniao_id"], formulario,
            votacao_em_edicao=registro), 400
    finally:
        conexao.close()


@bp.post("/votacoes/<int:votacao_id>/excluir")
@sessao.exige_admin
def excluir(votacao_id):
    conexao = banco.obter_conexao()
    try:
        registro = votacao.buscar_por_id(conexao, votacao_id)
        if registro is None:
            flash("Votação não encontrada", "erro")
            return redirect(url_for("autenticacao.painel"))
        excluir_votacao.excluir(conexao, votacao_id)
        flash("Votação excluída", "sucesso")
    except ErroDeNegocio as erro:
        flash(erro.mensagem, "erro")
    finally:
        conexao.close()
    return redirect(url_for("votacoes.tela_nova",
                            reuniao_id=registro["reuniao_id"]))


# ── UC5 — Execução de Votação ───────────────────────────────────────────────

@bp.post("/votacoes/<int:votacao_id>/iniciar")
@sessao.exige_admin
def iniciar(votacao_id):
    """Comando Iniciar: congela aptos/pesos e libera a votação (RN1/RN2/RN3)."""
    conexao = banco.obter_conexao()
    try:
        total_aptos = uc_iniciar.iniciar(conexao, votacao_id)
        flash(f"Votação iniciada — {total_aptos} proprietários aptos com pesos "
              "congelados", "sucesso")
        return redirect(url_for("votacoes.conducao", votacao_id=votacao_id))
    except ErroDeNegocio as erro:
        flash(erro.mensagem, "erro")
        registro = votacao.buscar_por_id(conexao, votacao_id)
        destino = (url_for("votacoes.tela_nova", reuniao_id=registro["reuniao_id"])
                   if registro else url_for("autenticacao.painel"))
        return redirect(destino)
    finally:
        conexao.close()


@bp.get("/votacoes/<int:votacao_id>/conducao")
@sessao.exige_admin
def conducao(votacao_id):
    """Tela de Condução da Votação (protótipo do UC5): pesos, votaram/não
    votaram e cronômetro."""
    conexao = banco.obter_conexao()
    try:
        registro = votacao.buscar_por_id(conexao, votacao_id)
        if registro is None:
            flash("Votação não encontrada", "erro")
            return redirect(url_for("autenticacao.painel"))
        # RN8 — encerramento automático ao carregar, se o tempo já zerou
        if uc_encerrar.encerrar_se_tempo_esgotado(conexao, registro):
            registro = votacao.buscar_por_id(conexao, votacao_id)
        totais = participacao_votacao.totais(conexao, votacao_id)
        return render_template(
            "uc5_conducao_admin.html",
            votacao=registro, totais=totais,
            segundos_restantes=uc_encerrar.segundos_restantes(registro))
    finally:
        conexao.close()


@bp.post("/votacoes/<int:votacao_id>/encerrar")
@sessao.exige_admin
def encerrar(votacao_id):
    """RN8 — encerramento manual pelo administrador."""
    conexao = banco.obter_conexao()
    try:
        uc_encerrar.encerrar_manual(conexao, votacao_id)
        flash("Votação encerrada pelo administrador", "sucesso")
    except ErroDeNegocio as erro:
        flash(erro.mensagem, "erro")
    finally:
        conexao.close()
    return redirect(url_for("votacoes.conducao", votacao_id=votacao_id))


@bp.get("/votacoes/<int:votacao_id>/votar")
@sessao.exige_proprietario
def tela_votar(votacao_id):
    """Tela de Votação em Andamento (protótipo do UC5): pergunta, cronômetro,
    'Peso do seu voto' e opções."""
    usuario = sessao.usuario_da_sessao()
    conexao = banco.obter_conexao()
    try:
        registro = votacao.buscar_por_id(conexao, votacao_id)
        if registro is None:
            flash("Votação não encontrada", "erro")
            return redirect(url_for("autenticacao.painel"))
        # RN8 — encerramento automático ao carregar, se o tempo já zerou
        if uc_encerrar.encerrar_se_tempo_esgotado(conexao, registro):
            registro = votacao.buscar_por_id(conexao, votacao_id)
        participacao = participacao_votacao.buscar(
            conexao, votacao_id, usuario["id"])
        return render_template(
            "uc5_votacao_proprietario.html",
            votacao=registro,
            opcoes=opcao_voto.listar_por_votacao(conexao, votacao_id),
            participacao=participacao,
            lotes=lote.identificacoes_por_usuario(conexao, usuario["id"]),
            segundos_restantes=uc_encerrar.segundos_restantes(registro))
    finally:
        conexao.close()


@bp.post("/votacoes/<int:votacao_id>/votar")
@sessao.exige_proprietario
def confirmar_voto(votacao_id):
    """Comando Confirmar Voto — todos os fluxos de erro tratados no caso de uso."""
    usuario = sessao.usuario_da_sessao()
    conexao = banco.obter_conexao()
    try:
        peso = uc_votar.votar(
            conexao, votacao_id, usuario["id"],
            int(request.form.get("opcao_voto_id", 0)))
        flash(f"Voto confirmado com peso {peso:.2f}".replace(".", ","), "sucesso")
    except ErroDeNegocio as erro:
        flash(erro.mensagem, "erro")
    finally:
        conexao.close()
    return redirect(url_for("votacoes.tela_votar", votacao_id=votacao_id))


@bp.get("/votacoes/<int:votacao_id>/estado")
@sessao.exige_login
def estado(votacao_id):
    """Estado em tempo real (JSON) para o cronômetro e os indicadores das
    telas de condução e votação — apenas leitura, sem regra de negócio."""
    conexao = banco.obter_conexao()
    try:
        registro = votacao.buscar_por_id(conexao, votacao_id)
        if registro is None:
            return jsonify({"erro": "Votação não encontrada"}), 404
        # RN8 — o polling também dispara o encerramento automático
        if uc_encerrar.encerrar_se_tempo_esgotado(conexao, registro):
            registro = votacao.buscar_por_id(conexao, votacao_id)
        totais = participacao_votacao.totais(conexao, votacao_id)
        return jsonify({
            "status": registro["status"],
            "segundos_restantes": uc_encerrar.segundos_restantes(registro),
            "peso_total_apto": totais["peso_total_apto"],
            "peso_participante": totais["peso_participante"],
            "votaram": totais["total_votaram"],
            "nao_votaram": totais["total_aptos"] - totais["total_votaram"],
        })
    finally:
        conexao.close()
