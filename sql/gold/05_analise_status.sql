
-- Distribuição dos pedidos por status

SELECT
    order_status,
    COUNT(DISTINCT order_id) AS quantidade_pedidos,
    ROUND(SUM(price), 2) AS valor_produtos,
    ROUND(SUM(freight_value), 2) AS valor_frete,
    ROUND(SUM(total_item_value), 2) AS valor_total

FROM gold_vendas

GROUP BY order_status

ORDER BY quantidade_pedidos DESC;
