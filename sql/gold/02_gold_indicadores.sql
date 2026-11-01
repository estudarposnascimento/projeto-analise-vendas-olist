
-- =========================================================
-- CAMADA GOLD - INDICADORES DE NEGÓCIO
-- Regra: considerar somente pedidos entregues
-- =========================================================


-- 1. INDICADORES MENSAIS

DROP TABLE IF EXISTS gold_vendas_mensais;

CREATE TABLE gold_vendas_mensais AS

SELECT
    strftime('%Y-%m', purchase_date) AS ano_mes,

    COUNT(DISTINCT order_id) AS quantidade_pedidos,

    COUNT(*) AS quantidade_itens,

    ROUND(SUM(price), 2) AS valor_produtos,

    ROUND(SUM(freight_value), 2) AS valor_frete,

    ROUND(SUM(total_item_value), 2) AS valor_total_com_frete,

    ROUND(
        SUM(price) / COUNT(DISTINCT order_id),
        2
    ) AS ticket_medio

FROM gold_vendas

WHERE order_status = 'delivered'

GROUP BY strftime('%Y-%m', purchase_date)

ORDER BY ano_mes;


-- 2. INDICADORES POR CATEGORIA

DROP TABLE IF EXISTS gold_vendas_categorias;

CREATE TABLE gold_vendas_categorias AS

SELECT
    COALESCE(
        product_category_name,
        'nao_informado'
    ) AS categoria,

    COUNT(DISTINCT order_id) AS quantidade_pedidos,

    COUNT(*) AS quantidade_itens,

    ROUND(SUM(price), 2) AS valor_produtos,

    ROUND(SUM(freight_value), 2) AS valor_frete,

    ROUND(SUM(total_item_value), 2) AS valor_total_com_frete

FROM gold_vendas

WHERE order_status = 'delivered'

GROUP BY COALESCE(
    product_category_name,
    'nao_informado'
)

ORDER BY valor_produtos DESC;


-- 3. RANKING DE PRODUTOS

DROP TABLE IF EXISTS gold_top_produtos;

CREATE TABLE gold_top_produtos AS

SELECT
    product_id,

    product_category_name AS categoria,

    COUNT(DISTINCT order_id) AS quantidade_pedidos,

    COUNT(*) AS quantidade_itens,

    ROUND(SUM(price), 2) AS valor_produtos,

    ROUND(SUM(freight_value), 2) AS valor_frete

FROM gold_vendas

WHERE order_status = 'delivered'

GROUP BY
    product_id,
    product_category_name

ORDER BY quantidade_itens DESC;
