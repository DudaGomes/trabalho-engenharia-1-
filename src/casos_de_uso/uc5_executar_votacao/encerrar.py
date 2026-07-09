"""UC5 — Execução de Votação (RF6): encerramento e cronômetro (RN8).

RN8 — o cronômetro inicia no Iniciar; ao chegar a zero a votação é
encerrada automaticamente; o administrador pode encerrá-la manualmente
antes. Votação Encerrada não recebe novos votos.
"""

from datetime import datetime, timedelta

from src.casos_de_uso.erros import ErroDeNegocio
from src.casos_de_uso.uc4_criar_votacao.validacoes import duracao_em_segundos
from src.config.constantes import StatusVotacao
from src.modelos import votacao


def momento_limite(registro):
    """Instante em que o tempo da votação chega a zero (RN8)."""
    inicio = datetime.fromisoformat(registro["data_inicio"])
    return inicio + timedelta(seconds=duracao_em_segundos(registro["duracao"]))


def segundos_restantes(registro):
    """Segundos que faltam no cronômetro regressivo (0 se não estiver Ativa)."""
    if registro["status"] != StatusVotacao.ATIVA:
        return 0
    restante = (momento_limite(registro) - datetime.now()).total_seconds()
    return max(0, int(restante))


def encerrar_manual(conexao, votacao_id):
    """RN8 — encerramento manual pelo administrador, antes do fim do tempo."""
    registro = votacao.buscar_por_id(conexao, votacao_id)
    if registro is None:
        raise ErroDeNegocio("Votação não encontrada")
    if registro["status"] != StatusVotacao.ATIVA:
        raise ErroDeNegocio("Somente votação Ativa pode ser encerrada")

    votacao.encerrar(
        conexao, votacao_id, datetime.now().isoformat(timespec="seconds"))
    conexao.commit()


def encerrar_se_tempo_esgotado(conexao, registro):
    """RN8 — encerramento automático: se a votação está Ativa e o tempo
    chegou a zero, encerra registrando o instante-limite como encerramento.
    Chamado por toda rota que toca uma votação, garantindo que o estado no
    banco nunca fique atrás do cronômetro. Retorna True se encerrou agora."""
    if (registro["status"] == StatusVotacao.ATIVA
            and datetime.now() >= momento_limite(registro)):
        votacao.encerrar(
            conexao, registro["id"],
            momento_limite(registro).isoformat(timespec="seconds"))
        conexao.commit()
        return True
    return False
