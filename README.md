# PAC — Plataforma de Assembleias Condominiais

Implementação acadêmica do PAC (ERSw versão 1.1, Equipe APEX) com **4 funcionalidades**:

| # | Funcionalidade | Caso de uso | Requisitos |
|---|---|---|---|
| 1 | Entrar no sistema | UC1 | RF9, RNF4 |
| 2 | Criar votação | UC4 | RF5 |
| 3 | Executar votação | UC5 | RF6 |
| 4 | Verificar o resultado | UC6 | RF7 |

Gestão de usuários/lotes (UC2) e de reuniões/pautas (UC3) estão **fora do escopo** e são
supridas pelo script de seed. A arquitetura, os diagramas e as decisões de projeto estão
em [docs/ARQUITETURA.md](docs/ARQUITETURA.md).

## Pré-requisitos

- **Python 3.10+** (testado com 3.14)
- Nenhum banco para instalar: o SQLite faz parte da biblioteca padrão do Python.

## Instalação

```bash
cd trabalho-engenharia-1-
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Como rodar o seed (dados de teste)

```bash
.venv/bin/python seed/popular_banco.py
```

O seed **recria o banco do zero** (`pac.db`) com 1 administradora, 6 proprietários,
6 lotes e a reunião "Assembleia Ordinária 2026" com 2 itens de pauta.

## Como subir o servidor

```bash
.venv/bin/python src/servidor.py
```

Acesse **http://127.0.0.1:5001** (interface mobile-first — funciona bem também com a
janela estreita ou no celular, a partir de 360 px).

## Credenciais de teste

Senha de **todos** os usuários: `Condominio@2026`

| E-mail | Perfil | Lotes | Peso de voto |
|---|---|---|---|
| carla@condominio.com | **Administradora** | — | — |
| joao@condominio.com | Proprietário | Apt 101 | 1,25 |
| maria@condominio.com | Proprietário | Apt 202 + Apt 203 | **2,40** (RN1 — soma dos lotes) |
| ana@condominio.com | Proprietário | Casa 05 | 1,50 |
| bruno@condominio.com | Proprietário | Apt 304 | 1,15 |
| pedro@condominio.com | Proprietário | **nenhum lote** | não apto (RN2) |
| otavio@condominio.com | Proprietário **inativo** | Apt 401 | não apto (RN2) — login bloqueado |

Peso total apto ao Iniciar: **6,30**.

## Roteiro de demonstração

Use **duas janelas** (ou uma janela normal + uma anônima): uma para a administradora,
outra para os proprietários.

### 1. Fluxo feliz (criar → iniciar → votar → encerrar → resultado)

1. **Login admin** — entre com `carla@condominio.com`. O painel mostra a reunião e a pauta.
2. **Criar votação** — clique em **Nova Votação**; preencha a pergunta ("Aprova o
   orçamento anual?"), tipo **Sim/Não/Abstenção**, visibilidade **Aberta**, tempo
   `05:00`, quórum `30`; clique **Salvar Votação**. Observe que ela fica **Configurada**
   — salvar não libera (RN3), e o botão **Iniciar** fica na listagem, fora do formulário.
3. **Iniciar** — clique **Iniciar** na listagem. O PAC congela os aptos (4 proprietários;
   Pedro e Otávio ficam de fora — RN2) e abre a tela de **Condução** com peso apto 6,30,
   cronômetro e indicadores ao vivo.
4. **Login proprietário (outra aba)** — entre com `maria@condominio.com`, clique
   **Votar**. A tela mostra **"Peso do seu voto: 2,40 (soma dos lotes Apt 202; Apt 203)"**
   (RN1). Escolha **Sim** e confirme → "Voto confirmado com peso 2,40".
5. **Voto único (RN4)** — tente votar de novo: "Seu voto já foi registrado".
6. **Não apto (RN2)** — em outra aba anônima, entre com `pedro@condominio.com` e abra a
   votação: "Você não está apto a votar nesta votação".
7. **Mais votos** — vote com `joao@condominio.com` (Não) e `bruno@condominio.com`
   (Abstenção). Veja os indicadores da Condução atualizando sozinhos.
8. **Encerrar** — na Condução (admin), clique **Encerrar**. Quem tentar votar depois
   recebe "Votação encerrada" (RN8) — vale também se o tempo zerar sozinho.
9. **Resultado (Aberta)** — clique **Ver Resultado**: quórum atingido,
   **CONCLUIDO — Aprovado (Sim)** — a abstenção do Bruno contou para o quórum, mas não
   concorreu (RN6) — e a **relação nominal** com proprietário, lotes, voto e peso.

### 2. Votação FECHADA (sigilo — RN5/RNF5)

1. Como admin, crie outra votação (ex.: Múltipla Escolha com "Construtora Alfa/Beta/Gama"),
   visibilidade **Fechada**, e inicie.
2. Vote com 2–3 proprietários e encerre.
3. No resultado: apuração consolidada por peso e **"Participantes da votação (sem escolha
   individual)"** — lotes, peso e horário, nunca a opção. No banco, os votos têm
   `usuario_id = NULL` (a associação não existe fisicamente):
   ```bash
   sqlite3 pac.db "SELECT usuario_id, peso_computado FROM voto WHERE votacao_id = <id>;"
   ```

### 3. EMPATE (RN6)

1. Crie uma votação Sim/Não/Abstenção **sem quórum mínimo** e inicie.
2. `maria` vota **Sim** (2,40); `joao` (1,25) e `bruno` (1,15) votam **Não** (2,40).
3. Encerre: **EMPATE**, vencedora vazia, "Empate entre: Sim · Não".

### 4. SEM QUÓRUM (RN6)

1. Crie uma votação com quórum mínimo `50` e inicie.
2. Somente `maria` vota (2,40 de 6,30 = 38,1%).
3. Encerre: **SEM_QUORUM — Não atingido**, sem vencedora.

### 5. Encerramento automático (RN8)

1. Crie uma votação com tempo `00:30` e inicie.
2. Deixe o cronômetro zerar: a votação encerra sozinha; a tela do proprietário passa a
   exibir "Votação encerrada" e qualquer voto tardio é rejeitado.

## Estrutura do projeto

```
docs/ARQUITETURA.md      # arquitetura, diagramas Mermaid, rastreabilidade, segurança
seed/popular_banco.py    # dados de teste (substitui UC2/UC3)
src/config/              # banco (esquema + constraints RN4/RN5), sessão, constantes
src/modelos/             # 1 arquivo por entidade persistente da ERSw
src/casos_de_uso/        # ★ regras de negócio: uc1_autenticacao, uc4_criar_votacao,
                         #   uc5_executar_votacao, uc6_resultado
src/rotas/               # mapeamento URL → caso de uso (zero regra de negócio)
src/telas/               # 1 template Jinja2 por protótipo da ERSw
src/publico/estilos.css  # CSS mobile-first (RNF1, a partir de 360 px)
src/servidor.py          # ponto de entrada Flask
```

A divisão do conteúdo para os **3 apresentadores** está na seção 10 do
[ARQUITETURA.md](docs/ARQUITETURA.md).
