
import sqlite3

from projeto.config import DATABASE_PATH


def main():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        print("=" * 75)
        print("ANÁLISE DE STATUS DOS PEDIDOS")
        print("=" * 75)

        # 1. Todos os pedidos da Silver, inclusive sem itens
        query_orders = """
            SELECT
                order_status,
                COUNT(*) AS quantidade
            FROM silver_orders
            GROUP BY order_status
            ORDER BY quantidade DESC
        """

        print("\n1. DISTRIBUIÇÃO DE TODOS OS PEDIDOS")

        for status, quantidade in cursor.execute(query_orders):
            print(f"{status}: {quantidade:,}")

        # 2. Pedidos que possuem itens na Gold
        query_gold = """
            SELECT
                order_status,
                COUNT(DISTINCT order_id) AS pedidos,
                ROUND(SUM(price), 2) AS produtos,
                ROUND(SUM(freight_value), 2) AS frete,
                ROUND(SUM(total_item_value), 2) AS total
            FROM gold_vendas
            GROUP BY order_status
            ORDER BY pedidos DESC
        """

        print("\n2. PEDIDOS PRESENTES NA GOLD")

        for linha in cursor.execute(query_gold):
            status, pedidos, produtos, frete, total = linha

            print(
                f"{status} | Pedidos: {pedidos:,} | "
                f"Produtos: R$ {produtos:,.2f} | "
                f"Frete: R$ {frete:,.2f} | "
                f"Total: R$ {total:,.2f}"
            )

        # 3. Pedidos sem itens associados
        query_missing = """
            SELECT
                o.order_status,
                COUNT(*) AS quantidade
            FROM silver_orders o
            LEFT JOIN silver_order_items i
                ON o.order_id = i.order_id
            WHERE i.order_id IS NULL
            GROUP BY o.order_status
            ORDER BY quantidade DESC
        """

        print("\n3. PEDIDOS SEM ITENS")

        for status, quantidade in cursor.execute(query_missing):
            print(f"{status}: {quantidade:,}")

        print("\n" + "=" * 75)


if __name__ == "__main__":
    main()
