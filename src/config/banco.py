"""Conexão SQLite e criação do esquema do PAC.

O esquema é fiel ao Diagrama de Classes Persistentes da ERSw (seção 3.5).
Duas garantias estruturais vivem AQUI, no banco, e não apenas na aplicação:

  • RN4 — Voto único: UNIQUE (votacao_id, usuario_id) em participacao_votacao
    e em voto (para votação aberta, na qual o voto identifica o autor).
  • RN5 — Sigilo: voto.usuario_id é opcional (NULL) e um TRIGGER impede
    que um voto de votação FECHADA seja gravado com usuário preenchido —
    a associação participante→escolha não existe fisicamente.
"""

import sqlite3
from pathlib import Path

# O banco fica na raiz do projeto (arquivo único, gratuito — RNF2)
CAMINHO_BANCO = Path(__file__).resolve().parents[2] / "pac.db"


def obter_conexao():
    """Abre uma conexão com FOREIGN KEYs habilitadas e linhas acessíveis por nome."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuario (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    senha_hash  TEXT    NOT NULL,
    telefone    TEXT,
    tipo        TEXT    NOT NULL CHECK (tipo IN ('ADMINISTRADOR', 'PROPRIETARIO')),
    ativo       INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

-- RN1 — o Lote é a fonte oficial do peso de voto; pertence a exatamente 1 proprietário
CREATE TABLE IF NOT EXISTS lote (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    identificacao TEXT    NOT NULL UNIQUE,
    fracao_ideal  REAL    NOT NULL,
    peso          REAL    NOT NULL CHECK (peso >= 0),
    usuario_id    INTEGER NOT NULL REFERENCES usuario (id)
);

CREATE TABLE IF NOT EXISTS reuniao (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo  TEXT NOT NULL,
    data    TEXT NOT NULL,
    horario TEXT NOT NULL,
    local   TEXT,
    status  TEXT NOT NULL DEFAULT 'AGENDADA'
            CHECK (status IN ('RASCUNHO', 'AGENDADA', 'EM_ANDAMENTO', 'ENCERRADA'))
);

CREATE TABLE IF NOT EXISTS item_pauta (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo     TEXT    NOT NULL,
    descricao  TEXT,
    reuniao_id INTEGER NOT NULL REFERENCES reuniao (id)
);

CREATE TABLE IF NOT EXISTS anexo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_arquivo  TEXT    NOT NULL,
    item_pauta_id INTEGER NOT NULL REFERENCES item_pauta (id)
);

-- RN3 — status CONFIGURADA | ATIVA | ENCERRADA; RN8 — duração obrigatória (mm:ss)
CREATE TABLE IF NOT EXISTS votacao (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    pergunta          TEXT    NOT NULL,
    tipo_resposta     TEXT    NOT NULL CHECK (tipo_resposta IN
                        ('SIM_NAO_ABSTENCAO', 'MULTIPLA_ESCOLHA', 'ELEICAO_NOMES')),
    visibilidade      TEXT    NOT NULL CHECK (visibilidade IN ('ABERTA', 'FECHADA')),
    duracao           TEXT    NOT NULL,
    quorum_minimo     REAL    NOT NULL DEFAULT 0 CHECK (quorum_minimo BETWEEN 0 AND 100),
    status            TEXT    NOT NULL DEFAULT 'CONFIGURADA'
                      CHECK (status IN ('CONFIGURADA', 'ATIVA', 'ENCERRADA')),
    data_inicio       TEXT,
    data_encerramento TEXT,
    reuniao_id        INTEGER NOT NULL REFERENCES reuniao (id),
    item_pauta_id     INTEGER REFERENCES item_pauta (id)
);

CREATE TABLE IF NOT EXISTS opcao_voto (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    texto      TEXT    NOT NULL,
    votacao_id INTEGER NOT NULL REFERENCES votacao (id) ON DELETE CASCADE
);

-- Voto sempre aponta para 1 votação e 1 opção; usuario_id é OPCIONAL:
-- preenchido somente em votação ABERTA (RN5).
CREATE TABLE IF NOT EXISTS voto (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora      TEXT    NOT NULL,
    peso_computado REAL    NOT NULL,
    votacao_id     INTEGER NOT NULL REFERENCES votacao (id),
    opcao_voto_id  INTEGER NOT NULL REFERENCES opcao_voto (id),
    usuario_id     INTEGER REFERENCES usuario (id),
    -- RN4 no banco (votação aberta): um voto identificado por usuário por votação.
    -- SQLite ignora NULLs em UNIQUE, então votos sigilosos não colidem entre si.
    UNIQUE (votacao_id, usuario_id)
);

-- RN2 — aptos e pesos congelados no Iniciar. NUNCA referencia OpcaoVoto (RN5).
CREATE TABLE IF NOT EXISTS participacao_votacao (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    peso_fixado             REAL    NOT NULL,
    data_hora_participacao  TEXT,               -- NULL até o proprietário votar
    votacao_id              INTEGER NOT NULL REFERENCES votacao (id),
    usuario_id              INTEGER NOT NULL REFERENCES usuario (id),
    -- RN4 no banco (vale também para votação FECHADA, na qual o voto é anônimo):
    -- há exatamente 1 registro de participação por proprietário por votação.
    UNIQUE (votacao_id, usuario_id)
);

CREATE TABLE IF NOT EXISTS resultado_votacao (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    status                   TEXT    NOT NULL
                             CHECK (status IN ('CONCLUIDO', 'EMPATE', 'SEM_QUORUM')),
    peso_total_apto          REAL    NOT NULL,
    peso_participante        REAL    NOT NULL,
    percentual_participacao  REAL    NOT NULL,
    data_apuracao            TEXT    NOT NULL,
    votacao_id               INTEGER NOT NULL UNIQUE REFERENCES votacao (id),
    opcao_vencedora_id       INTEGER REFERENCES opcao_voto (id)  -- NULL em EMPATE/SEM_QUORUM
);

-- RN5/RNF5 — Sigilo no nível do banco: rejeita fisicamente qualquer voto de
-- votação FECHADA que tente referenciar um usuário.
CREATE TRIGGER IF NOT EXISTS trg_sigilo_votacao_fechada
BEFORE INSERT ON voto
FOR EACH ROW
WHEN NEW.usuario_id IS NOT NULL
     AND (SELECT visibilidade FROM votacao WHERE id = NEW.votacao_id) = 'FECHADA'
BEGIN
    SELECT RAISE(ABORT, 'RN5: voto de votacao FECHADA nao pode referenciar usuario');
END;
"""


def criar_esquema(conexao):
    """Cria todas as tabelas e o trigger de sigilo (idempotente)."""
    conexao.executescript(ESQUEMA)
    conexao.commit()
