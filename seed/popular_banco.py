"""Seed do PAC — popula o banco com os dados de teste que substituem UC2/UC3.

Cenários criados (rastreáveis aos critérios de aceite):
  • 1 administradora (Carla Síndica).
  • Maria Gomes com 2 lotes (Apt 202 + Apt 203) = peso 2,40  → demonstra RN1.
  • Pedro Semlote, proprietário ATIVO sem lote               → fora dos aptos (RN2).
  • Otávio Inativo, proprietário INATIVO com lote            → fora dos aptos (RN2).
  • Demais proprietários com 1 lote cada (João 1,25; Ana 1,50; Bruno 1,15).
  • Reunião "Assembleia Ordinária 2026" com 2 itens de pauta e anexos.

Peso total apto esperado ao Iniciar: 1,25 + 2,40 + 1,50 + 1,15 = 6,30.
Cenário de EMPATE demonstrável (RN6): Maria (2,40) numa opção contra
João + Bruno (1,25 + 1,15 = 2,40) em outra, com Ana se abstendo ou ausente.

Uso:  python3 seed/popular_banco.py   (a partir da raiz do projeto)
"""

import sys
from pathlib import Path

# permite executar o script diretamente da raiz do projeto
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from werkzeug.security import generate_password_hash

from src.config import banco, constantes
from src.modelos import usuario, lote, reuniao, item_pauta, anexo

SENHA_PADRAO = "Condominio@2026"  # atende RNF4: >= 8 caracteres, não é senha comum


def popular():
    # RNF4 — o seed passa pela mesma política de senha da aplicação
    erro_senha = constantes.validar_senha(SENHA_PADRAO)
    if erro_senha:
        raise SystemExit(f"Senha do seed viola a RNF4: {erro_senha}")

    if banco.CAMINHO_BANCO.exists():
        banco.CAMINHO_BANCO.unlink()
        print(f"Banco anterior removido: {banco.CAMINHO_BANCO.name}")

    conexao = banco.obter_conexao()
    banco.criar_esquema(conexao)
    hash_senha = generate_password_hash(SENHA_PADRAO)

    # ── Usuários ────────────────────────────────────────────────────────────
    admin_id = usuario.inserir(
        conexao, "Carla Síndica", "carla@condominio.com", hash_senha,
        "86 99999-0001", constantes.TipoUsuario.ADMINISTRADOR)

    joao_id = usuario.inserir(
        conexao, "João Limão", "joao@condominio.com", hash_senha,
        "86 99999-0002", constantes.TipoUsuario.PROPRIETARIO)
    maria_id = usuario.inserir(
        conexao, "Maria Gomes", "maria@condominio.com", hash_senha,
        "86 99999-0003", constantes.TipoUsuario.PROPRIETARIO)
    ana_id = usuario.inserir(
        conexao, "Ana Pereira", "ana@condominio.com", hash_senha,
        "86 99999-0004", constantes.TipoUsuario.PROPRIETARIO)
    bruno_id = usuario.inserir(
        conexao, "Bruno Costa", "bruno@condominio.com", hash_senha,
        "86 99999-0005", constantes.TipoUsuario.PROPRIETARIO)

    # RN2 — proprietário ATIVO mas SEM lote: não entra na lista de aptos
    usuario.inserir(
        conexao, "Pedro Semlote", "pedro@condominio.com", hash_senha,
        "86 99999-0006", constantes.TipoUsuario.PROPRIETARIO)

    # RN2 — proprietário INATIVO (mesmo com lote): não entra na lista de aptos
    otavio_id = usuario.inserir(
        conexao, "Otávio Inativo", "otavio@condominio.com", hash_senha,
        "86 99999-0007", constantes.TipoUsuario.PROPRIETARIO, ativo=False)

    # ── Lotes (RN1 — fonte oficial do peso de voto) ─────────────────────────
    lote.inserir(conexao, "Apt 101", 0.625, 1.25, joao_id)
    lote.inserir(conexao, "Apt 202", 0.60, 1.20, maria_id)   # Maria: 2 lotes
    lote.inserir(conexao, "Apt 203", 0.60, 1.20, maria_id)   # 1,20 + 1,20 = 2,40
    lote.inserir(conexao, "Casa 05", 0.75, 1.50, ana_id)
    lote.inserir(conexao, "Apt 304", 0.575, 1.15, bruno_id)
    lote.inserir(conexao, "Apt 401", 0.475, 0.95, otavio_id)  # dono inativo

    # ── Reunião e pauta (substitui UC3) ─────────────────────────────────────
    reuniao_id = reuniao.inserir(
        conexao, "Assembleia Ordinária 2026", "2026-07-12", "19:00",
        "Salão de festas", constantes.StatusReuniao.AGENDADA)
    item1_id = item_pauta.inserir(
        conexao, "Aprovação de orçamento", "Orçamento anual de custeio", reuniao_id)
    item2_id = item_pauta.inserir(
        conexao, "Prestação de contas Q1", "Demonstrativo do 1º trimestre", reuniao_id)
    anexo.inserir(conexao, "orcamento_2026.pdf", item1_id)
    anexo.inserir(conexao, "contas_q1.pdf", item2_id)

    conexao.commit()

    # ── Resumo ──────────────────────────────────────────────────────────────
    aptos = usuario.listar_aptos_com_peso(conexao)
    print(f"\nBanco criado em {banco.CAMINHO_BANCO}")
    print(f"Reunião: Assembleia Ordinária 2026 (id {reuniao_id}) com 2 itens de pauta")
    print(f"\nSenha de TODOS os usuários: {SENHA_PADRAO}")
    print(f"  Administradora: carla@condominio.com (id {admin_id})")
    print("  Proprietários:")
    for linha in aptos:
        print(f"    APTO   {linha['nome']:<15} peso {linha['peso_total']:.2f}")
    print("    NÃO APTO Pedro Semlote   (ativo, sem lote — RN2)")
    print("    NÃO APTO Otávio Inativo  (inativo, com lote — RN2)")
    peso_total = sum(linha["peso_total"] for linha in aptos)
    print(f"\nPeso total apto esperado no Iniciar: {peso_total:.2f}")
    conexao.close()


if __name__ == "__main__":
    popular()
