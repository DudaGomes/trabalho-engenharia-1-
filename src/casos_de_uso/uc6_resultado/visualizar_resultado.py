"""UC6 — Apuração e Resultado da Votação (RF7): visualizar resultado.

RN5 — Visibilidade e sigilo:
  • ABERTA: o resultado pode exibir a relação nominal (proprietário, lotes,
    voto e peso);
  • FECHADA: o resultado exibe a apuração consolidada e a relação de
    participantes (lotes, peso e horário) SEM a escolha de ninguém — a
    associação nem existe no banco (voto.usuario_id é NULL).
"""

from src.casos_de_uso.uc6_resultado.apurar import apurar
from src.config.constantes import (StatusResultado, TipoResposta,
                                   Visibilidade)
from src.modelos import (lote, opcao_voto, participacao_votacao, votacao,
                         voto)


def _rotulo_final(registro, resultado, vencedora):
    """RN6 — apresentação do resultado: 'Aprovado'/'Rejeitado' em
    Sim/Não/Abstenção; texto da opção ou nome nos demais tipos."""
    if resultado["status"] == StatusResultado.SEM_QUORUM:
        return "Sem quórum"
    if resultado["status"] == StatusResultado.EMPATE:
        return "Empate"
    if registro["tipo_resposta"] == TipoResposta.SIM_NAO_ABSTENCAO:
        if vencedora["texto"] == "Sim":
            return "Aprovado"
        if vencedora["texto"] == "Não":
            return "Rejeitado"
    return vencedora["texto"]


def montar(conexao, votacao_id):
    """Apura (se necessário) e devolve todos os dados da tela de resultado,
    conforme a visibilidade da votação."""
    resultado = apurar(conexao, votacao_id)
    registro = votacao.buscar_por_id(conexao, votacao_id)

    vencedora = (opcao_voto.buscar_por_id(conexao, resultado["opcao_vencedora_id"])
                 if resultado["opcao_vencedora_id"] else None)

    # apuração por opção com % por peso sobre o peso participante
    apuracao = []
    empatadas = []
    maior_peso = None
    peso_participante = resultado["peso_participante"]
    for opcao in voto.apuracao_por_opcao(conexao, votacao_id):
        percentual = (100.0 * opcao["peso_total"] / peso_participante
                      if peso_participante > 0 else 0.0)
        apuracao.append({
            "texto": opcao["texto"],
            "quantidade": opcao["quantidade_votos"],
            "peso": opcao["peso_total"],
            "percentual": percentual,
        })
    if resultado["status"] == StatusResultado.EMPATE:
        pesos = [o["peso"] for o in apuracao]
        maior_peso = max(pesos) if pesos else 0
        empatadas = [o["texto"] for o in apuracao if o["peso"] == maior_peso]

    visao = {
        "votacao": registro,
        "resultado": resultado,
        "vencedora": vencedora,
        "rotulo_final": _rotulo_final(registro, resultado, vencedora),
        "apuracao": apuracao,
        "empatadas": empatadas,
        "quorum_atingido": resultado["status"] != StatusResultado.SEM_QUORUM,
    }

    if registro["visibilidade"] == Visibilidade.ABERTA:
        # RN5 — relação nominal permitida SOMENTE na votação aberta
        visao["relacao_nominal"] = [
            {
                "nome": linha["nome"],
                "lotes": lote.identificacoes_por_usuario(
                    conexao, linha["usuario_id"]),
                "voto": linha["voto"],
                "peso": linha["peso_computado"],
            }
            for linha in voto.relacao_nominal(conexao, votacao_id)
        ]
    else:
        # RN5 — participantes com lotes, peso e horário, SEM a escolha
        visao["participantes"] = [
            {
                "nome": linha["nome"],
                "lotes": lote.identificacoes_por_usuario(
                    conexao, linha["usuario_id"]),
                "peso": linha["peso_fixado"],
                "horario": (linha["data_hora_participacao"] or "")[11:16],
            }
            for linha in participacao_votacao.listar_por_votacao(
                conexao, votacao_id)
            if linha["data_hora_participacao"] is not None
        ]

    return visao
