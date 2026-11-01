
# Projeto de Análise de Vendas — Olist

## Visão geral

Este projeto tem como objetivo desenvolver uma solução de análise de dados
utilizando o conjunto de dados público Brazilian E-Commerce Public Dataset
by Olist.

A solução utiliza Python, Pandas, SQL e SQLite para realizar a extração,
validação, transformação e análise dos dados de vendas.

## Objetivos

- Construir um pipeline de dados utilizando a arquitetura Medalhão.
- Organizar os dados nas camadas Bronze, Silver e Gold.
- Aplicar regras de qualidade e validação dos dados.
- Desenvolver indicadores comerciais utilizando SQL.
- Preparar uma base analítica para visualização em dashboard.

## Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Desenvolvimento do pipeline |
| Pandas | Manipulação dos dados |
| SQLite | Armazenamento dos dados |
| SQL | Transformação e indicadores |
| Streamlit | Dashboard planejado |
| Plotly | Visualizações planejadas |
| Pytest | Testes automatizados |
| Ruff | Qualidade e padronização do código |
| MkDocs Material | Documentação técnica |

## Resultados atuais

A camada Gold apresenta os seguintes resultados:

| Indicador | Resultado |
|---|---:|
| Pedidos entregues | 96.478 |
| Itens entregues | 110.197 |
| Valor dos produtos vendidos | R$ 13.221.498,11 |
| Valor do frete | R$ 2.198.275,64 |
| Ticket médio | R$ 137,04 |

Os indicadores foram reconciliados entre as tabelas de vendas mensais,
categorias e produtos, sem diferenças nos valores totais.

## Arquitetura

O projeto utiliza a arquitetura Medalhão:

- **Bronze:** dados originais carregados no banco SQLite.
- **Silver:** dados tratados, padronizados e validados.
- **Gold:** dados consolidados para análises e indicadores.

## Status do projeto

- [x] Extração dos dados
- [x] Camada Bronze
- [x] Transformações Silver
- [x] Validações de qualidade
- [x] Camada Gold
- [x] Indicadores comerciais
- [ ] Testes automatizados
- [ ] Dashboard interativo
- [ ] Documentação completa
- [ ] Publicação final no GitHub
