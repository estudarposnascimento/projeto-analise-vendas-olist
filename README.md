# Projeto de Análise de Vendas — Olist

## Sobre o projeto

Este projeto tem como objetivo desenvolver uma solução de Engenharia de Dados e Análise de Vendas utilizando o conjunto de dados Brazilian E-Commerce Public Dataset by Olist.

A proposta é construir um pipeline de dados organizado em arquitetura Medalhão (Bronze, Silver e Gold), utilizando Python, Pandas, SQLite e SQL para realizar extração, armazenamento, transformação, validação e análise de dados.

O projeto também busca aplicar boas práticas de desenvolvimento, organização de código, documentação e testes automatizados.

## Objetivos

- Desenvolver um pipeline de dados reproduzível.
- Implementar a arquitetura Medalhão (Bronze, Silver e Gold).
- Realizar extração e tratamento de dados com Python e Pandas.
- Utilizar SQLite como banco de dados local.
- Implementar validações de qualidade e integridade dos dados.
- Desenvolver indicadores de negócio utilizando SQL.
- Construir um dashboard interativo para análise dos resultados.
- Implementar testes automatizados e documentação técnica.

## Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Desenvolvimento do pipeline |
| UV | Gerenciamento do ambiente e dependências |
| Pandas | Manipulação e transformação de dados |
| SQLite | Armazenamento local |
| SQL | Consultas e indicadores |
| Streamlit | Dashboard interativo |
| Plotly | Visualização de dados |
| Pytest | Testes automatizados |
| Ruff | Padronização e qualidade do código |
| MkDocs Material | Documentação técnica |

## Fonte dos dados

**Brazilian E-Commerce Public Dataset by Olist**

Fonte: Kaggle

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Arquivos utilizados inicialmente:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`

Os arquivos originais e o banco de dados local não são disponibilizados neste repositório. Para executar o projeto, baixe os arquivos diretamente da fonte e coloque-os na pasta `data/raw/`.

## Arquitetura de dados

O projeto utiliza a arquitetura Medalhão:

### Bronze

Camada responsável pelo armazenamento inicial dos dados extraídos dos arquivos CSV, preservando os valores originais.

### Silver

Camada destinada à limpeza, padronização, conversão de tipos e validação dos dados.

### Gold

Camada analítica destinada à construção de tabelas de negócio e indicadores para apoiar a tomada de decisão.

O armazenamento das camadas é realizado localmente em SQLite.

## Estrutura do projeto

```text
projeto_analise_vendas/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── database/
│
├── docs/
│
├── sql/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── src/
│   └── projeto/
│       ├── config.py
│       ├── extract.py
│       ├── load.py
│       ├── validate.py
│       ├── check_database.py
│       └── check_silver.py
│
├── tests/
│
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

## Configuração do ambiente

### Requisitos

- Python 3.12
- UV
- Git

### 1. Clonar o repositório

```powershell
git clone https://github.com/SEU_USUARIO/projeto-analise-vendas-olist.git
cd projeto-analise-vendas-olist
```

### 2. Instalar as dependências

```powershell
uv sync
```

### 3. Disponibilizar os dados

Baixe os arquivos CSV do Kaggle e coloque-os na pasta:

```text
data/raw/
```

### 4. Executar a extração

```powershell
uv run python -m projeto.extract
```

## Status do desenvolvimento

- [x] Estrutura inicial do projeto
- [x] Configuração do ambiente Python com UV
- [x] Extração dos arquivos CSV
- [x] Diagnóstico inicial dos dados
- [x] Implementação da camada Bronze
- [x] Armazenamento local em SQLite
- [x] Validação inicial de integridade
- [ ] Finalização e validação da camada Silver
- [ ] Construção da camada Gold
- [ ] Desenvolvimento dos indicadores SQL
- [ ] Construção do dashboard interativo
- [ ] Implementação dos testes automatizados
- [ ] Documentação técnica com MkDocs

## Autor: Fabiano Ferreira do Nascimento

Projeto desenvolvido para estudos e aplicação prática de Engenharia de Dados, Python, SQL e Análise de Dados.