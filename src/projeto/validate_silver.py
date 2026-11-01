
import sqlite3

from projeto.config import DATABASE_PATH


VALIDATIONS = {
    "Orders - order_id nulo": """
        SELECT COUNT(*)
        FROM silver_orders
        WHERE order_id IS NULL OR TRIM(order_id) = ''
    """,
    "Orders - order_id duplicado": """
        SELECT COUNT(*)
        FROM (
            SELECT order_id
            FROM silver_orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        )
    """,
    "Orders - data de compra nula": """
        SELECT COUNT(*)
        FROM silver_orders
        WHERE order_purchase_timestamp IS NULL
    """,
    "Orders - data estimada nula": """
        SELECT COUNT(*)
        FROM silver_orders
        WHERE order_estimated_delivery_date IS NULL
    """,
    "Items - chave composta duplicada": """
        SELECT COUNT(*)
        FROM (
            SELECT order_id, order_item_id
            FROM silver_order_items
            GROUP BY order_id, order_item_id
            HAVING COUNT(*) > 1
        )
    """,
    "Items - preço negativo": """
        SELECT COUNT(*)
        FROM silver_order_items
        WHERE price < 0
    """,
    "Items - frete negativo": """
        SELECT COUNT(*)
        FROM silver_order_items
        WHERE freight_value < 0
    """,
    "Items - pedido inexistente": """
        SELECT COUNT(*)
        FROM silver_order_items i
        LEFT JOIN silver_orders o
            ON i.order_id = o.order_id
        WHERE o.order_id IS NULL
    """,
    "Items - produto inexistente": """
        SELECT COUNT(*)
        FROM silver_order_items i
        LEFT JOIN silver_products p
            ON i.product_id = p.product_id
        WHERE p.product_id IS NULL
    """,
    "Products - product_id nulo": """
        SELECT COUNT(*)
        FROM silver_products
        WHERE product_id IS NULL OR TRIM(product_id) = ''
    """,
    "Products - product_id duplicado": """
        SELECT COUNT(*)
        FROM (
            SELECT product_id
            FROM silver_products
            GROUP BY product_id
            HAVING COUNT(*) > 1
        )
    """,
    "Products - peso negativo": """
        SELECT COUNT(*)
        FROM silver_products
        WHERE product_weight_g < 0
    """,
    "Products - dimensões negativas": """
        SELECT COUNT(*)
        FROM silver_products
        WHERE product_length_cm < 0
           OR product_height_cm < 0
           OR product_width_cm < 0
    """,
}


def main():
    with sqlite3.connect(DATABASE_PATH) as connection:
        print("=" * 55)
        print("VALIDAÇÃO DE QUALIDADE - CAMADA SILVER")
        print("=" * 55)

        failures = 0

        for description, query in VALIDATIONS.items():
            result = connection.execute(query).fetchone()[0]

            status = "OK" if result == 0 else "VERIFICAR"

            if result != 0:
                failures += 1

            print(f"{description}: {result} - {status}")

        print("=" * 55)
        print(f"Verificações: {len(VALIDATIONS)}")
        print(f"Ocorrências para verificar: {failures}")


if __name__ == "__main__":
    main()
