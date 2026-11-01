
import sqlite3

import pandas as pd

from projeto.config import DATABASE_PATH


def main():
    with sqlite3.connect(DATABASE_PATH) as connection:
        produtos = pd.read_sql_query(
            """
            SELECT
                product_id,
                product_category_name
            FROM silver_products
            ORDER BY product_id
            """,
            connection,
        )

        # Categorias com nomes mais amigáveis
        produtos["categoria"] = (
            produtos["product_category_name"]
            .fillna("nao_informado")
            .str.replace("_", " ", regex=False)
            .str.title()
        )

        produtos["nome_exibicao"] = (
            produtos["categoria"]
            + " | Produto "
            + produtos["product_id"].str[:8]
        )

        produtos["tipo_nome"] = "categoria_id"

        dimensao = produtos[
            [
                "product_id",
                "nome_exibicao",
                "categoria",
                "tipo_nome",
            ]
        ]

        dimensao.to_sql(
            "dim_produtos",
            connection,
            if_exists="replace",
            index=False,
        )

        connection.execute(
            """
            CREATE UNIQUE INDEX idx_dim_produtos_id
            ON dim_produtos(product_id)
            """
        )

        print("=" * 60)
        print("DIMENSÃO DE PRODUTOS CRIADA")
        print("=" * 60)
        print(f"Produtos cadastrados: {len(dimensao):,}")
        print(
            "IDs duplicados:",
            dimensao["product_id"].duplicated().sum(),
        )
        print("\nExemplos:")

        print(
            dimensao[
                ["product_id", "nome_exibicao"]
            ].head(10).to_string(index=False)
        )


if __name__ == "__main__":
    main()
