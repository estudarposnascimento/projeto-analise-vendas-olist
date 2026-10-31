
import sqlite3

from projeto.config import DATABASE_PATH


def count_query(
    connection: sqlite3.Connection,
    query: str,
) -> int:
    return connection.execute(query).fetchone()[0]


def validate_bronze() -> None:
    """
    Verifica chaves primárias e integridade referencial
    das tabelas Bronze.
    """

    with sqlite3.connect(DATABASE_PATH) as connection:

        checks = {
            "Orders com order_id nulo": """
                SELECT COUNT(*)
                FROM bronze_orders
                WHERE order_id IS NULL
            """,

            "Orders com order_id duplicado": """
                SELECT COUNT(*)
                FROM (
                    SELECT order_id
                    FROM bronze_orders
                    GROUP BY order_id
                    HAVING COUNT(*) > 1
                )
            """,

            "Products com product_id nulo": """
                SELECT COUNT(*)
                FROM bronze_products
                WHERE product_id IS NULL
            """,

            "Products com product_id duplicado": """
                SELECT COUNT(*)
                FROM (
                    SELECT product_id
                    FROM bronze_products
                    GROUP BY product_id
                    HAVING COUNT(*) > 1
                )
            """,

            "Order Items com chave composta duplicada": """
                SELECT COUNT(*)
                FROM (
                    SELECT order_id, order_item_id
                    FROM bronze_order_items
                    GROUP BY order_id, order_item_id
                    HAVING COUNT(*) > 1
                )
            """,

            "Order Items sem pedido correspondente": """
                SELECT COUNT(*)
                FROM bronze_order_items AS i
                LEFT JOIN bronze_orders AS o
                    ON i.order_id = o.order_id
                WHERE o.order_id IS NULL
            """,

            "Order Items sem produto correspondente": """
                SELECT COUNT(*)
                FROM bronze_order_items AS i
                LEFT JOIN bronze_products AS p
                    ON i.product_id = p.product_id
                WHERE p.product_id IS NULL
            """,
        }

        print("\n" + "=" * 60)
        print("VALIDAÇÃO DE QUALIDADE - CAMADA BRONZE")
        print("=" * 60)

        for description, query in checks.items():

            result = count_query(connection, query)

            status = "OK" if result == 0 else "VERIFICAR"

            print(f"{status} | {description}: {result:,}")

        print("\nValidação concluída.")


if __name__ == "__main__":
    validate_bronze()
