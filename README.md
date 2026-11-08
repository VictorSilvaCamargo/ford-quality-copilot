# Quality Copilot

Copiloto de Inteligência Artificial (RAG + Analytics) para detecção precoce de falhas recorrentes em campo e estimativa de custo evitável em veículos automotivos, construído sobre dados públicos oficiais da **NHTSA**.

> [!IMPORTANT]
> **Aviso sobre Dados e Premissas de Custo**
> Todos os registros utilizados neste projeto são **dados públicos oficiais da NHTSA** (*National Highway Traffic Safety Administration* — reclamações de consumidores, recalls, investigações de segurança e boletins de serviço técnico/TSBs).
> As **premissas de custo** adotadas na modelagem financeira são **hipóteses analíticas declaradas e auditáveis** para fins de estudo de engenharia e portfólio, **não** representando dados internos, confidenciais ou reais de nenhuma montadora.

---

## 1. Problema

Falhas emergentes de qualidade e confiabilidade automotiva costumam surgir de maneira pulverizada em milhares de relatos textuais não estruturados (reclamações de proprietários e boletins técnicos) meses antes de se consolidarem em campanhas de recall ou picos severos de custo de garantia. A triagem puramente manual dificulta:

- agrupar descrições distintas que descrevem o mesmo modo de falha físico;
- detectar precocemente desvios de volume por fabricante, modelo, ano-modelo e subsistema;
- priorizar investigações de engenharia com base no risco de segurança e no impacto financeiro evitável.

## 2. Hipótese

Se integrarmos os dados públicos da NHTSA em um banco relacional e vetorial (**PostgreSQL + pgvector**), aplicarmos *embeddings* e clusterização semântica sobre as narrativas de falha, monitorarmos anomalias temporais e acoplarmos um **agente RAG** a um modelo explícito de custo evitável, será possível identificar padrões críticos com antecedência, recuperar evidências rastreáveis e apoiar decisões de priorização de qualidade com justificativa quantitativa.

## 3. Arquitetura Planejada

Fluxo ponta a ponta planejado para o sistema (`ingestão → banco → embeddings/clusters → alertas → agente → API/UI`):

```text
[Dados Públicos NHTSA: Reclamações, Recalls, Investigações e TSBs]
        │
        ▼
1. Ingestão (src/ingest)
   Download reprodutível, higienização, padronização de esquemas e carga incremental
        │
        ▼
2. Banco de Dados (PostgreSQL 17 + pgvector)
   Armazenamento relacional estruturado + índice vetorial para busca semântica
        │
        ▼
3. Embeddings & Clusters (src/features)
   Vetorização das narrativas técnicas e agrupamento de modos de falha recorrentes
        │
        ▼
4. Alertas (src/alerts)
   Detecção de tendências, surtos de reclamações e correlação com recalls/investigações
        │
        ▼
5. Custo Evitável & Agente RAG (src/cost + src/agent)
   Simulação financeira sob premissas declaradas + copiloto LangChain com citações verificáveis
        │
        ▼
6. API & Interface (src/api + app/)
   Serviços REST em FastAPI e aplicação analítica interativa em Streamlit
```

## 4. Stack Tecnológica

| Camada | Tecnologias |
| :--- | :--- |
| **Linguagem & Ambiente** | Python 3.11+, `uv` |
| **Banco & Vetores** | PostgreSQL 17 + `pgvector` (`pgvector/pgvector:0.8.7-pg17`), Docker Compose |
| **Dados & Persistência** | `pandas`, `pyarrow`, `SQLAlchemy`, `psycopg` (v3), `python-dotenv`, `requests` |
| **IA & Orquestração *(previsto)*** | `LangChain`, modelos de embeddings e LLMs |
| **Serviços & UI *(previsto)*** | `FastAPI`, `Streamlit` |
| **Qualidade & CI/CD** | `ruff` (lint + format), `pytest`, `pre-commit`, GitHub Actions |

## 5. Estrutura de Pastas

```text
quality-copilot/
├── app/                        # Interface analítica (Streamlit - próximas etapas)
├── data/
│   ├── raw/                    # Dados brutos baixados da NHTSA (ignorados no Git)
│   └── processed/              # Dados tratados/particionados (ignorados no Git)
├── docker/
│   └── init/01_pgvector.sql    # Script SQL de inicialização da extensão vector
├── notebooks/                  # Explorações e prototipação controlada
├── reports/                    # Relatórios técnicos e artefatos gerados
├── src/
│   ├── ingest/                 # Pipelines de coleta e carga dos dados NHTSA
│   ├── features/               # Geração de embeddings e clusterização
│   ├── alerts/                 # Regras e estatísticas de detecção de anomalias
│   ├── cost/                   # Modelo paramétrico de estimativa de custo evitável
│   ├── agent/                  # Agente RAG e ferramentas de consulta
│   └── api/                    # Endpoints FastAPI
├── tests/                      # Testes automatizados (fumaça, unidade e integração)
├── .env.example                # Exemplo de variáveis de ambiente (sem segredos)
├── .pre-commit-config.yaml     # Hooks de validação local pré-commit
├── docker-compose.yml          # Serviço local PostgreSQL + pgvector com healthcheck
├── Makefile                    # Atalhos de automação para desenvolvimento
└── pyproject.toml              # Configuração do projeto, dependências e Ruff
```

## 6. Como Rodar Localmente

### Pré-requisitos

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** instalado no `PATH`
- **Docker Desktop** em execução (no Windows, requer **WSL 2** e *Virtual Machine Platform* habilitados)

### Passo a passo com `make` (Linux / macOS / Git Bash com Make)

```bash
# 1. Instala dependências, configura hooks do pre-commit e cria o .env local
make setup

# 2. Sobe o container PostgreSQL + pgvector em background aguardando healthcheck
make up

# 3. Executa verificação estática e formatação com Ruff
make lint

# 4. Executa os testes automatizados (inclui teste de fumaça do banco + extensão vector)
make test

# 5. Encerra os containers locais
make down
```

### Comandos diretos equivalentes no Windows (PowerShell, sem `make`)

Caso o utilitário `make` não esteja instalado no Windows, execute diretamente os comandos equivalentes:

| Alvo (`Makefile`) | Comando direto no PowerShell |
| :--- | :--- |
| `make setup` | `uv sync; uv run pre-commit install; if (!(Test-Path .env)) { Copy-Item .env.example .env }` |
| `make up` | `docker compose up -d --wait` |
| `make down` | `docker compose down` |
| `make lint` | `uv run ruff check .; uv run ruff format --check .` |
| `make test` | `uv run pytest -v` |

> **Nota sobre porta de rede:** por padrão o PostgreSQL é exposto em `localhost:5432`. Se a porta `5432` já estiver em uso na máquina local, altere `POSTGRES_PORT=5433` no arquivo `.env` antes de subir os containers.

## 7. Roadmap — Etapas do Projeto

- [ ] 🔄 **Etapa 1 — Fundação *(Em andamento)***: Repositório, estrutura modular, ambiente Python com `uv`, `ruff` + `pre-commit`, PostgreSQL + `pgvector` via Docker Compose, teste de fumaça e integração contínua (GitHub Actions).
- [ ] **Etapa 2 — Ingestão de Dados NHTSA**: Coleta automatizada, validação de esquemas e persistência de reclamações, recalls, investigações e TSBs filtrados por fabricante e modelo.
- [ ] **Etapa 3 — Análise Exploratória e Qualidade de Dados**: Perfilamento das bases por linha de veículo, ano-modelo, componente e indicadores críticos de segurança.
- [ ] **Etapa 4 — Embeddings e Clusterização de Falhas**: Vetorização semântica dos relatos no `pgvector` e identificação de grupos de falhas recorrentes.
- [ ] **Etapa 5 — Detecção de Tendências e Alertas**: Monitoramento temporal de anomalias e priorização de sinais precoces.
- [ ] **Etapa 6 — Estimativa Paramétrica de Custo Evitável**: Modelagem financeira transparente baseada em premissas declaradas e cenários de sensibilidade.
- [ ] **Etapa 7 — Agente RAG (Quality Copilot)**: Assistente em LangChain capaz de responder perguntas técnicas combinando busca semântica, agregações SQL e citações das fontes originais.
- [ ] **Etapa 8 — API e Painel Interativo**: Disponibilização via FastAPI e construção de interface executiva e investigativa em Streamlit.
- [ ] **Etapa 9 — Avaliação, Hardening e Consolidação de Portfólio**: Métricas de avaliação do RAG, revisão de testes ponta a ponta e documentação executiva final.

## Licença

Distribuído sob a licença **MIT**. Consulte o arquivo `LICENSE` para mais detalhes.
