
import sqlite3

from projeto.config import DATABASE_PATH


def main():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        print("=" * 55)
        print("VALIDAÇÃO DA CAMADA GOLD")
        print("=" * 55)

        # Quantidade de registros
        total = cursor.execute(
            "SELECT COUNT(*) FROM gold_vendas"
        ).fetchone()[0]

        print(f"\nTotal de registros: {total:,}")

        # Quantidade de pedidos
        pedidos = cursor.execute(
            "SELECT COUNT(DISTINCT order_id) FROM gold_vendas"
        ).fetchone()[0]

        print(f"Pedidos distintos: {pedidos:,}")

        # Quantidade de produtos
        produtos = cursor.execute(
            "SELECT COUNT(DISTINCT product_id) FROM gold_vendas"
        ).fetchone()[0]

        print(f"Produtos distintos: {produtos:,}")

        # Verificação de duplicidade da granularidade
        duplicados = cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT order_id, order_item_id
                FROM gold_vendas
                GROUP BY order_id, order_item_id
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]

        print(f"Itens duplicados: {duplicados}")

        # Verificação de valores nulos
        nulos = cursor.execute("""
            SELECT COUNT(*)
            FROM gold_vendas
            WHERE order_id IS NULL
               OR order_item_id IS NULL
               OR product_id IS NULL
               OR price IS NULL
               OR freight_value IS NULL
        """).fetchone()[0]

        print(f"Registros com campos essenciais nulos: {nulos}")

        # Resumo financeiro
        financeiro = cursor.execute("""
            SELECT
                ROUND(SUM(price), 2),
                ROUND(SUM(freight_value), 2),
                ROUND(SUM(total_item_value), 2)
            FROM gold_vendas
        """).fetchone()

        print("\nRESUMO FINANCEIRO")
        print(f"Total de produtos: R$ {financeiro[0]:,.2f}")
        print(f"Total de frete: R$ {financeiro[1]:,.2f}")
        print(f"Total com frete: R$ {financeiro[2]:,.2f}")

        print("\n" + "=" * 55)


if __name__ == "__main__":
    main()
