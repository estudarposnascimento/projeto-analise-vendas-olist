
-- =========================================================
-- CAMADA GOLD
-- Tabela analítica de vendas
-- Granularidade: um registro por item de pedido
-- =========================================================

DROP TABLE IF EXISTS gold_vendas;

CREATE TABLE gold_vendas AS

SELECT
    oi.order_id,
    oi.order_item_id,

    o.customer_id,

    DATE(o.order_purchase_timestamp) AS purchase_date,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    o.order_status,

    oi.product_id,
    p.product_category_name,

    oi.seller_id,
    oi.shipping_limit_date,

    CAST(oi.price AS REAL) AS price,
    CAST(oi.freight_value AS REAL) AS freight_value,

    ROUND(
        CAST(oi.price AS REAL) +
        CAST(oi.freight_value AS REAL),
        2
    ) AS total_item_value

FROM silver_order_items AS oi

INNER JOIN silver_orders AS o
    ON oi.order_id = o.order_id

INNER JOIN silver_products AS p
    ON oi.product_id = p.product_id;


-- Índices para otimizar consultas analíticas

CREATE INDEX IF NOT EXISTS idx_gold_vendas_order_id
    ON gold_vendas(order_id);

CREATE INDEX IF NOT EXISTS idx_gold_vendas_purchase_date
    ON gold_vendas(purchase_date);

CREATE INDEX IF NOT EXISTS idx_gold_vendas_category
    ON gold_vendas(product_category_name);

CREATE INDEX IF NOT EXISTS idx_gold_vendas_product_id
    ON gold_vendas(product_id);
