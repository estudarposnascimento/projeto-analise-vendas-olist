
import sqlite3

from projeto.config import DATABASE_PATH


TABLES = [
    "gold_vendas_mensais",
    "gold_vendas_categorias",
    "gold_top_produtos",
]


def main():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        print("=" * 60)
        print("VALIDAÇÃO DOS INDICADORES GOLD")
        print("=" * 60)

        for table in TABLES:
            total = cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {total:,} registros")

        print("\nRESUMO DAS VENDAS ENTREGUES")

        query = """
            SELECT
                COUNT(DISTINCT order_id),
                COUNT(*),
                ROUND(SUM(price), 2),
                ROUND(SUM(freight_value), 2),
                ROUND(
                    SUM(price) / COUNT(DISTINCT order_id),
                    2
                )
            FROM gold_vendas
            WHERE order_status = 'delivered'
        """

        pedidos, itens, produtos, frete, ticket = (
            cursor.execute(query).fetchone()
        )

        print(f"Pedidos entregues: {pedidos:,}")
        print(f"Itens entregues: {itens:,}")
        print(f"Valor dos produtos: R$ {produtos:,.2f}")
        print(f"Valor do frete: R$ {frete:,.2f}")
        print(f"Ticket médio: R$ {ticket:,.2f}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
