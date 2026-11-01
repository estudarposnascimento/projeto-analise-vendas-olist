
import sqlite3

from projeto.config import DATABASE_PATH


def main():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        print("=" * 70)
        print("ANÁLISE DOS RESULTADOS GOLD")
        print("=" * 70)

        # 1. Vendas mensais
        print("\n1. DESEMPENHO MENSAL")

        query_mensal = """
            SELECT
                ano_mes,
                quantidade_pedidos,
                quantidade_itens,
                valor_produtos,
                ticket_medio
            FROM gold_vendas_mensais
            ORDER BY ano_mes
        """

        for row in cursor.execute(query_mensal):
            print(
                f"{row[0]} | Pedidos: {row[1]:,} | "
                f"Itens: {row[2]:,} | "
                f"Vendas: R$ {row[3]:,.2f} | "
                f"Ticket: R$ {row[4]:,.2f}"
            )

        # 2. Top 10 categorias
        print("\n2. TOP 10 CATEGORIAS")

        query_categorias = """
            SELECT
                categoria,
                quantidade_itens,
                valor_produtos
            FROM gold_vendas_categorias
            ORDER BY valor_produtos DESC
            LIMIT 10
        """

        for row in cursor.execute(query_categorias):
            print(
                f"{row[0]} | Itens: {row[1]:,} | "
                f"Vendas: R$ {row[2]:,.2f}"
            )

        # 3. Top 10 produtos
        print("\n3. TOP 10 PRODUTOS")

        query_produtos = """
            SELECT
                product_id,
                categoria,
                quantidade_itens,
                valor_produtos
            FROM gold_top_produtos
            ORDER BY quantidade_itens DESC, valor_produtos DESC
            LIMIT 10
        """

        for row in cursor.execute(query_produtos):
            print(
                f"Produto: {row[0]} | Categoria: {row[1]} | "
                f"Itens: {row[2]:,} | "
                f"Vendas: R$ {row[3]:,.2f}"
            )

        # 4. Reconciliação dos indicadores
        print("\n4. RECONCILIAÇÃO FINANCEIRA")

        query_reconciliacao = """
            SELECT
                (SELECT ROUND(SUM(valor_produtos), 2)
                 FROM gold_vendas_mensais),

                (SELECT ROUND(SUM(valor_produtos), 2)
                 FROM gold_vendas_categorias),

                (SELECT ROUND(SUM(valor_produtos), 2)
                 FROM gold_top_produtos)
        """

        mensal, categorias, produtos = cursor.execute(
            query_reconciliacao
        ).fetchone()

        print(f"Total mensal: R$ {mensal:,.2f}")
        print(f"Total categorias: R$ {categorias:,.2f}")
        print(f"Total produtos: R$ {produtos:,.2f}")

        print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
